#!/usr/bin/env python3
"""
Test script to verify metadata randomization functionality
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory (project root) to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from settings import ChaffSettings, ChaffGenerationPlanner
from main import generate_chaff_files, randomize_file_metadata

def test_metadata_randomization():
    """Test the metadata randomization functionality"""
    
    print("Testing Chafftafarian Chaff Generator - Metadata Randomization")
    print("=" * 60)
    
    # Create test settings
    settings = ChaffSettings()
    
    # Override settings for testing
    settings.target_directory = "./test_chaff"
    settings.min_file_count = 5
    settings.max_file_count = 10
    settings.min_file_size = 1024  # 1KB
    settings.max_file_size = 5120  # 5KB
    settings.delete_after_completion = False
    
    # Ensure test directory exists
    test_dir = Path(settings.target_directory)
    test_dir.mkdir(exist_ok=True)
    
    print(f"Test directory: {test_dir.absolute()}")
    print(f"Generating {settings.min_file_count}-{settings.max_file_count} test files...")
    
    try:
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
        
        # Show original timestamps
        print("\nOriginal file timestamps (before randomization):")
        for encoded_file in encoded_files[:3]:  # Show first 3
            file_path = test_dir / encoded_file.original_plan.filename
            if file_path.exists():
                stat = file_path.stat()
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                access_time = datetime.fromtimestamp(stat.st_atime)
                print(f"  {encoded_file.original_plan.filename}:")
                print(f"    Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"    Accessed: {access_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test metadata randomization
        print(f"\nRandomizing metadata for {len(encoded_files)} files...")
        randomize_file_metadata(settings, encoded_files)
        
        # Verify randomization worked
        print("\nVerifying randomization results:")
        randomized_count = 0
        current_time = datetime.now()
        
        for encoded_file in encoded_files:
            file_path = test_dir / encoded_file.original_plan.filename
            if file_path.exists():
                stat = file_path.stat()
                mod_time = datetime.fromtimestamp(stat.st_mtime)
                
                # Check if modification time is significantly different from current time
                time_diff = abs((current_time - mod_time).total_seconds())
                if time_diff > 86400:  # More than 1 day difference
                    randomized_count += 1
        
        print(f"Files with randomized timestamps: {randomized_count}/{len(encoded_files)}")
        
        if randomized_count > 0:
            print("✅ SUCCESS: Metadata randomization is working!")
            return True
        else:
            print("❌ FAILURE: Metadata randomization did not work as expected")
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
    success = test_metadata_randomization()
    sys.exit(0 if success else 1)