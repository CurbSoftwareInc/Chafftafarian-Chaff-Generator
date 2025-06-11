#!/usr/bin/env python3
"""
Chafftafarian Chaff Generator

Generates realistic-looking fake files (chaff) for security purposes.
Creates various file types including emails with attachments, documents, 
and images that are cross-referenced and encoded to appear as legitimate data.
"""

import argparse
import os
import sys
import time
import random
from pathlib import Path
from typing import List
from datetime import datetime, timedelta

from settings import ChaffSettings, ChaffGenerationPlanner, FileGenerationPlan
from templates import TemplateFactory
from file_linking import FileLinkingManager


def get_actual_filename(encoded_file) -> str:
    """Get the actual filename that will be used for an encoded file"""
    original_filename = encoded_file.original_plan.filename
    
    # Always keep original filename to avoid application confusion
    # All files should be openable in their native applications
    return original_filename


def create_linked_file(encoded_file, target_dir: Path) -> bool:
    """Create a file from an encoded file object"""
    try:
        modified_filename = get_actual_filename(encoded_file)
        file_path = target_dir / modified_filename
        
        # Ensure we don't overwrite existing files
        counter = 1
        base_modified_filename = modified_filename
        while file_path.exists():
            name_parts = base_modified_filename.rsplit('.', 1)
            if len(name_parts) == 2:
                new_filename = f"{name_parts[0]}_{counter}.{name_parts[1]}"
            else:
                new_filename = f"{base_modified_filename}_{counter}"
            file_path = target_dir / new_filename
            counter += 1
        
        # Write the encoded content
        with open(file_path, 'wb') as f:
            f.write(encoded_file.encoded_content)
        
        return True
        
    except Exception as e:
        print(f"Error creating file {encoded_file.original_plan.filename}: {e}")
        return False


def generate_file_content(plan: FileGenerationPlan) -> bytes:
    """Generate appropriate content for the file type and language"""
    
    # Sample content templates by language
    content_templates = {
        'en': {
            'txt': "This is a sample document containing important information about project data and analysis results.",
            'eml': """From: sender@example.com
To: recipient@company.com
Subject: Important Document
Date: Mon, 15 Jan 2024 10:30:00 +0000

Dear Colleague,

Please find the attached documents for your review.

Best regards,
John Smith""",
            'csv': "ID,Name,Date,Amount,Status\n1,John Doe,2024-01-15,1250.50,Active\n2,Jane Smith,2024-01-14,890.25,Pending",
        },
        'es': {
            'txt': "Este es un documento de muestra que contiene informaci�n importante sobre datos del proyecto y resultados de an�lisis.",
            'eml': """From: remitente@ejemplo.com
To: destinatario@empresa.com
Subject: Documento Importante
Date: Mon, 15 Jan 2024 10:30:00 +0000

Estimado Colega,

Por favor encuentre los documentos adjuntos para su revisi�n.

Saludos cordiales,
Juan P�rez""",
        },
        'fr': {
            'txt': "Ceci est un document d'exemple contenant des informations importantes sur les donn�es de projet et les r�sultats d'analyse.",
        },
        'de': {
            'txt': "Dies ist ein Beispieldokument mit wichtigen Informationen �ber Projektdaten und Analyseergebnisse.",
        }
    }
    
    # Get base content for the language and file type
    lang_content = content_templates.get(plan.language, content_templates['en'])
    base_content = lang_content.get(plan.file_type, lang_content.get('txt', 'Sample content'))
    
    # Special handling for different file types
    if plan.file_type == 'jpg':
        # Create a simple binary pattern for JPG files
        return create_dummy_image_content(plan.size_bytes)
    elif plan.file_type in ['pdf', 'docx', 'xlsx']:
        # For complex formats, create text content with format markers
        base_content = f"[{plan.file_type.upper()} Document]\n{base_content}\n[End of Document]"
    
    # Repeat and pad content to reach target size
    content_bytes = base_content.encode('utf-8')
    
    if len(content_bytes) < plan.size_bytes:
        # Repeat content to fill size
        repetitions = (plan.size_bytes // len(content_bytes)) + 1
        content_bytes = (content_bytes * repetitions)[:plan.size_bytes]
    else:
        # Truncate if too long
        content_bytes = content_bytes[:plan.size_bytes]
    
    return content_bytes


def create_dummy_image_content(size_bytes: int) -> bytes:
    """Create dummy binary content for image files"""
    # Simple pattern that looks like binary data
    pattern = bytes([random.randint(0, 255) for _ in range(min(1024, size_bytes))])
    
    if size_bytes <= len(pattern):
        return pattern[:size_bytes]
    
    # Repeat pattern to fill size
    repetitions = (size_bytes // len(pattern)) + 1
    return (pattern * repetitions)[:size_bytes]


def adjust_file_size(file_path: Path, target_size: int, file_type: str):
    """Adjust file size to match target by padding or truncating"""
    try:
        current_size = file_path.stat().st_size
        
        if current_size < target_size:
            # Pad the file
            padding_size = target_size - current_size
            if file_type == 'jpg':
                padding = bytes([0] * padding_size)
                with open(file_path, 'ab') as f:
                    f.write(padding)
            else:
                padding = '\n' + ' ' * (padding_size - 1)
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(padding)
        elif current_size > target_size:
            # Truncate the file
            with open(file_path, 'r+b') as f:
                f.truncate(target_size)
                
    except Exception as e:
        print(f"Warning: Could not adjust file size for {file_path}: {e}")


def generate_chaff_files(settings: ChaffSettings, plans: List[FileGenerationPlan]) -> tuple[int, list]:
    """Generate all chaff files with linking and encoding"""
    target_dir = Path(settings.target_directory)
    
    print(f"Creating file network with {len(plans)} chaff files in {target_dir}")
    print("Building cross-references and encoding files...")
    
    # Create file linking manager and generate network
    linking_manager = FileLinkingManager()
    encoded_files = linking_manager.create_file_network(plans)
    
    # Show encoding summary
    encoding_summary = linking_manager.get_encoding_summary()
    print("\\nEncoding methods used:")
    for method, count in encoding_summary.items():
        print(f"  {method}: {count} files")
    
    # Show cross-reference summary
    total_refs = len(linking_manager.file_references)
    password_refs = len([r for r in linking_manager.file_references if r.reference_type == "password"])
    attachment_refs = len([r for r in linking_manager.file_references if r.reference_type == "attachment"])
    
    print(f"\\nCross-references created: {total_refs}")
    print(f"  Email attachments: {attachment_refs}")
    print(f"  Password references: {password_refs}")
    print(f"  Other references: {total_refs - password_refs - attachment_refs}")
    
    print(f"\\nWriting {len(encoded_files)} encoded files...")
    
    success_count = 0
    for i, encoded_file in enumerate(encoded_files, 1):
        file_info = f"{encoded_file.original_plan.filename}"
        if encoded_file.encoding_method.value != "none":
            file_info += f" ({encoded_file.encoding_method.value})"
        if encoded_file.password:
            file_info += " [password protected]"
        
        print(f"Creating file {i}/{len(encoded_files)}: {file_info}")
        
        if create_linked_file(encoded_file, target_dir):
            success_count += 1
        
        # Show progress
        if i % 10 == 0 or i == len(encoded_files):
            progress = (i / len(encoded_files)) * 100
            print(f"Progress: {progress:.1f}% ({i}/{len(encoded_files)} files)")
    
    # Show passwords and keys summary
    if linking_manager.passwords:
        print(f"\\nPassword-protected files: {len(linking_manager.passwords)}")
        print("Note: Passwords are distributed throughout other files as references")
    
    return success_count, encoded_files


def randomize_file_metadata(settings: ChaffSettings, encoded_files):
    """Randomize file system metadata (timestamps) for all generated files"""
    print("Randomizing file metadata (timestamps)...")
    target_dir = Path(settings.target_directory)
    randomized_count = 0
    
    # Define realistic time ranges for different file types
    now = datetime.now()
    
    # Create different time ranges for more realistic distribution
    time_ranges = {
        'recent': (now - timedelta(days=30), now - timedelta(days=1)),      # Last month
        'medium': (now - timedelta(days=365), now - timedelta(days=30)),    # Last year
        'old': (now - timedelta(days=365*3), now - timedelta(days=365)),    # 1-3 years ago
        'archive': (now - timedelta(days=365*10), now - timedelta(days=365*3))  # 3-10 years ago
    }
    
    for encoded_file in encoded_files:
        try:
            modified_filename = get_actual_filename(encoded_file)
            file_path = target_dir / modified_filename
            if not file_path.exists():
                continue
                
            # Choose time range based on file type and random distribution
            file_type = encoded_file.original_plan.file_type
            
            # Different file types get different age distributions
            if file_type == 'eml':
                # Emails tend to be more recent
                range_weights = [0.4, 0.3, 0.2, 0.1]  # recent, medium, old, archive
            elif file_type in ['pdf', 'docx']:
                # Documents have mixed ages
                range_weights = [0.2, 0.4, 0.3, 0.1]
            elif file_type in ['xlsx', 'csv']:
                # Data files tend to be older
                range_weights = [0.1, 0.3, 0.4, 0.2]
            elif file_type in ['jpg', 'png']:
                # Images can be quite old
                range_weights = [0.15, 0.25, 0.35, 0.25]
            else:
                # Default distribution
                range_weights = [0.25, 0.35, 0.25, 0.15]
            
            # Select time range
            range_keys = list(time_ranges.keys())
            selected_range = random.choices(range_keys, weights=range_weights)[0]
            start_time, end_time = time_ranges[selected_range]
            
            # Generate random timestamps within the selected range
            time_span = (end_time - start_time).total_seconds()
            
            # Creation time (oldest)
            creation_offset = random.uniform(0, time_span * 0.8)
            creation_time = start_time + timedelta(seconds=creation_offset)
            
            # Modification time (between creation and end)
            remaining_span = (end_time - creation_time).total_seconds()
            if remaining_span > 0:
                mod_offset = random.uniform(0, remaining_span)
                modification_time = creation_time + timedelta(seconds=mod_offset)
            else:
                modification_time = creation_time
            
            # Access time (between modification and end, or recent)
            if random.random() < 0.7:  # 70% chance of recent access
                # Recent access
                recent_start = max(modification_time, now - timedelta(days=90))
                recent_span = (now - recent_start).total_seconds()
                if recent_span > 0:
                    access_offset = random.uniform(0, recent_span)
                    access_time = recent_start + timedelta(seconds=access_offset)
                else:
                    access_time = modification_time
            else:
                # Access time close to modification time
                access_span = (end_time - modification_time).total_seconds()
                if access_span > 0:
                    access_offset = random.uniform(0, access_span * 0.5)
                    access_time = modification_time + timedelta(seconds=access_offset)
                else:
                    access_time = modification_time
            
            # Convert to timestamps
            creation_timestamp = creation_time.timestamp()
            modification_timestamp = modification_time.timestamp()
            access_timestamp = access_time.timestamp()
            
            # Apply the timestamps to the file
            # Note: On Windows, creation time can be set via os.utime with specific parameters
            # On Unix-like systems, we can only set modification and access times
            try:
                # Set modification and access times
                os.utime(file_path, (access_timestamp, modification_timestamp))
                
                # Try to set creation time on Windows
                if os.name == 'nt':
                    try:
                        import win32file
                        import win32con
                        from pywintypes import Time
                        
                        # Open file handle
                        handle = win32file.CreateFile(
                            str(file_path),
                            win32con.GENERIC_WRITE,
                            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
                            None,
                            win32con.OPEN_EXISTING,
                            0,
                            None
                        )
                        
                        # Set creation time
                        win32file.SetFileTime(handle, Time(creation_timestamp), None, None)
                        win32file.CloseHandle(handle)
                        
                    except ImportError:
                        # win32file not available, skip creation time setting
                        pass
                    except Exception as e:
                        # Failed to set creation time, but that's okay
                        pass
                
                randomized_count += 1
                
            except Exception as e:
                print(f"Warning: Could not set timestamps for {encoded_file.original_plan.filename}: {e}")
                
        except Exception as e:
            print(f"Warning: Could not process metadata for {encoded_file.original_plan.filename}: {e}")
    
    print(f"Randomized metadata for {randomized_count}/{len(encoded_files)} files")
    
    # Show some examples of the randomized timestamps
    if randomized_count > 0:
        print("\nSample of randomized timestamps:")
        sample_files = random.sample(encoded_files, min(3, len(encoded_files)))
        for encoded_file in sample_files:
            modified_filename = get_actual_filename(encoded_file)
            file_path = target_dir / modified_filename
            if file_path.exists():
                stat = file_path.stat()
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                access_time = datetime.fromtimestamp(stat.st_atime)
                print(f"  {modified_filename}:")
                print(f"    Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"    Accessed: {access_time.strftime('%Y-%m-%d %H:%M:%S')}")


def cleanup_files(settings: ChaffSettings, encoded_files):
    """Delete generated files if delete_after_completion is enabled"""
    if not settings.delete_after_completion:
        return
    
    print("Cleaning up generated files...")
    target_dir = Path(settings.target_directory)
    deleted_count = 0
    
    for encoded_file in encoded_files:
        try:
            modified_filename = get_actual_filename(encoded_file)
            file_path = target_dir / modified_filename
            if file_path.exists():
                file_path.unlink()
                deleted_count += 1
        except Exception as e:
            print(f"Warning: Could not delete {modified_filename}: {e}")
    
    print(f"Deleted {deleted_count} files")


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="Chafftafarian Chaff Generator - Create realistic fake files for security purposes"
    )
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be generated without creating files'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed output'
    )
    parser.add_argument(
        '--config',
        help='Path to .env configuration file (default: .env)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load settings
        if args.config:
            os.environ['DOTENV_PATH'] = args.config
        
        settings = ChaffSettings()
        
        if args.verbose:
            settings.print_settings()
        
        # Validate settings
        warnings = settings.validate_settings()
        if warnings:
            print("Configuration warnings:")
            for warning in warnings:
                print(f"  - {warning}")
            
            if any("not enough" in warning.lower() for warning in warnings):
                print("Aborting due to insufficient disk space.")
                return 1
        
        # Create generation plan
        planner = ChaffGenerationPlanner(settings)
        plans = planner.generate_file_plan()
        
        if not plans:
            print("No files to generate (insufficient disk space or invalid configuration)")
            return 1
        
        # Show generation summary
        summary = planner.get_generation_summary(plans)
        print(f"\nGeneration Plan Summary:")
        print(f"  Total Files: {summary['total_files']}")
        print(f"  Total Size: {summary['total_size_formatted']}")
        print(f"  Average File Size: {summary['average_file_size_formatted']}")
        print(f"  File Types: {dict(summary['file_types'])}")
        print(f"  Languages: {dict(summary['languages'])}")
        
        if args.dry_run:
            print("\n[DRY RUN] Files that would be generated:")
            for i, plan in enumerate(plans[:10], 1):  # Show first 10
                print(f"  {i}. {plan.filename} ({settings.format_size(plan.size_bytes)}, {plan.language})")
            if len(plans) > 10:
                print(f"  ... and {len(plans) - 10} more files")
            return 0
        
        # Confirm generation
        print(f"\nTarget directory: {settings.target_directory}")
        available_space = settings.get_available_disk_space()
        print(f"Available disk space: {settings.format_size(available_space)}")
        
        response = input("\nProceed with generation? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Generation cancelled")
            return 0
        
        # Generate files
        start_time = time.time()
        success_count, encoded_files = generate_chaff_files(settings, plans)
        generation_time = time.time() - start_time
        
        print(f"\nGeneration complete!")
        print(f"  Successfully created: {success_count}/{len(plans)} files")
        print(f"  Time taken: {generation_time:.2f} seconds")
        print(f"  Average speed: {success_count/generation_time:.1f} files/second")
        
        # Note about the chaff network
        print(f"\nChaff network features:")
        print(f"  - Files are cross-referenced and linked")
        print(f"  - Multiple encoding methods used (base64, encryption, compression)")
        print(f"  - Passwords distributed throughout files")
        print(f"  - Email attachments simulated")
        print(f"  - Realistic business content generated")
        
        # CRITICAL: Randomize file metadata before cleanup or termination
        print(f"\nRandomizing file metadata...")
        randomize_file_metadata(settings, encoded_files)
        
        # Cleanup if requested
        if settings.delete_after_completion:
            print(f"\nWaiting 5 seconds before cleanup...")
            time.sleep(5)
            cleanup_files(settings, encoded_files)
        
        return 0
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())