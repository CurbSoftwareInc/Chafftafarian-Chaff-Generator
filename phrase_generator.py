"""
Phrase generator utility that uses vocabulary files and templates to create
realistic text content for chaff files.
"""

import os
import random
import csv
from typing import Dict, List, Optional
from pathlib import Path


class PhraseGenerator:
    """Generate realistic phrases using vocabulary files and templates"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.vocabularies: Dict[str, List[str]] = {}
        self.queries: List[str] = []
        self.sentences: List[str] = []
        self.story_sentences: List[str] = []
        self.addresses: List[Dict[str, str]] = []
        self.cities: List[Dict[str, str]] = []
        self.states: List[Dict[str, str]] = []
        self.street_names: List[str] = []
        self.first_names: List[str] = []
        self.last_names: List[str] = []
        self.available_languages: List[str] = []
        
        self._auto_detect_data_files()
        self._load_vocabularies()
        self._load_queries()
        self._load_sentences()
        self._load_addresses()
        self._load_cities_and_states()
        self._load_street_names()
        self._load_name_lists()
        self._detect_available_languages()
    
    def _auto_detect_data_files(self):
        """Auto-detect available data files in the data directory"""
        self.detected_files = {
            'vocab': [],
            'txt': [],
            'csv': [],
            'first_names': [],
            'last_names': []
        }
        
        if not self.data_dir.exists():
            return
        
        for file_path in self.data_dir.glob('*'):
            if file_path.is_file():
                name = file_path.name.lower()
                if name.endswith('.vocab'):
                    self.detected_files['vocab'].append(file_path)
                elif name.endswith('.txt'):
                    self.detected_files['txt'].append(file_path)
                elif name.endswith('.csv'):
                    self.detected_files['csv'].append(file_path)
                elif 'first' in name and not name.endswith('.csv'):
                    self.detected_files['first_names'].append(file_path)
                elif 'last' in name and not name.endswith('.csv'):
                    self.detected_files['last_names'].append(file_path)
    
    def _load_vocabularies(self):
        """Load all vocabulary files"""
        for vocab_path in self.detected_files['vocab']:
            vocab_name = vocab_path.stem.replace('-', '_').lower()
            self.vocabularies[vocab_name] = self._read_lines(vocab_path)
    
    def _load_queries(self):
        """Load query templates from detected txt files"""
        for txt_path in self.detected_files['txt']:
            if 'queries' in txt_path.name.lower():
                self.queries.extend(self._read_lines(txt_path))
    
    def _load_sentences(self):
        """Load sentence templates from detected txt files"""
        for txt_path in self.detected_files['txt']:
            name = txt_path.name.lower()
            if 'sentence' in name and 'story' not in name:
                self.sentences.extend(self._read_lines(txt_path))
            elif 'story' in name and 'sentence' in name:
                self.story_sentences.extend(self._read_lines(txt_path))
    
    def _load_name_lists(self):
        """Load first and last name lists"""
        for first_path in self.detected_files['first_names']:
            self.first_names.extend(self._read_lines(first_path))
        
        for last_path in self.detected_files['last_names']:
            self.last_names.extend(self._read_lines(last_path))
    
    def _detect_available_languages(self):
        """Detect available languages from file patterns"""
        languages = set()
        
        # Check for language-specific patterns in filenames
        language_patterns = {
            'en': ['english', 'en_', '_en'],
            'es': ['spanish', 'es_', '_es', 'espanol'],
            'fr': ['french', 'fr_', '_fr', 'francais'],
            'de': ['german', 'de_', '_de', 'deutsch'],
            'it': ['italian', 'it_', '_it', 'italiano'],
            'pt': ['portuguese', 'pt_', '_pt'],
            'ru': ['russian', 'ru_', '_ru'],
            'zh': ['chinese', 'zh_', '_zh', 'cn_', '_cn'],
            'ja': ['japanese', 'ja_', '_ja', 'jp_', '_jp'],
            'ko': ['korean', 'ko_', '_ko']
        }
        
        all_files = list(self.data_dir.glob('*'))
        for file_path in all_files:
            filename = file_path.name.lower()
            for lang_code, patterns in language_patterns.items():
                if any(pattern in filename for pattern in patterns):
                    languages.add(lang_code)
        
        # Default to English if no specific languages detected
        if not languages:
            languages.add('en')
        
        self.available_languages = sorted(list(languages))
    
    def _load_addresses(self):
        """Load address data from detected CSV files"""
        for csv_path in self.detected_files['csv']:
            name = csv_path.name.lower()
            if 'address' in name:
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        self.addresses.extend(list(reader))
                except Exception:
                    pass
    
    def _load_cities_and_states(self):
        """Load cities and states data from detected CSV files"""
        for csv_path in self.detected_files['csv']:
            name = csv_path.name.lower()
            if 'cities' in name or 'city' in name:
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        self.cities.extend(list(reader))
                except Exception:
                    pass
            elif 'states' in name or 'state' in name:
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        self.states.extend(list(reader))
                except Exception:
                    pass
    
    def _load_street_names(self):
        """Load street names from detected CSV files"""
        for csv_path in self.detected_files['csv']:
            name = csv_path.name.lower()
            if 'street' in name:
                try:
                    with open(csv_path, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        self.street_names.extend([row[0] for row in reader if row])
                except Exception:
                    pass
    
    def _read_lines(self, file_path: Path) -> List[str]:
        """Read lines from a text file, filtering empty lines"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception:
            return []
    
    def get_random_from_vocab(self, vocab_name: str) -> str:
        """Get random item from vocabulary"""
        vocab = self.vocabularies.get(vocab_name, [])
        return random.choice(vocab) if vocab else f"[{vocab_name}]"
    
    def get_random_address(self) -> str:
        """Generate random address"""
        if self.addresses:
            addr = random.choice(self.addresses)
            return f"{addr.get('address', '')}, {addr.get('city', '')}, {addr.get('state', '')}"
        elif self.street_names and self.cities and self.states:
            street = random.choice(self.street_names)
            number = random.randint(100, 9999)
            city_data = random.choice(self.cities)
            state_data = random.choice(self.states)
            return f"{number} {street}, {city_data.get('city', '')}, {state_data.get('state', '')}"
        else:
            return "123 Main St, Anytown, CA"
    
    def get_random_city(self) -> str:
        """Get random city"""
        if self.cities:
            city_data = random.choice(self.cities)
            return city_data.get('city', 'San Francisco')
        return 'San Francisco'
    
    def get_random_state(self) -> str:
        """Get random state"""
        if self.states:
            state_data = random.choice(self.states)
            return state_data.get('state', 'California')
        return 'California'
    
    def expand_template(self, template: str) -> str:
        """Expand a template string by replacing @PLACEHOLDER tokens"""
        result = template
        
        # Define mapping from template placeholders to vocab keys
        placeholder_map = {
            '@DAY-OF-WEEK': 'day_of_week',
            '@PERSON-FAMOUS': 'person_famous',
            '@PERSON-FIRSTNAME': 'person_famous',  # Use famous names as first names
            '@PERSON-LASTNAME': 'person_famous',   # Use famous names as last names
            '@RESTAURANT-FOOD': 'restaurant_food',
            '@RESTAURANT-NAME': 'restaurant_name',
            '@RESTAURANT-TYPE': 'restaurant_type',
            '@RETAILER': 'retailer',
            '@WEBSITE': 'website',
            '@CITY': None,  # Special handling
            '@ADDRESS': None,  # Special handling
            '@STATE': None   # Special handling
        }
        
        # Replace placeholders
        for placeholder, vocab_key in placeholder_map.items():
            while placeholder in result:
                if placeholder == '@CITY':
                    replacement = self.get_random_city()
                elif placeholder == '@ADDRESS':
                    replacement = self.get_random_address()
                elif placeholder == '@STATE':
                    replacement = self.get_random_state()
                elif vocab_key:
                    replacement = self.get_random_from_vocab(vocab_key)
                else:
                    replacement = placeholder  # Fallback
                
                result = result.replace(placeholder, replacement, 1)
        
        return result
    
    def generate_query(self) -> str:
        """Generate a realistic query/search string"""
        if self.queries:
            template = random.choice(self.queries)
            return self.expand_template(template)
        return "search query"
    
    def generate_sentence(self) -> str:
        """Generate a realistic sentence"""
        if self.sentences:
            template = random.choice(self.sentences)
            return self.expand_template(template)
        return "This is a sample sentence."
    
    def generate_story_sentence(self) -> str:
        """Generate a story-like sentence"""
        if self.story_sentences:
            template = random.choice(self.story_sentences)
            return self.expand_template(template)
        return "Once upon a time, there was a story."
    
    def generate_realistic_email_content(self) -> str:
        """Generate realistic email content using phrases"""
        parts = []
        
        # Subject variations
        subjects = [
            f"Meeting about {self.get_random_from_vocab('restaurant_food')}",
            f"Trip to {self.get_random_city()}",
            f"Dinner at {self.get_random_from_vocab('restaurant_name')}",
            f"Visit {self.get_random_from_vocab('retailer')}",
            f"Check out {self.get_random_from_vocab('website')}"
        ]
        
        # Generate sentences for email body
        for _ in range(random.randint(2, 5)):
            if random.random() < 0.3:
                parts.append(self.generate_query())
            elif random.random() < 0.5:
                parts.append(self.generate_sentence())
            else:
                parts.append(self.generate_story_sentence())
        
        return " ".join(parts)
    
    def generate_realistic_document_content(self, content_length: int = 500) -> str:
        """Generate realistic document content"""
        content_parts = []
        current_length = 0
        
        while current_length < content_length:
            if random.random() < 0.4:
                # Add query-style content
                sentence = self.generate_query()
            elif random.random() < 0.6:
                # Add regular sentences
                sentence = self.generate_sentence()
            else:
                # Add story sentences
                sentence = self.generate_story_sentence()
            
            content_parts.append(sentence)
            current_length += len(sentence)
            
            if current_length < content_length:
                content_parts.append("\n\n")
                current_length += 2
        
        result = "".join(content_parts)
        return result[:content_length] if len(result) > content_length else result
    
    def generate_realistic_name_data(self) -> Dict[str, str]:
        """Generate realistic name and contact data"""
        return {
            'name': self.get_random_from_vocab('person_famous'),
            'address': self.get_random_address(),
            'city': self.get_random_city(),
            'state': self.get_random_state(),
            'day': self.get_random_from_vocab('day_of_week'),
            'restaurant': self.get_random_from_vocab('restaurant_name'),
            'food': self.get_random_from_vocab('restaurant_food'),
            'retailer': self.get_random_from_vocab('retailer'),
            'website': self.get_random_from_vocab('website')
        }