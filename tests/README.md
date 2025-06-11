# Test Files Directory

This directory contains all test and utility files for the Chafftafarian Chaff Generator project.

## Test Files

### Core Functionality Tests
- **`test_metadata.py`** - Tests metadata randomization functionality for file timestamps
- **`test_file_types.py`** - Comprehensive tests for all supported file types (PDF, DOCX, XLSX, EML, etc.)

### PDF-Specific Tests
- **`test_pdf_debug.py`** - Debug tests for PDF generation issues
- **`test_pdf_pipeline.py`** - Tests PDF generation pipeline and encoding methods
- **`test_pdf_fix.py`** - Tests fixes for PDF corruption issues
- **`test_zip_pdfs.py`** - Tests ZIP encoding behavior with PDF files

### Email Tests
- **`test_email_enhancement.py`** - Tests EML file generation and RFC-822 compliance

## Utility Files
- **`decode_chaff.py`** - Utility script for decoding and analyzing generated chaff files

## Running Tests

To run any test file from the project root directory:

```bash
# Activate virtual environment
source venv/bin/activate

# Run a specific test
python tests/test_file_types.py

# Run metadata tests
python tests/test_metadata.py

# Run email tests
python tests/test_email_enhancement.py
```

## Test Results Summary

All tests verify the following key functionality:
- ✅ PDF files generate without corruption (no ZIP encoding)
- ✅ EML files follow proper RFC-822 standard structure
- ✅ File extensions remain original (no .b64 suffixes)
- ✅ Metadata randomization works across all file types
- ✅ Cross-references between files work correctly
- ✅ All encoding methods (base64, encryption, ZIP) work properly