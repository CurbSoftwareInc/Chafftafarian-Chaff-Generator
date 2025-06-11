#!/usr/bin/env python3
"""
Debug PDF generation issues
"""

import os
import sys
from pathlib import Path

# Add the parent directory (project root) to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from templates import PDFTemplate

def test_pdf_generation():
    """Test PDF generation to identify corruption issues"""
    
    print("Testing PDF Generation - Debug Mode")
    print("=" * 40)
    
    try:
        # Create PDF template
        pdf_template = PDFTemplate('en')
        
        # Generate a small PDF
        print("Generating test PDF...")
        pdf_content = pdf_template.generate(target_size=50000, filename="test.pdf")
        
        print(f"Generated PDF size: {len(pdf_content)} bytes")
        
        # Write to file
        test_file = Path("debug_test.pdf")
        with open(test_file, 'wb') as f:
            f.write(pdf_content)
        
        print(f"Written to: {test_file.absolute()}")
        
        # Check if it's a valid PDF by looking at header/footer
        if pdf_content.startswith(b'%PDF-'):
            print("✅ PDF header is correct")
        else:
            print("❌ PDF header is missing or incorrect")
            print(f"First 20 bytes: {pdf_content[:20]}")
        
        if pdf_content.endswith(b'%%EOF') or b'%%EOF' in pdf_content[-50:]:
            print("✅ PDF footer is correct")
        else:
            print("❌ PDF footer is missing or incorrect")
            print(f"Last 50 bytes: {pdf_content[-50:]}")
        
        # Try to validate with a simple PDF check
        try:
            # Check for basic PDF structure
            content_str = pdf_content.decode('latin-1', errors='ignore')
            if '%PDF-' in content_str and '%%EOF' in content_str:
                print("✅ Basic PDF structure appears valid")
            else:
                print("❌ Basic PDF structure is invalid")
        except Exception as e:
            print(f"❌ Error checking PDF structure: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        test_file = Path("debug_test.pdf")
        if test_file.exists():
            try:
                test_file.unlink()
                print("🧹 Cleaned up test file")
            except:
                pass

if __name__ == "__main__":
    success = test_pdf_generation()
    sys.exit(0 if success else 1)