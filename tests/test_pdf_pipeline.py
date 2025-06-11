#!/usr/bin/env python3
"""
Test the full PDF generation pipeline to identify where corruption occurs
"""

import os
import sys
from pathlib import Path

# Add the parent directory (project root) to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from settings import ChaffSettings, ChaffGenerationPlanner, FileGenerationPlan
from templates import TemplateFactory
from file_linking import FileLinkingManager

def test_pdf_pipeline():
    """Test the full PDF generation pipeline"""
    
    print("Testing PDF Generation Pipeline")
    print("=" * 40)
    
    try:
        # Create a single PDF plan
        pdf_plan = FileGenerationPlan(
            file_type='pdf',
            size_bytes=50000,
            language='en',
            filename='test_pipeline.pdf'
        )
        
        print("Step 1: Direct template generation...")
        template = TemplateFactory.create_template('pdf', 'en')
        direct_content = template.generate(50000, 'test_direct.pdf')
        
        print(f"Direct generation: {len(direct_content)} bytes")
        
        # Write direct content
        with open('test_direct.pdf', 'wb') as f:
            f.write(direct_content)
        
        # Check direct content
        if direct_content.startswith(b'%PDF-') and (direct_content.endswith(b'%%EOF') or b'%%EOF' in direct_content[-50:]):
            print("✅ Direct generation produces valid PDF")
        else:
            print("❌ Direct generation produces invalid PDF")
        
        print("\nStep 2: Through file linking manager...")
        
        # Test through file linking manager
        linking_manager = FileLinkingManager()
        encoded_files = linking_manager.create_file_network([pdf_plan])
        
        if encoded_files:
            encoded_pdf = encoded_files[0]
            linked_content = encoded_pdf.encoded_content
            
            print(f"Linked generation: {len(linked_content)} bytes")
            print(f"Encoding method: {encoded_pdf.encoding_method.value}")
            
            # Write linked content
            with open('test_linked.pdf', 'wb') as f:
                f.write(linked_content)
            
            # Check linked content
            if encoded_pdf.encoding_method.value == 'none':
                # Should be a valid PDF
                if linked_content.startswith(b'%PDF-') and (linked_content.endswith(b'%%EOF') or b'%%EOF' in linked_content[-50:]):
                    print("✅ Linked generation (no encoding) produces valid PDF")
                else:
                    print("❌ Linked generation (no encoding) produces invalid PDF")
                    print(f"First 50 bytes: {linked_content[:50]}")
                    print(f"Last 50 bytes: {linked_content[-50:]}")
            else:
                print(f"ℹ️  PDF was encoded with {encoded_pdf.encoding_method.value}")
                print("This is expected - encoded PDFs won't be directly readable")
                
                # For base64 encoded, let's try to decode and check
                if 'base64' in encoded_pdf.encoding_method.value:
                    try:
                        import base64
                        if encoded_pdf.encoding_method.value == 'base64':
                            decoded = base64.b64decode(linked_content)
                        elif encoded_pdf.encoding_method.value == 'base64_urlsafe':
                            decoded = base64.urlsafe_b64decode(linked_content)
                        elif encoded_pdf.encoding_method.value == 'base64_multiline':
                            # Remove newlines and decode
                            clean_content = linked_content.replace(b'\n', b'')
                            decoded = base64.b64decode(clean_content)
                        
                        if decoded.startswith(b'%PDF-'):
                            print("✅ Decoded PDF is valid")
                        else:
                            print("❌ Decoded PDF is invalid")
                            
                    except Exception as e:
                        print(f"❌ Error decoding base64 PDF: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in pipeline test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        for filename in ['test_direct.pdf', 'test_linked.pdf']:
            try:
                Path(filename).unlink()
            except:
                pass

if __name__ == "__main__":
    success = test_pdf_pipeline()
    sys.exit(0 if success else 1)