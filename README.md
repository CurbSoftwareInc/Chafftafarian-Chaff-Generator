# Chafftafarian Chaff Generator

A sophisticated chaff file generator that creates realistic-looking files with randomized metadata, cross-references, and various encoding methods. Perfect for testing, security research, or creating decoy data.

## Features

- **Multiple File Types**: Generates PDFs, Word documents, Excel files, emails (EML), images (JPG/PNG), CSV files, and text files
- **Realistic Content**: Uses AI-powered content generation with customizable data sources
- **Cross-File References**: Creates interconnected files (emails reference attachments, documents embed images, etc.)
- **Multiple Encoding Methods**: Base64, encryption (Fernet), ZIP with passwords, and unencoded files
- **MIME Type Preservation**: Binary files (PDFs, images) maintain proper formats and are never corrupted by encoding
- **Metadata Randomization**: Randomizes file timestamps across realistic date ranges
- **RFC-822 Compliant Emails**: Generates proper EML files with headers and rich content
- **Customizable Data Sources**: Easily add your own vocabulary, sentences, and data files

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CurbSoftwareInc/Chafftafarian-Chaff-Generator.git
   cd Chafftafarian-Chaff-Generator
   ```

2. **Create and activate a Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
   
   *Note: On Ubuntu/Debian systems, you may need to install python3-venv first:*
   ```bash
   sudo apt install python3.12-venv
   ```

3. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure settings:**
   ```bash
   cp .env.example .env
   # Edit .env file with your desired settings
   ```

5. **Run the generator:**
   ```bash
   python main.py
   ```

6. **Deactivate virtual environment when done:**
   ```bash
   deactivate
   ```

## Configuration

### Available Settings (.env file)

| Setting | Default | Description |
|---------|---------|-------------|
| `TARGET_DIRECTORY` | `./chaff_output` | Directory where files will be generated |
| `DELETE_AFTER_COMPLETION` | `false` | Delete files after generation (for testing) |
| `FILL_DRIVE` | `false` | Continue generating until disk space limit |
| `MIN_REMAINING_DISK_SPACE_MB` | `100` | Minimum disk space to leave (MB) |
| `MIN_FILE_SIZE_BYTES` | `1024` | Minimum file size (1KB) |
| `MAX_FILE_SIZE_BYTES` | `10485760` | Maximum file size (10MB) |
| `MIN_FILE_COUNT` | `10` | Minimum number of files to generate |
| `MAX_FILE_COUNT` | `100` | Maximum number of files to generate |
| `CHAFF_FILE_TYPES` | `pdf,docx,xlsx,eml,csv,txt,jpg,png` | File types to generate |
| `INCLUDE_LANGUAGES` | `en,es,fr,de,cn,jp,ru` | Languages for content generation |

### Example .env Configuration

```env
TARGET_DIRECTORY=./my_chaff_files
DELETE_AFTER_COMPLETION=false
FILL_DRIVE=false
MIN_REMAINING_DISK_SPACE_MB=500
MIN_FILE_SIZE_BYTES=5120
MAX_FILE_SIZE_BYTES=52428800
MIN_FILE_COUNT=50
MAX_FILE_COUNT=200
CHAFF_FILE_TYPES=pdf,eml,jpg,png,docx
INCLUDE_LANGUAGES=en,es,fr
```

## How It Works

The generator creates interconnected files that mimic real-world data patterns:

1. **File Planning**: Generates a plan for files with realistic names and sizes
2. **Cross-Referencing**: Creates relationships between files (emails → attachments, documents → images)
3. **Content Generation**: Fills files with realistic content using templates and data sources
4. **Encoding**: Applies various encoding methods (base64, encryption, ZIP compression)
5. **Metadata Randomization**: Sets realistic timestamps spanning months or years
6. **File Creation**: Writes files with proper formats and extensions

### File Relationships

- **Emails** reference other files as attachments
- **PDF/Word documents** embed image references
- **Password-protected files** have passwords distributed in other files
- **Cross-references** create realistic file ecosystems

## Customizing Generation Data

The `data/` directory contains various data sources used for content generation. You can customize these to create more targeted or realistic content.

### Data File Types

#### **Vocabulary Files (.vocab)**
Text files with one word/phrase per line for specific categories:

```
data/RESTAURANT-NAME.vocab
data/RESTAURANT-FOOD.vocab
data/PERSON-FAMOUS.vocab
data/WEBSITE.vocab
data/RETAILER.vocab
```

**Example RESTAURANT-NAME.vocab:**
```
The Golden Spoon
Mama's Kitchen
Blue Ocean Bistro
Mountain View Cafe
```

#### **Name Data Files**
Demographic data for realistic name generation:

```
data/dist.male.first      # Male first names with frequency weights
data/dist.female.first    # Female first names with frequency weights  
data/dist.all.last        # Last names with frequency weights
```

**Example format:**
```
JAMES          3.318  3.318      1
ROBERT         3.143  6.461      2
JOHN           3.271  9.732      3
```

#### **Geographic Data (CSV)**
Location data for addresses and realistic geographic content:

```
data/us_cities.csv                           # US cities with state info
data/us_states.csv                          # US states data
data/bay_area_addresses.csv                 # Sample addresses
data/us_street_name_sorted_top75percent.csv # Common street names
```

**Example us_cities.csv:**
```csv
city,state_id,state_name,county_name,lat,lng
New York,NY,New York,New York County,40.7128,-74.0060
Los Angeles,CA,California,Los Angeles County,34.0522,-118.2437
```

#### **Text Content Files**
Source material for document content generation:

```
data/sentences.txt        # Individual sentences
data/story_sentences.txt  # Narrative sentences
data/queries.txt         # Question-style content
data/queries.csv         # Structured query data
```

**Example sentences.txt:**
```
The quarterly report shows significant growth in all sectors.
Our team has successfully completed the project ahead of schedule.
Please review the attached documents for detailed analysis.
```

#### **Day/Time Data**
```
data/DAY-OF-WEEK.vocab   # Days of the week in various formats
```

### Adding Custom Data

#### **1. Adding New Vocabulary Categories**

Create new `.vocab` files for specific domains:

```bash
# Create custom vocabulary file
echo -e "Artificial Intelligence\nMachine Learning\nDeep Learning\nNeural Networks" > data/TECHNOLOGY.vocab
```

#### **2. Adding Language-Specific Content**

Create language-specific data files:

```bash
# Spanish vocabulary
echo -e "Restaurante El Sol\nCafé Luna\nBistro Madrid" > data/RESTAURANT-NAME-ES.vocab

# French sentences
echo -e "Le rapport trimestriel montre une croissance significative.\nNotre équipe a terminé le projet avec succès." > data/sentences-fr.txt
```

#### **3. Adding Custom Geographic Data**

Add location data for specific regions:

```csv
# data/custom_locations.csv
city,state,country,lat,lng
Toronto,ON,Canada,43.6532,-79.3832
Vancouver,BC,Canada,49.2827,-123.1207
Montreal,QC,Canada,45.5017,-73.5673
```

#### **4. Adding Industry-Specific Content**

Create domain-specific content files:

```bash
# Medical terminology
echo -e "Patient consultation\nMedical examination\nTreatment plan\nDiagnostic results" > data/MEDICAL.vocab

# Legal terms  
echo -e "Contract review\nLegal analysis\nCompliance audit\nRisk assessment" > data/LEGAL.vocab

# Financial content
echo -e "Quarterly earnings report\nInvestment portfolio\nMarket analysis\nFinancial projections" > data/FINANCE.vocab
```

#### **5. Adding Custom Sentence Patterns**

Create structured content for specific document types:

```bash
# Business email templates
cat > data/business_emails.txt << EOF
I hope this email finds you well and that your projects are progressing smoothly.
Please find attached the requested documents for your review and approval.
We need to schedule a meeting to discuss the upcoming project milestones.
The quarterly results exceed our expectations and show strong growth trends.
EOF

# Technical documentation
cat > data/technical_content.txt << EOF
The system architecture follows industry best practices for scalability.
Implementation details are documented in the attached specifications.
Performance metrics indicate optimal system efficiency and reliability.
Security protocols have been implemented according to compliance standards.
EOF
```

### Data File Naming Conventions

- **Vocabulary files**: `CATEGORY.vocab` or `CATEGORY-SUBCATEGORY.vocab`
- **Language-specific**: `filename-LANG.ext` (e.g., `sentences-es.txt`)
- **Geographic data**: `location_type.csv` (e.g., `european_cities.csv`)
- **Content files**: `content_type.txt` (e.g., `technical_sentences.txt`)

### Using Custom Data

The phrase generator automatically discovers and uses files in the `data/` directory:

1. **Vocabulary files** (`.vocab`) are loaded for random word selection
2. **Text files** (`.txt`) provide sentence and paragraph content
3. **CSV files** supply structured data for names, locations, etc.
4. **Language detection** happens automatically based on file naming

### Testing Custom Data

After adding custom data files, test the generator:

```bash
# Run with minimal settings to test quickly
python main.py
```

Check the generated files to ensure your custom data is being incorporated correctly.

## Testing

The project includes comprehensive tests in the `tests/` directory:

```bash
# Run all file type tests
python tests/test_file_types.py

# Test metadata randomization
python tests/test_metadata.py

# Test email generation
python tests/test_email_enhancement.py

# Test PDF generation
python tests/test_pdf_fix.py
```

See [`tests/README.md`](tests/README.md) for detailed testing information.

## Project Structure

```
Chafftafarian-Chaff-Generator/
├── main.py                    # Main application entry point
├── settings.py               # Configuration management
├── templates.py              # File generation templates
├── file_linking.py           # Cross-referencing logic
├── phrase_generator.py       # Content generation engine
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── .env.example             # Example configuration
├── data/                    # Generation data sources
│   ├── *.vocab             # Vocabulary files
│   ├── *.csv               # Geographic and demographic data
│   ├── *.txt               # Text content sources
│   └── dist.*              # Name frequency data
├── tests/                   # Test suite
│   ├── README.md           # Testing documentation
│   ├── test_*.py           # Various test files
│   └── decode_chaff.py     # Utility for analyzing generated files
└── venv/                   # Python virtual environment
```

## Advanced Usage

### Generating Specific File Types

```bash
# Only generate emails and PDFs
CHAFF_FILE_TYPES=eml,pdf python main.py

# Generate large files (up to 100MB)
MAX_FILE_SIZE_BYTES=104857600 python main.py
```

### Language-Specific Generation

```bash
# Generate only Spanish content
INCLUDE_LANGUAGES=es python main.py

# Multi-language content
INCLUDE_LANGUAGES=en,es,fr,de python main.py
```

### Filling Available Space

```bash
# Fill drive leaving 1GB free
FILL_DRIVE=true MIN_REMAINING_DISK_SPACE_MB=1024 python main.py
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated and dependencies installed
2. **Permission Errors**: Check write permissions for target directory
3. **Disk Space**: Monitor available space when using `FILL_DRIVE=true`
4. **Memory Usage**: Large file generation may require significant RAM

### Debug Mode

Enable verbose logging by modifying the script or using debug test files:

```bash
python tests/test_pdf_debug.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security Notice

This tool is designed for legitimate testing and research purposes. Users are responsible for ensuring compliance with applicable laws and regulations when using this software.