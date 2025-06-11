# Settings

import os
import shutil
import random
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv


class ChaffSettings:
    def __init__(self):
        load_dotenv()
        
        # Load settings from environment variables with defaults
        self.target_directory = os.getenv('TARGET_DIRECTORY', f'/home/{os.getenv("USER", "user")}/.chaff')
        self.delete_after_completion = os.getenv('DELETE_AFTER_COMPLETION', 'false').lower() == 'true'
        self.fill_drive = os.getenv('FILL_DRIVE', 'false').lower() == 'true'
        
        # File size settings (convert to bytes)
        self.min_file_size = self._parse_size(os.getenv('MIN_FILE_SIZE', '0.1MB'))
        self.max_file_size = self._parse_size(os.getenv('MAX_FILE_SIZE', '10MB'))
        
        # Minimum remaining disk space (convert to bytes)
        self.minimum_remaining_disk_space = self._parse_size(os.getenv('MINIMUM_REMAINING_DISK_SPACE', '100MB'))
        
        # File count settings
        self.min_file_count = int(os.getenv('MIN_FILE_COUNT', '100'))
        self.max_file_count = int(os.getenv('MAX_FILE_COUNT', '10000'))
        
        # File types
        self.chaff_file_types = self._parse_list(os.getenv('CHAFF_FILE_TYPES', 'txt,jpg,eml,pdf,docx,xlsx,csv'))
        
        # Auto-detect languages from data directory
        self.include_languages = self._detect_available_languages()
        
        # Ensure target directory exists
        Path(self.target_directory).mkdir(parents=True, exist_ok=True)
    
    def _parse_size(self, size_str: str) -> int:
        """Convert size string (e.g., '1MB', '500KB', '0.1MB') to bytes"""
        size_str = size_str.upper().strip()
        
        if size_str.endswith('KB'):
            return int(float(size_str[:-2]) * 1024)
        elif size_str.endswith('MB'):
            return int(float(size_str[:-2]) * 1024 * 1024)
        elif size_str.endswith('GB'):
            return int(float(size_str[:-2]) * 1024 * 1024 * 1024)
        else:
            # Assume bytes if no unit specified
            return int(float(size_str))
    
    def _parse_list(self, list_str: str) -> List[str]:
        """Parse comma-separated string into list"""
        return [item.strip() for item in list_str.split(',') if item.strip()]
    
    def _detect_available_languages(self) -> List[str]:
        """Detect available languages from data files"""
        try:
            from phrase_generator import PhraseGenerator
            pg = PhraseGenerator()
            if pg.available_languages:
                return pg.available_languages
        except ImportError:
            pass
        
        # Fallback to default languages
        return ['en']
    
    def get_available_disk_space(self, path: str = None) -> int:
        """Get available disk space in bytes for the target directory"""
        if path is None:
            path = self.target_directory
        
        try:
            _, _, free = shutil.disk_usage(path)
            return free
        except Exception as e:
            print(f"Error getting disk space for {path}: {e}")
            return 0
    
    def format_size(self, size_bytes: int) -> str:
        """Format bytes into human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def validate_settings(self) -> List[str]:
        """Validate settings and return list of warnings/errors"""
        warnings = []
        
        if self.min_file_size >= self.max_file_size:
            warnings.append("Minimum file size must be less than maximum file size")
        
        if self.min_file_count >= self.max_file_count:
            warnings.append("Minimum file count must be less than maximum file count")
        
        available_space = self.get_available_disk_space()
        usable_space = available_space - self.minimum_remaining_disk_space
        estimated_min_space = self.min_file_count * self.min_file_size
        
        if usable_space < estimated_min_space:
            warnings.append(f"Not enough usable disk space. Available: {self.format_size(available_space)}, "
                          f"Reserved: {self.format_size(self.minimum_remaining_disk_space)}, "
                          f"Usable: {self.format_size(max(0, usable_space))}, "
                          f"Minimum needed: {self.format_size(estimated_min_space)}")
        
        if not os.path.exists(self.target_directory):
            warnings.append(f"Target directory does not exist: {self.target_directory}")
        
        return warnings
    
    def print_settings(self):
        """Print current settings for debugging"""
        print("Chaff Generator Settings:")
        print(f"  Target Directory: {self.target_directory}")
        print(f"  Delete After Completion: {self.delete_after_completion}")
        print(f"  Fill Drive: {self.fill_drive}")
        print(f"  File Size Range: {self.format_size(self.min_file_size)} - {self.format_size(self.max_file_size)}")
        print(f"  File Count Range: {self.min_file_count} - {self.max_file_count}")
        print(f"  File Types: {', '.join(self.chaff_file_types)}")
        print(f"  Languages: {', '.join(self.include_languages)}")
        print(f"  Available Disk Space: {self.format_size(self.get_available_disk_space())}")
        print(f"  Minimum Remaining Space: {self.format_size(self.minimum_remaining_disk_space)}")
        
        warnings = self.validate_settings()
        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  - {warning}")


@dataclass
class FileGenerationPlan:
    """Represents a plan for generating a single file"""
    file_type: str
    size_bytes: int
    language: str
    filename: str


class ChaffGenerationPlanner:
    """Plans the generation of chaff files based on settings and constraints"""
    
    def __init__(self, settings: ChaffSettings):
        self.settings = settings
    
    def calculate_fill_drive_parameters(self) -> Tuple[int, int]:
        """Calculate file count and average size when fill_drive is enabled"""
        available_space = self.settings.get_available_disk_space()
        
        # Reserve minimum remaining disk space as specified by user
        usable_space = available_space - self.settings.minimum_remaining_disk_space
        
        if usable_space <= 0:
            return 0, 0
        
        # Calculate optimal file count within constraints
        # Try to use average file size between min and max
        avg_target_size = (self.settings.min_file_size + self.settings.max_file_size) // 2
        estimated_file_count = usable_space // avg_target_size
        
        # Ensure file count is within user-defined bounds
        file_count = max(self.settings.min_file_count, 
                        min(estimated_file_count, self.settings.max_file_count))
        
        # Recalculate average size based on actual file count
        if file_count > 0:
            avg_file_size = usable_space // file_count
            # Ensure average size is within bounds
            avg_file_size = max(self.settings.min_file_size,
                              min(avg_file_size, self.settings.max_file_size))
        else:
            avg_file_size = self.settings.min_file_size
        
        return file_count, avg_file_size
    
    def generate_file_plan(self) -> List[FileGenerationPlan]:
        """Generate a complete plan for all files to be created"""
        if self.settings.fill_drive:
            file_count, avg_size = self.calculate_fill_drive_parameters()
            if file_count == 0:
                return []
        else:
            # Use random count within user-defined range
            file_count = random.randint(self.settings.min_file_count, 
                                      self.settings.max_file_count)
            avg_size = (self.settings.min_file_size + self.settings.max_file_size) // 2
        
        plans = []
        total_allocated_size = 0
        target_total_size = file_count * avg_size if self.settings.fill_drive else None
        
        for i in range(file_count):
            # Randomly select file type and language
            file_type = random.choice(self.settings.chaff_file_types)
            language = random.choice(self.settings.include_languages)
            
            # Calculate file size
            if self.settings.fill_drive and target_total_size:
                # For fill_drive mode, distribute remaining space among remaining files
                remaining_files = file_count - i
                remaining_space = target_total_size - total_allocated_size
                
                if remaining_files > 1:
                    # Randomly vary size but ensure we can fit remaining files
                    max_for_this_file = min(
                        self.settings.max_file_size,
                        remaining_space - (remaining_files - 1) * self.settings.min_file_size
                    )
                    min_for_this_file = max(
                        self.settings.min_file_size,
                        remaining_space - (remaining_files - 1) * self.settings.max_file_size
                    )
                    
                    if max_for_this_file >= min_for_this_file:
                        file_size = random.randint(min_for_this_file, max_for_this_file)
                    else:
                        file_size = self.settings.min_file_size
                else:
                    # Last file gets remaining space
                    file_size = max(self.settings.min_file_size, 
                                  min(remaining_space, self.settings.max_file_size))
            else:
                # Normal mode: random size within bounds
                file_size = random.randint(self.settings.min_file_size, 
                                         self.settings.max_file_size)
            
            # Generate unique filename
            filename = self._generate_filename(file_type, language, i)
            
            plans.append(FileGenerationPlan(
                file_type=file_type,
                size_bytes=file_size,
                language=language,
                filename=filename
            ))
            
            total_allocated_size += file_size
        
        return plans
    
    def _generate_filename(self, file_type: str, language: str, index: int) -> str:
        """Generate a realistic filename for the given file type and language"""
        # Base names by language
        base_names = {
            'en': ['document', 'report', 'data', 'file', 'backup', 'archive', 'temp'],
            'es': ['documento', 'informe', 'datos', 'archivo', 'respaldo', 'temporal'],
            'fr': ['document', 'rapport', 'donnees', 'fichier', 'sauvegarde', 'temporaire'],
            'de': ['dokument', 'bericht', 'daten', 'datei', 'sicherung', 'temporaer'],
            'cn': ['wenjian', 'baogao', 'shuju', 'beifen', 'linshi'],
            'jp': ['bunso', 'hokoku', 'deeta', 'bakkuappu', 'ichiji'],
            'ru': ['dokument', 'otchet', 'dannye', 'fajl', 'rezerv', 'vremennyj']
        }
        
        base_name = random.choice(base_names.get(language, base_names['en']))
        
        # Add some variation
        suffixes = ['', '_copy', '_backup', '_final', '_draft', '_v2', '_old']
        suffix = random.choice(suffixes)
        
        # Add timestamp-like numbers sometimes
        if random.random() < 0.3:
            timestamp = random.randint(20200101, 20241231)
            base_name += f'_{timestamp}'
        
        return f"{base_name}{suffix}.{file_type}"
    
    def get_generation_summary(self, plans: List[FileGenerationPlan]) -> Dict:
        """Get summary statistics for the generation plan"""
        if not plans:
            return {'total_files': 0, 'total_size': 0, 'file_types': {}, 'languages': {}}
        
        total_size = sum(plan.size_bytes for plan in plans)
        
        file_types = {}
        languages = {}
        
        for plan in plans:
            file_types[plan.file_type] = file_types.get(plan.file_type, 0) + 1
            languages[plan.language] = languages.get(plan.language, 0) + 1
        
        return {
            'total_files': len(plans),
            'total_size': total_size,
            'total_size_formatted': self.settings.format_size(total_size),
            'file_types': file_types,
            'languages': languages,
            'average_file_size': total_size // len(plans),
            'average_file_size_formatted': self.settings.format_size(total_size // len(plans))
        }


# Create a default settings instance
settings = ChaffSettings()
