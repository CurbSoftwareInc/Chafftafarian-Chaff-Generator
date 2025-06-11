#!/usr/bin/env python3
"""
Test that the PDF corruption issue is fixed
"""

import os
import sys
from pathlib import Path

# Add the parent directory (project root) to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from settings import ChaffSettings, ChaffGenerationPlanner, FileGenerationPlan
from main import generate_chaff_files

def test_pdf_fix():
    """Test that PDFs are now properly handled with encoding extensions"""
    
    print("Testing PDF Fix - Encoding Extensions")
    print("=" * 45)
    
    try:
        # Create test settings
        settings = ChaffSettings()
        settings.target_directory = "./test_pdf_fix"
        settings.min_file_count = 3
        settings.max_file_count = 5
        settings.min_file_size = 10240  # 10KB
        settings.max_file_size = 51200  # 50KB
        settings.delete_after_completion = False
        settings.chaff_file_types = ['pdf', 'txt']  # Focus on PDFs
        
        # Ensure test directory exists
        test_dir = Path(settings.target_directory)
        test_dir.mkdir(exist_ok=True)
        
        print(f"Test directory: {test_dir.absolute()}")
        print("Generating test files with focus on PDFs...")
        
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
        
        # Check the generated files
        print("\nAnalyzing generated files:")
        pdf_files = []
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
            else:
                other_files.append((encoded_file, actual_filename, file_path))
            
            print(f"  {actual_filename}")
            print(f"    Original type: {original_type}")
            print(f"    Encoding: {encoding_method}")
            print(f"    Exists: {file_path.exists()}")
            
            if file_path.exists():
                file_size = file_path.stat().st_size
                print(f"    Size: {file_size} bytes")
                
                # Check if it's a proper PDF or encoded file
                if encoding_method == "none" and original_type == 'pdf':
                    # Should be a valid PDF
                    with open(file_path, 'rb') as f:
                        first_bytes = f.read(10)
                        if first_bytes.startswith(b'%PDF-'):
                            print(f"    ✅ Valid PDF file")
                        else:
                            print(f"    ❌ Invalid PDF file")
                elif encoding_method != "none":
                    # Should be encoded, filename should reflect this
                    if actual_filename != encoded_file.original_plan.filename:
                        print(f"    ✅ Filename correctly indicates encoding")
                    else:
                        print(f"    ❌ Filename should indicate encoding")
            print()
        
        # Summary
        print(f"Summary:")
        print(f"  PDF files generated: {len(pdf_files)}")
        print(f"  Other files generated: {len(other_files)}")
        
        # Check if any PDFs were encoded and have proper extensions
        encoded_pdfs = [pf for pf in pdf_files if pf[0].encoding_method.value != "none"]
        unencoded_pdfs = [pf for pf in pdf_files if pf[0].encoding_method.value == "none"]
        
        print(f"  Encoded PDFs: {len(encoded_pdfs)}")
        print(f"  Unencoded PDFs: {len(unencoded_pdfs)}")
        
        # Verify encoded PDFs have proper extensions
        success = True
        for encoded_file, actual_filename, file_path in encoded_pdfs:
            if not actual_filename.endswith(('.b64', '.enc', '.zip', '.dat')):
                print(f"  ❌ {actual_filename} should have encoding extension")
                success = False
            else:
                print(f"  ✅ {actual_filename} has proper encoding extension")
        
        # Verify unencoded PDFs are valid
        for encoded_file, actual_filename, file_path in unencoded_pdfs:
            if file_path.exists():
                with open(file_path, 'rb') as f:
                    first_bytes = f.read(10)
                    if first_bytes.startswith(b'%PDF-'):
                        print(f"  ✅ {actual_filename} is a valid PDF")
                    else:
                        print(f"  ❌ {actual_filename} is not a valid PDF")
                        success = False
        
        if success:
            print("\n✅ SUCCESS: PDF corruption issue is fixed!")
            print("   - Encoded PDFs have proper file extensions")
            print("   - Unencoded PDFs are valid PDF files")
            return True
        else:
            print("\n❌ FAILURE: PDF issues still exist")
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
    success = test_pdf_fix()
    sys.exit(0 if success else 1)