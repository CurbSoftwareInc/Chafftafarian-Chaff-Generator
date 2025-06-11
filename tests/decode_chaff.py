#!/usr/bin/env python3
"""
Chaff File Decoder Utility

This utility can decode chaff files that were encoded during generation.
It supports base64, encrypted, and compressed files.
"""

import argparse
import base64
import os
import sys
import zipfile
import io
from pathlib import Path
from typing import Optional

# Try to import cryptography for decryption
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# Try to import pyzipper for password-protected zips
try:
    import pyzipper
    PYZIPPER_AVAILABLE = True
except ImportError:
    PYZIPPER_AVAILABLE = False


def detect_encoding_method(filename: str) -> Optional[str]:
    """Detect encoding method from filename extension"""
    if filename.endswith('.b64'):
        return 'base64'
    elif filename.endswith('.enc'):
        return 'encrypted_fernet'
    elif filename.endswith('.zip'):
        return 'zip'
    elif filename.endswith('.dat'):
        return 'unknown'
    else:
        # Check if it might be a ZIP-encoded file that kept its original extension
        # This happens with PDFs that are ZIP-compressed
        try:
            import zipfile
            with zipfile.ZipFile(filename, 'r') as zf:
                # If we can open it as a ZIP, it's probably ZIP-encoded
                return 'zip'
        except:
            pass
        
        return None


def get_original_filename(encoded_filename: str) -> str:
    """Get the original filename by removing encoding extensions"""
    # Remove encoding extensions
    for ext in ['.b64', '.enc', '.zip', '.dat']:
        if encoded_filename.endswith(ext):
            return encoded_filename[:-len(ext)]
    return encoded_filename


def decode_base64_file(file_path: Path, output_path: Path) -> bool:
    """Decode a base64 encoded file"""
    try:
        with open(file_path, 'rb') as f:
            encoded_content = f.read()
        
        # Handle multiline base64 (remove newlines)
        if b'\n' in encoded_content:
            encoded_content = encoded_content.replace(b'\n', b'')
        
        # Try different base64 variants
        try:
            # Standard base64
            decoded_content = base64.b64decode(encoded_content)
        except:
            try:
                # URL-safe base64
                decoded_content = base64.urlsafe_b64decode(encoded_content)
            except:
                print(f"Error: Could not decode base64 content in {file_path}")
                return False
        
        with open(output_path, 'wb') as f:
            f.write(decoded_content)
        
        print(f"✅ Decoded base64 file: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error decoding base64 file {file_path}: {e}")
        return False


def decode_encrypted_file(file_path: Path, output_path: Path, password: str) -> bool:
    """Decode an encrypted file using Fernet encryption"""
    if not CRYPTO_AVAILABLE:
        print("Error: cryptography library not available for decryption")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Extract salt (first 16 bytes) and encrypted content
        salt = encrypted_data[:16]
        encrypted_content = encrypted_data[16:]
        
        # Derive key from password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        # Decrypt content
        fernet = Fernet(key)
        decrypted_content = fernet.decrypt(encrypted_content)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted_content)
        
        print(f"✅ Decrypted file: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error decrypting file {file_path}: {e}")
        print("Note: Make sure you have the correct password")
        return False


def decode_zip_file(file_path: Path, output_dir: Path, password: Optional[str] = None) -> bool:
    """Decode a ZIP file (with optional password)"""
    try:
        if password and PYZIPPER_AVAILABLE:
            # Use pyzipper for password-protected files
            with pyzipper.AESZipFile(file_path, 'r') as zf:
                zf.setpassword(password.encode())
                zf.extractall(output_dir)
        else:
            # Use standard zipfile
            with zipfile.ZipFile(file_path, 'r') as zf:
                if password:
                    zf.setpassword(password.encode())
                zf.extractall(output_dir)
        
        print(f"✅ Extracted ZIP file to: {output_dir}")
        return True
        
    except Exception as e:
        print(f"Error extracting ZIP file {file_path}: {e}")
        if password:
            print("Note: Make sure you have the correct password")
        return False


def main():
    """Main decoder function"""
    parser = argparse.ArgumentParser(
        description="Decode chaff files that were encoded during generation"
    )
    parser.add_argument(
        'input_file',
        help='Path to the encoded chaff file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output path (default: auto-detect from filename)'
    )
    parser.add_argument(
        '-p', '--password',
        help='Password for encrypted/password-protected files'
    )
    parser.add_argument(
        '--output-dir',
        help='Output directory for ZIP files (default: current directory)'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    
    if not input_path.exists():
        print(f"Error: Input file {input_path} does not exist")
        return 1
    
    # Detect encoding method
    encoding_method = detect_encoding_method(input_path.name)
    
    if encoding_method is None:
        print(f"Warning: Could not detect encoding method from filename {input_path.name}")
        print("File may not be encoded or may use an unknown encoding method")
        return 1
    
    print(f"Detected encoding method: {encoding_method}")
    
    # Determine output path
    if args.output:
        output_path = Path(args.output)
    else:
        original_filename = get_original_filename(input_path.name)
        output_path = input_path.parent / original_filename
    
    # Decode based on method
    success = False
    
    if encoding_method == 'base64':
        success = decode_base64_file(input_path, output_path)
        
    elif encoding_method == 'encrypted_fernet':
        if not args.password:
            print("Error: Password required for encrypted files (use -p/--password)")
            return 1
        success = decode_encrypted_file(input_path, output_path, args.password)
        
    elif encoding_method == 'zip':
        output_dir = Path(args.output_dir) if args.output_dir else input_path.parent
        success = decode_zip_file(input_path, output_dir, args.password)
        
    else:
        print(f"Error: Unsupported encoding method: {encoding_method}")
        return 1
    
    if success:
        print("✅ Decoding completed successfully!")
        return 0
    else:
        print("❌ Decoding failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())