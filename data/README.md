# Data Directory - Custom Content Sources

This directory contains data sources used by the Chafftafarian Chaff Generator to create realistic content. You can customize these files or add new ones to tailor the generated content to your specific needs.

## File Types Overview

### 📝 Vocabulary Files (*.vocab)
**Purpose**: Word lists for specific categories  
**Format**: One word/phrase per line  
**Usage**: Random selection for content generation

**Existing Files:**
- `PERSON-FAMOUS.vocab` - Famous person names
- `RESTAURANT-NAME.vocab` - Restaurant names
- `RESTAURANT-FOOD.vocab` - Food items
- `RESTAURANT-TYPE.vocab` - Restaurant types
- `RETAILER.vocab` - Retail store names
- `WEBSITE.vocab` - Website names
- `DAY-OF-WEEK.vocab` - Day names
- `TECHNOLOGY.vocab` - Technology terms (example)

**Example Custom File:**
```bash
# Create data/MEDICAL.vocab
echo -e "Patient Care\nMedical Records\nDiagnostic Imaging\nTreatment Plan" > MEDICAL.vocab
```

### 👥 Name Data Files
**Purpose**: Realistic name generation with frequency weights  
**Format**: Name + frequency data

**Files:**
- `dist.male.first` - Male first names
- `dist.female.first` - Female first names  
- `dist.all.last` - Last names

**Format Example:**
```
JAMES          3.318  3.318      1
ROBERT         3.143  6.461      2
```

### 🌍 Geographic Data (*.csv)
**Purpose**: Location information for addresses and geographic content  
**Format**: CSV with headers

**Existing Files:**
- `us_cities.csv` - US cities with coordinates
- `us_states.csv` - US state information
- `bay_area_addresses.csv` - Sample addresses
- `us_street_name_sorted_top75percent.csv` - Common street names
- `international_cities.csv` - Global cities (example)

**CSV Format Example:**
```csv
city,state,country,lat,lng,population
New York,NY,USA,40.7128,-74.0060,8982000
```

### 📄 Text Content Files (*.txt)
**Purpose**: Source sentences and paragraphs for document content  
**Format**: One sentence per line or paragraph blocks

**Existing Files:**
- `sentences.txt` - General sentences
- `story_sentences.txt` - Narrative content
- `queries.txt` - Question-style content
- `business_emails.txt` - Business email content (example)

### 📊 Structured Data (*.csv)
**Purpose**: Tabular data for spreadsheets and structured content

**Existing Files:**
- `queries.csv` - Query data in CSV format

## Adding Custom Content

### 1. Industry-Specific Vocabulary

```bash
# Healthcare
cat > HEALTHCARE.vocab << EOF
Patient Management
Electronic Health Records
Telemedicine
Clinical Research
Medical Imaging
EOF

# Finance
cat > FINANCE.vocab << EOF
Investment Portfolio
Risk Assessment
Financial Planning
Market Analysis
Asset Management
EOF
```

### 2. Language-Specific Content

```bash
# Spanish business terms
cat > BUSINESS-ES.vocab << EOF
Gestión Empresarial
Análisis Financiero
Desarrollo Estratégico
Recursos Humanos
EOF

# French sentences
cat > sentences-fr.txt << EOF
Le rapport trimestriel montre une croissance significative.
Notre équipe a terminé le projet avec succès.
Veuillez examiner les documents ci-joints.
EOF
```

### 3. Regional Geographic Data

```bash
# European cities
cat > european_cities.csv << EOF
city,country,region,lat,lng
London,United Kingdom,Western Europe,51.5074,-0.1278
Paris,France,Western Europe,48.8566,2.3522
Berlin,Germany,Central Europe,52.5200,13.4050
EOF
```

### 4. Custom Content Templates

```bash
# Technical documentation phrases
cat > technical_content.txt << EOF
The system architecture follows industry best practices.
Implementation details are documented in the specifications.
Performance metrics indicate optimal efficiency.
Security protocols meet compliance standards.
EOF

# Legal document content
cat > legal_content.txt << EOF
This agreement shall be governed by applicable law.
All parties agree to the terms and conditions herein.
Confidentiality provisions remain in effect indefinitely.
EOF
```

## File Naming Conventions

| Pattern | Purpose | Example |
|---------|---------|---------|
| `CATEGORY.vocab` | General vocabulary | `TECHNOLOGY.vocab` |
| `CATEGORY-SUBCATEGORY.vocab` | Specific vocabulary | `RESTAURANT-FOOD.vocab` |
| `content_type.txt` | Text content | `business_emails.txt` |
| `content-LANG.txt` | Language-specific | `sentences-es.txt` |
| `location_type.csv` | Geographic data | `european_cities.csv` |
| `data_type.csv` | Structured data | `customer_data.csv` |

## Content Integration

The phrase generator automatically:
- Discovers new files in the data directory
- Loads vocabulary files for random selection
- Uses text files for sentence generation
- Incorporates CSV data for structured content
- Detects language variants based on file naming

## Testing Custom Data

After adding custom files:

1. **Quick Test:**
   ```bash
   python main.py
   ```

2. **Verify Integration:**
   Check generated files to ensure your custom content appears

3. **Debug Issues:**
   ```bash
   python tests/test_file_types.py
   ```

## Best Practices

### Content Quality
- Use realistic, professional language
- Ensure vocabulary is appropriate for the domain
- Include varied sentence structures and lengths

### File Organization
- Group related content logically
- Use clear, descriptive filenames
- Maintain consistent formatting within files

### Language Support
- Add language codes to filenames for multi-language content
- Ensure character encoding is UTF-8
- Test with target language requirements

### Data Accuracy
- Verify geographic coordinates are correct
- Use realistic demographic data
- Ensure CSV headers match expected formats

## Examples in Action

When you add custom data files, they automatically enhance content generation:

- **Vocabulary files** → Random word selection in documents
- **Text files** → Sentence content in emails and documents  
- **CSV files** → Structured data in spreadsheets and addresses
- **Name files** → Realistic person names throughout content

The generator intelligently combines these sources to create cohesive, realistic content that matches your specified domains and languages.