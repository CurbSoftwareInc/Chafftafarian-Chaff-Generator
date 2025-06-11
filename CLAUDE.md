# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Chafftafarian Chaff Generator creates realistic-looking fake files (chaff) for security purposes. It generates various file types including emails with attachments, documents, and images that are cross-referenced and encoded to appear as legitimate data.

## Common Commands

### Setup
```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env file with desired settings
python main.py
```

### Sentence Generator Example (will be removed when main project is complete)
```bash
python Sentence-Generator/run_generator.py <num-of-scripts-to-generate>
```

## Architecture

### Main Application Structure
- `main.py` - Primary entry point (needs implementation)
- `settings.py` - Configuration management
- `data/` - Contains templates, images, and phrase generation resources
  - `images/` - Source images for chaff generation
  - `templates/` - File templates for different chaff types
  - `phrase_generator/` - Additional data for text generation

### Configuration System
- Settings managed via `.env` file
- Default target directory: `/home/$USER/.chaff`
- Configurable file types: txt, jpg, eml, pdf, docx, xlsx, csv
- Multi-language support: en, es, fr, de, cn, jp, ru
- File size range: 1MB-10MB, count range: 10-100 files

### Chaff Generation Strategy
The system creates interconnected files:
- Emails reference attachments and other files
- Files encoded using various methods (base64, compression, encryption)
- Cross-references between files create realistic data relationships
- Passwords and encryption keys randomly distributed across files

### Sentence-Generator Reference Implementation
Located in `Sentence-Generator/` directory - example of data generation patterns:
- Rich vocabulary datasets (names, addresses, restaurants, etc.)
- Configurable sentence types via `generation.conf`
- Available types: NUMBER, TIME, DATE, PHONE_NUMBER, NAME, ADDRESS, QUERY, SENTENCE