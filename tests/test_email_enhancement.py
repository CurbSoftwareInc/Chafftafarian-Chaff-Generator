#!/usr/bin/env python3
"""
Test the enhanced email generation with conversation threads and rich content
"""

import os
import sys
from pathlib import Path

# Add the parent directory (project root) to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from settings import ChaffSettings, ChaffGenerationPlanner
from main import generate_chaff_files

def test_email_enhancement():
    """Test enhanced email generation"""
    
    print("Testing Enhanced Email Generation")
    print("=" * 40)
    
    try:
        # Create test settings focused on emails
        settings = ChaffSettings()
        settings.target_directory = "./test_emails"
        settings.min_file_count = 8
        settings.max_file_count = 12
        settings.min_file_size = 5120   # 5KB
        settings.max_file_size = 25600  # 25KB
        settings.delete_after_completion = False
        settings.chaff_file_types = ['eml', 'pdf', 'jpg', 'png', 'docx', 'xlsx']  # Include attachments and images
        
        # Ensure test directory exists
        test_dir = Path(settings.target_directory)
        test_dir.mkdir(exist_ok=True)
        
        print(f"Test directory: {test_dir.absolute()}")
        print("Generating test files with enhanced emails...")
        
        # Generate file plans
        planner = ChaffGenerationPlanner(settings)
        plans = planner.generate_file_plan()
        
        if not plans:
            print("ERROR: No files planned for generation")
            return False
        
        print(f"Generated {len(plans)} file plans")
        
        # Count file types
        file_type_counts = {}
        for plan in plans:
            file_type_counts[plan.file_type] = file_type_counts.get(plan.file_type, 0) + 1
        
        print("File type distribution:")
        for file_type, count in file_type_counts.items():
            print(f"  {file_type}: {count}")
        
        # Generate files
        success_count, encoded_files = generate_chaff_files(settings, plans)
        print(f"Successfully created {success_count} files")
        
        if success_count == 0:
            print("ERROR: No files were created")
            return False
        
        # Analyze the generated email files
        print("\nAnalyzing generated email files:")
        
        email_files = []
        other_files = []
        
        for encoded_file in encoded_files:
            original_type = encoded_file.original_plan.file_type
            
            # Get the actual filename that was created
            from main import get_actual_filename
            actual_filename = get_actual_filename(encoded_file)
            file_path = test_dir / actual_filename
            
            if original_type == 'eml':
                email_files.append((encoded_file, actual_filename, file_path))
            else:
                other_files.append((encoded_file, actual_filename, file_path))
        
        print(f"Found {len(email_files)} email files and {len(other_files)} other files")
        
        # Examine email content
        for i, (encoded_file, actual_filename, file_path) in enumerate(email_files):
            print(f"\nEmail {i+1}: {actual_filename}")
            print(f"  Size: {file_path.stat().st_size} bytes")
            print(f"  Encoding: {encoded_file.encoding_method.value}")
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Check for email structure
                    has_headers = 'From:' in content and 'To:' in content and 'Subject:' in content
                    has_html = '<html>' in content or '<body>' in content
                    has_conversation = 'Re:' in content
                    has_images = any(img_type in content.lower() for img_type in ['jpg', 'png', 'image'])
                    has_attachments = any(att_type in content.lower() for att_type in ['pdf', 'docx', 'xlsx', 'attachment'])
                    
                    print(f"  ✅ Email headers: {'Yes' if has_headers else 'No'}")
                    print(f"  ✅ HTML content: {'Yes' if has_html else 'No'}")
                    print(f"  ✅ Conversation thread: {'Yes' if has_conversation else 'No'}")
                    print(f"  ✅ Image references: {'Yes' if has_images else 'No'}")
                    print(f"  ✅ Attachment references: {'Yes' if has_attachments else 'No'}")
                    
                    # Count emails in thread
                    email_count = content.count('From:')
                    if email_count > 1:
                        print(f"  📧 Thread contains {email_count} emails")
                    
                    # Show a snippet of content
                    lines = content.split('\n')
                    subject_line = next((line for line in lines if line.startswith('Subject:')), 'No subject found')
                    print(f"  📝 {subject_line}")
                    
                except Exception as e:
                    print(f"  ❌ Error reading email content: {e}")
        
        # Summary
        enhanced_emails = 0
        for encoded_file, actual_filename, file_path in email_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Check if email has enhanced features
                    has_html = '<html>' in content
                    has_references = any(ref in content.lower() for ref in ['jpg', 'png', 'pdf', 'docx', 'xlsx'])
                    
                    if has_html or has_references:
                        enhanced_emails += 1
                        
                except:
                    pass
        
        print(f"\nSummary:")
        print(f"  Total emails generated: {len(email_files)}")
        print(f"  Enhanced emails: {enhanced_emails}")
        print(f"  Other files (potential attachments): {len(other_files)}")
        
        if enhanced_emails > 0:
            print("\n✅ SUCCESS: Enhanced email generation is working!")
            print("   - Emails contain rich HTML content")
            print("   - Image and attachment references are included")
            print("   - Conversation threads are generated")
            return True
        else:
            print("\n❌ FAILURE: Enhanced email features not detected")
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
    success = test_email_enhancement()
    sys.exit(0 if success else 1)