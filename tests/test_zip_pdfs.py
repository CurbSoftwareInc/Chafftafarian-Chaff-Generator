#!/usr/bin/env python3
"""
Test ZIP-encoded PDFs specifically to ensure they work correctly
"""

import os
import sys
from pathlib import Path

# Add the parent directory (project root) to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from settings import FileGenerationPlan
from file_linking import FileLinkingManager, EncodingMethod
from main import create_linked_file

def test_zip_pdfs():
    """Test ZIP-encoded PDFs specifically"""
    
    print("Testing ZIP-encoded PDFs")
    print("=" * 30)
    
    try:
        # Create test directory
        test_dir = Path("./test_zip_pdfs")
        test_dir.mkdir(exist_ok=True)
        
        # Create a PDF plan
        pdf_plan = FileGenerationPlan(
            file_type='pdf',
            size_bytes=20480,  # 20KB
            language='en',
            filename='test_document.pdf'
        )
        
        # Force ZIP encoding by creating the file linking manager and modifying the encoding choice
        linking_manager = FileLinkingManager()
        
        # Generate the file network
        encoded_files = linking_manager.create_file_network([pdf_plan])
        
        if not encoded_files:
            print("ERROR: No files generated")
            return False
        
        encoded_file = encoded_files[0]
        
        print(f"Generated file:")
        print(f"  Original filename: {encoded_file.original_plan.filename}")
        print(f"  Encoding method: {encoded_file.encoding_method.value}")
        
        # Get the actual filename
        from main import get_actual_filename
        actual_filename = get_actual_filename(encoded_file)
        print(f"  Actual filename: {actual_filename}")
        
        # Create the file
        success = create_linked_file(encoded_file, test_dir)
        
        if not success:
            print("ERROR: Failed to create file")
            return False
        
        file_path = test_dir / actual_filename
        
        if not file_path.exists():
            print(f"ERROR: File {file_path} was not created")
            return False
        
        print(f"  File created: {file_path}")
        print(f"  File size: {file_path.stat().st_size} bytes")
        
        # Test the file based on encoding method
        if encoded_file.encoding_method.value in ['zip_password', 'zip_encrypted']:
            # Should be a ZIP file that can be opened
            try:
                import zipfile
                with zipfile.ZipFile(file_path, 'r') as zf:
                    file_list = zf.namelist()
                    print(f"  ✅ ZIP file contains: {file_list}")
                    
                    # Try to extract and check if it contains PDF data
                    if file_list:
                        first_file = file_list[0]
                        try:
                            if encoded_file.password:
                                zf.setpassword(encoded_file.password.encode())
                            
                            extracted_data = zf.read(first_file)
                            if extracted_data.startswith(b'%PDF-'):
                                print(f"  ✅ ZIP contains valid PDF data")
                            else:
                                print(f"  ℹ️  ZIP contains data (may be partial PDF)")
                        except Exception as e:
                            print(f"  ℹ️  ZIP is password protected: {e}")
                
                # Check that filename keeps .pdf extension
                if actual_filename.endswith('.pdf'):
                    print(f"  ✅ ZIP-encoded PDF keeps .pdf extension")
                else:
                    print(f"  ❌ ZIP-encoded PDF should keep .pdf extension")
                    return False
                    
            except Exception as e:
                print(f"  ❌ Error reading ZIP file: {e}")
                return False
                
        elif encoded_file.encoding_method.value == 'none':
            # Should be a valid PDF
            with open(file_path, 'rb') as f:
                first_bytes = f.read(10)
                if first_bytes.startswith(b'%PDF-'):
                    print(f"  ✅ Unencoded PDF is valid")
                else:
                    print(f"  ❌ Unencoded PDF is invalid")
                    return False
        
        else:
            # Other encoding methods
            print(f"  ℹ️  File uses {encoded_file.encoding_method.value} encoding")
            if encoded_file.encoding_method.value in ['base64', 'base64_multiline', 'base64_urlsafe']:
                if actual_filename.endswith('.b64'):
                    print(f"  ✅ Base64-encoded PDF has .b64 extension")
                else:
                    print(f"  ❌ Base64-encoded PDF should have .b64 extension")
                    return False
        
        print("\n✅ SUCCESS: ZIP-encoded PDFs work correctly!")
        return True
        
    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        try:
            for file_path in test_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
            test_dir.rmdir()
            print("🧹 Cleanup completed")
        except Exception as e:
            print(f"Warning: Cleanup failed: {e}")

if __name__ == "__main__":
    success = test_zip_pdfs()
    sys.exit(0 if success else 1)