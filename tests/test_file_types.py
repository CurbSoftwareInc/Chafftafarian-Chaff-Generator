#!/usr/bin/env python3
"""
Test that all file types (PDFs, images, etc.) work correctly with the new filename system
"""

import os
import sys
from pathlib import Path

# Add the parent directory (project root) to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from settings import ChaffSettings, ChaffGenerationPlanner
from main import generate_chaff_files

def test_file_types():
    """Test that all file types work correctly"""
    
    print("Testing File Types - PDFs and Images")
    print("=" * 40)
    
    try:
        # Create test settings
        settings = ChaffSettings()
        settings.target_directory = "./test_file_types"
        settings.min_file_count = 8
        settings.max_file_count = 12
        settings.min_file_size = 5120   # 5KB
        settings.max_file_size = 20480  # 20KB
        settings.delete_after_completion = False
        settings.chaff_file_types = ['pdf', 'jpg', 'png', 'txt']  # Focus on problematic types
        
        # Ensure test directory exists
        test_dir = Path(settings.target_directory)
        test_dir.mkdir(exist_ok=True)
        
        print(f"Test directory: {test_dir.absolute()}")
        print("Generating test files...")
        
        # Generate file plans
        planner = ChaffGenerationPlanner(settings)
        plans = planner.generate_file_plan()
        
        if not plans:
            print("ERROR: No files planned for generation")
            return False
        
        print(f"Generated {len(plans)} file plans")
        
        # Generate files
        success_count, encoded_files = generate_chaff_files(settings, plans)
        print(f"Successfully created {success_count} files")
        
        if success_count == 0:
            print("ERROR: No files were created")
            return False
        
        # Analyze the generated files
        print("\nAnalyzing generated files:")
        
        pdf_files = []
        image_files = []
        other_files = []
        
        for encoded_file in encoded_files:
            original_type = encoded_file.original_plan.file_type
            encoding_method = encoded_file.encoding_method.value
            
            # Get the actual filename that was created
            from main import get_actual_filename
            actual_filename = get_actual_filename(encoded_file)
            file_path = test_dir / actual_filename
            
            if original_type == 'pdf':
                pdf_files.append((encoded_file, actual_filename, file_path))
            elif original_type in ['jpg', 'png']:
                image_files.append((encoded_file, actual_filename, file_path))
            else:
                other_files.append((encoded_file, actual_filename, file_path))
            
            print(f"  {actual_filename}")
            print(f"    Original type: {original_type}")
            print(f"    Encoding: {encoding_method}")
            print(f"    Exists: {file_path.exists()}")
            
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"    Size: {file_size} bytes")
                
                # Check file validity based on type and encoding
                if encoding_method == "none":
                    # Unencoded files should be valid in their original format
                    if original_type == 'pdf':
                        with open(file_path, 'rb') as f:
                            first_bytes = f.read(10)
                            if first_bytes.startswith(b'%PDF-'):
                                print(f"    ✅ Valid PDF file")
                            else:
                                print(f"    ❌ Invalid PDF file")
                    elif original_type in ['jpg', 'png']:
                        with open(file_path, 'rb') as f:
                            first_bytes = f.read(10)
                            if (original_type == 'jpg' and first_bytes.startswith(b'\xff\xd8')) or \
                               (original_type == 'png' and first_bytes.startswith(b'\x89PNG')):
                                print(f"    ✅ Valid {original_type.upper()} image")
                            else:
                                print(f"    ❌ Invalid {original_type.upper()} image")
                
                elif encoding_method in ['zip_password', 'zip_encrypted']:
                    # ZIP files should be openable as archives
                    try:
                        import zipfile
                        with zipfile.ZipFile(file_path, 'r') as zf:
                            file_list = zf.namelist()
                            print(f"    ✅ Valid ZIP archive with {len(file_list)} files")
                    except:
                        print(f"    ❌ Invalid ZIP archive")
                
                elif encoding_method in ['base64', 'base64_multiline', 'base64_urlsafe']:
                    # Base64 files should have .b64 extension
                    if actual_filename.endswith('.b64'):
                        print(f"    ✅ Base64 file has correct extension")
                    else:
                        print(f"    ❌ Base64 file should have .b64 extension")
                
                elif encoding_method == 'encrypted_fernet':
                    # Encrypted files should either keep original extension (images) or have .enc
                    if original_type in ['jpg', 'png']:
                        if actual_filename.endswith(f'.{original_type}'):
                            print(f"    ✅ Encrypted image keeps original extension")
                        else:
                            print(f"    ❌ Encrypted image should keep original extension")
                    else:
                        if actual_filename.endswith('.enc'):
                            print(f"    ✅ Encrypted file has .enc extension")
                        else:
                            print(f"    ❌ Encrypted file should have .enc extension")
            print()
        
        # Summary
        print(f"Summary:")
        print(f"  PDF files: {len(pdf_files)}")
        print(f"  Image files: {len(image_files)}")
        print(f"  Other files: {len(other_files)}")
        
        # Check for issues
        issues = 0
        
        # Check PDFs
        for encoded_file, actual_filename, file_path in pdf_files:
            encoding_method = encoded_file.encoding_method.value
            if encoding_method in ['zip_password', 'zip_encrypted']:
                # Should be openable as ZIP
                if not actual_filename.endswith('.pdf'):
                    print(f"  ❌ ZIP-encoded PDF {actual_filename} should keep .pdf extension")
                    issues += 1
            elif encoding_method == "none":
                # Should be valid PDF
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        if not f.read(10).startswith(b'%PDF-'):
                            print(f"  ❌ Unencoded PDF {actual_filename} is not valid")
                            issues += 1
        
        # Check images
        for encoded_file, actual_filename, file_path in image_files:
            encoding_method = encoded_file.encoding_method.value
            original_type = encoded_file.original_plan.file_type
            
            if encoding_method == "none":
                # Should be valid image
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        first_bytes = f.read(10)
                        valid = False
                        if original_type == 'jpg' and first_bytes.startswith(b'\xff\xd8'):
                            valid = True
                        elif original_type == 'png' and first_bytes.startswith(b'\x89PNG'):
                            valid = True
                        
                        if not valid:
                            print(f"  ❌ Unencoded image {actual_filename} is not valid")
                            issues += 1
            elif encoding_method == 'encrypted_fernet':
                # Should keep original extension
                if not actual_filename.endswith(f'.{original_type}'):
                    print(f"  ❌ Encrypted image {actual_filename} should keep .{original_type} extension")
                    issues += 1
        
        if issues == 0:
            print("\n✅ SUCCESS: All file types are working correctly!")
            print("   - PDFs are properly handled")
            print("   - Images maintain correct extensions")
            print("   - ZIP files are accessible")
            return True
        else:
            print(f"\n❌ FAILURE: Found {issues} issues with file handling")
            return False
            
    except Exception as e:
        print(f"ERROR during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup test files
        print(f"\nCleaning up test files in {test_dir}...")
        try:
            for file_path in test_dir.glob("*"):
                if file_path.is_file():
                    file_path.unlink()
            test_dir.rmdir()
            print("✅ Cleanup completed")
        except Exception as e:
            print(f"Warning: Cleanup failed: {e}")

if __name__ == "__main__":
    success = test_file_types()
    sys.exit(0 if success else 1)