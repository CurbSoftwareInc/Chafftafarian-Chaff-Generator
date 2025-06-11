"""
File linking and cross-reference system for creating interconnected chaff files.

This module handles creating relationships between files, encryption, encoding,
and embedding references and passwords throughout the chaff collection.
"""

import os
import base64
import random
import zipfile
import io
import string
import secrets
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

import pyzipper
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from faker import Faker

from settings import FileGenerationPlan


class EncodingMethod(Enum):
    """Available encoding methods for files"""
    NONE = "none"
    BASE64 = "base64"
    BASE64_MULTILINE = "base64_multiline"
    BASE64_URL_SAFE = "base64_urlsafe"
    ENCRYPTED_FERNET = "encrypted_fernet"
    ZIP_PASSWORD = "zip_password"
    ZIP_ENCRYPTED = "zip_encrypted"


@dataclass
class FileReference:
    """Represents a reference from one file to another"""
    source_file: str
    target_file: str
    reference_type: str  # 'attachment', 'password', 'key', 'data', 'backup'
    context: str  # Human-readable context for the reference


@dataclass
class EncodedFile:
    """Represents a file that has been encoded/encrypted"""
    original_plan: FileGenerationPlan
    encoded_content: bytes
    encoding_method: EncodingMethod
    password: Optional[str] = None
    key: Optional[str] = None
    salt: Optional[bytes] = None
    references: List[FileReference] = field(default_factory=list)


class PasswordGenerator:
    """Generates realistic passwords and keys"""
    
    def __init__(self):
        self.fake = Faker('en_US')
    
    def generate_password(self, strength: str = "medium") -> str:
        """Generate a password of specified strength"""
        if strength == "weak":
            # Common weak passwords
            weak_passwords = [
                "password123", "admin", "letmein", "welcome", "qwerty123",
                "password1", "123456", "admin123", "welcome1", "password"
            ]
            return random.choice(weak_passwords)
        elif strength == "medium":
            # Realistic medium strength passwords
            patterns = [
                f"{self.fake.word().title()}{random.randint(10, 99)}!",
                f"{self.fake.first_name()}{random.randint(1980, 2024)}",
                f"{self.fake.company().replace(' ', '').replace(',', '')[:8]}{random.randint(1, 99)}",
                f"{self.fake.city().replace(' ', '')}{random.randint(10, 999)}"
            ]
            return random.choice(patterns)
        else:  # strong
            # Strong random passwords
            chars = string.ascii_letters + string.digits + "!@#$%^&*"
            return ''.join(secrets.choice(chars) for _ in range(16))
    
    def generate_encryption_key(self) -> str:
        """Generate a base64-encoded encryption key"""
        key = Fernet.generate_key()
        return key.decode('utf-8')
    
    def generate_api_key(self) -> str:
        """Generate a realistic API key"""
        prefixes = ["sk_", "pk_", "api_", "key_", "token_"]
        prefix = random.choice(prefixes)
        key_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        return f"{prefix}{key_part}"


class FileEncoder:
    """Handles encoding and encryption of file content"""
    
    def __init__(self):
        self.password_gen = PasswordGenerator()
    
    def encode_file(self, content: bytes, method: EncodingMethod, password: str = None) -> Tuple[bytes, Dict[str, Any]]:
        """Encode file content using specified method"""
        metadata = {}
        
        if method == EncodingMethod.BASE64:
            encoded = base64.b64encode(content)
            metadata['encoding'] = 'base64'
            
        elif method == EncodingMethod.BASE64_MULTILINE:
            encoded = base64.b64encode(content)
            # Split into 64-character lines
            lines = [encoded[i:i+64] for i in range(0, len(encoded), 64)]
            encoded = b'\n'.join(lines)
            metadata['encoding'] = 'base64'
            metadata['format'] = 'multiline'
            
        elif method == EncodingMethod.BASE64_URL_SAFE:
            encoded = base64.urlsafe_b64encode(content)
            metadata['encoding'] = 'base64url'
            
        elif method == EncodingMethod.ENCRYPTED_FERNET:
            if not password:
                password = self.password_gen.generate_password("medium")
            
            # Derive key from password
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            
            # Encrypt content
            fernet = Fernet(key)
            encrypted = fernet.encrypt(content)
            
            # Combine salt and encrypted data
            encoded = salt + encrypted
            metadata['encryption'] = 'fernet'
            metadata['password'] = password
            metadata['salt'] = base64.b64encode(salt).decode()
            
        elif method == EncodingMethod.ZIP_PASSWORD:
            if not password:
                password = self.password_gen.generate_password("medium")
            
            buffer = io.BytesIO()
            with pyzipper.AESZipFile(buffer, 'w', compression=pyzipper.ZIP_LZMA, encryption=pyzipper.WZ_AES) as zf:
                zf.setpassword(password.encode())
                zf.writestr("data.bin", content)
            
            encoded = buffer.getvalue()
            metadata['compression'] = 'zip'
            metadata['encryption'] = 'aes'
            metadata['password'] = password
            
        elif method == EncodingMethod.ZIP_ENCRYPTED:
            if not password:
                password = self.password_gen.generate_password("strong")
            
            buffer = io.BytesIO()
            with pyzipper.AESZipFile(buffer, 'w', compression=pyzipper.ZIP_DEFLATED, encryption=pyzipper.WZ_AES) as zf:
                zf.setpassword(password.encode())
                # Add multiple files to make it more realistic
                zf.writestr("document.dat", content[:len(content)//2] if len(content) > 100 else content)
                if len(content) > 100:
                    zf.writestr("metadata.txt", content[len(content)//2:])
                zf.writestr("checksum.md5", b"d41d8cd98f00b204e9800998ecf8427e")
            
            encoded = buffer.getvalue()
            metadata['compression'] = 'zip'
            metadata['encryption'] = 'aes256'
            metadata['password'] = password
            
        else:  # NONE
            encoded = content
            metadata['encoding'] = 'none'
        
        return encoded, metadata


class FileLinkingManager:
    """Manages relationships and cross-references between files"""
    
    def __init__(self):
        self.encoder = FileEncoder()
        self.password_gen = PasswordGenerator()
        self.fake = Faker('en_US')
        self.file_references: List[FileReference] = []
        self.passwords: Dict[str, str] = {}  # filename -> password
        self.keys: Dict[str, str] = {}  # filename -> key
        self.encoded_files: List[EncodedFile] = []
    
    def create_file_network(self, plans: List[FileGenerationPlan]) -> List[EncodedFile]:
        """Create a network of interconnected files with encoding/encryption"""
        
        # Group files by type for easier linking
        emails = [p for p in plans if p.file_type == 'eml']
        documents = [p for p in plans if p.file_type in ['pdf', 'docx', 'txt']]
        spreadsheets = [p for p in plans if p.file_type in ['xlsx', 'csv']]
        images = [p for p in plans if p.file_type in ['jpg', 'png']]
        
        # Store file groups for reference
        self.file_groups = {
            'emails': emails,
            'documents': documents, 
            'spreadsheets': spreadsheets,
            'images': images,
            'all_files': plans
        }
        
        # Create encoded files with image embedding
        for plan in plans:
            encoding_method = self._choose_encoding_method(plan.file_type)
            
            # Generate content first (will be replaced with actual template content)
            from templates import TemplateFactory
            template = TemplateFactory.create_template(plan.file_type, plan.language)
            
            # For documents, pass image references before generating content
            if plan.file_type in ['pdf', 'docx'] and hasattr(template, 'set_image_references'):
                # Find 1-3 images to embed in this document
                if images:
                    num_images = random.randint(1, min(3, len(images)))
                    embedded_images = random.sample(images, num_images)
                    image_filenames = [img.filename for img in embedded_images]
                    template.set_image_references(image_filenames)
            
            # For emails, pass both image and attachment references
            elif plan.file_type == 'eml' and hasattr(template, 'set_image_references'):
                # Add images to emails
                if images:
                    num_images = random.randint(1, min(4, len(images)))
                    email_images = random.sample(images, num_images)
                    image_filenames = [img.filename for img in email_images]
                    template.set_image_references(image_filenames)
                
                # Add attachments to emails (documents and spreadsheets)
                if hasattr(template, 'set_attachment_references'):
                    potential_attachments = documents + spreadsheets
                    if potential_attachments:
                        num_attachments = random.randint(1, min(5, len(potential_attachments)))
                        email_attachments = random.sample(potential_attachments, num_attachments)
                        attachment_filenames = [att.filename for att in email_attachments]
                        template.set_attachment_references(attachment_filenames)
            
            original_content = template.generate(plan.size_bytes, plan.filename)
            
            # Encode the content
            encoded_content, metadata = self.encoder.encode_file(original_content, encoding_method)
            
            # Create encoded file record
            encoded_file = EncodedFile(
                original_plan=plan,
                encoded_content=encoded_content,
                encoding_method=encoding_method,
                password=metadata.get('password'),
                key=metadata.get('key'),
                salt=metadata.get('salt')
            )
            
            self.encoded_files.append(encoded_file)
            
            # Store passwords and keys for reference
            if encoded_file.password:
                self.passwords[plan.filename] = encoded_file.password
            if encoded_file.key:
                self.keys[plan.filename] = encoded_file.key
        
        # Create comprehensive cross-references
        self._create_email_attachments(emails, documents + spreadsheets + images)
        self._create_document_image_embeddings(documents, images)
        self._create_document_references(documents)
        self._create_spreadsheet_references(spreadsheets, documents + images)
        self._create_password_references(plans)  # All files can reference passwords
        self._create_backup_references(documents, spreadsheets)
        self._create_data_references(spreadsheets, documents)
        self._create_project_references(plans)  # Cross-project file references
        self._create_version_references(plans)  # Version control references
        
        # Update content with references
        self._update_email_content_with_references()
        self._update_document_content_with_references()
        self._update_spreadsheet_content_with_references()
        
        # Add password hints to random files
        self._distribute_password_hints()
        
        return self.encoded_files
    
    def _choose_encoding_method(self, file_type: str) -> EncodingMethod:
        """Choose appropriate encoding method based on file type and randomness"""
        
        # Binary files (PDFs, images) must maintain their integrity and proper MIME types
        # These files should NEVER be encoded/encrypted as it corrupts their format
        if file_type == 'pdf':
            # PDFs must remain unencoded to maintain proper format and MIME type
            return EncodingMethod.NONE
            
        elif file_type in ['jpg', 'png']:
            # Images must remain unencoded to maintain proper MIME types
            return EncodingMethod.NONE
            
        elif file_type == 'eml':
            # Emails are usually not encoded themselves, but may reference encoded attachments
            return EncodingMethod.NONE
            
        elif file_type == 'docx':
            # Word documents can use various encoding methods
            weights = [0.3, 0.2, 0.1, 0.1, 0.2, 0.05, 0.05]
            
        elif file_type in ['xlsx', 'csv']:
            # Data files often compressed or encoded
            weights = [0.2, 0.2, 0.1, 0.1, 0.1, 0.2, 0.1]
            
        elif file_type == 'txt':
            # Text files can use any encoding method
            weights = [0.3, 0.3, 0.2, 0.1, 0.05, 0.03, 0.02]
            
        else:
            # Default for other file types - conservative approach
            weights = [0.5, 0.2, 0.1, 0.1, 0.1, 0.0, 0.0]
        
        methods = list(EncodingMethod)
        return random.choices(methods, weights=weights)[0]
    
    def _create_email_attachments(self, emails: List[FileGenerationPlan], other_files: List[FileGenerationPlan]):
        """Create email-attachment relationships with increased density"""
        
        for email in emails:
            # Each email references 2-6 attachments (increased from 1-4)
            if len(other_files) > 0:
                num_attachments = random.randint(1, min(6, len(other_files)))
                attachments = random.sample(other_files, num_attachments)
                
                for attachment in attachments:
                    # Create different types of attachment references
                    attachment_contexts = [
                        f"Please see the attached {attachment.file_type.upper()} file: {attachment.filename}",
                        f"Attachment: {attachment.filename} contains the requested data",
                        f"See attached document {attachment.filename} for details",
                        f"Please review the enclosed file: {attachment.filename}",
                        f"The file {attachment.filename} is attached for your reference",
                        f"Attached: {attachment.filename} (contains confidential information)",
                        f"Please find {attachment.filename} attached to this email",
                        f"Document attached: {attachment.filename} - requires immediate attention"
                    ]
                    
                    ref = FileReference(
                        source_file=email.filename,
                        target_file=attachment.filename,
                        reference_type="attachment",
                        context=random.choice(attachment_contexts)
                    )
                    self.file_references.append(ref)
                    
                    # Sometimes create bidirectional references
                    if random.random() < 0.3:
                        reverse_ref = FileReference(
                            source_file=attachment.filename,
                            target_file=email.filename,
                            reference_type="email_source",
                            context=f"This file was sent via email: {email.filename}"
                        )
                        self.file_references.append(reverse_ref)
    
    def _create_document_image_embeddings(self, documents: List[FileGenerationPlan], images: List[FileGenerationPlan]):
        """Create references for images embedded in documents"""
        
        for document in documents:
            # 60% chance to embed 1-3 images in each document
            if random.random() < 0.6 and images:
                num_images = random.randint(1, min(3, len(images)))
                embedded_images = random.sample(images, num_images)
                
                for image in embedded_images:
                    ref = FileReference(
                        source_file=document.filename,
                        target_file=image.filename,
                        reference_type="embedded_image",
                        context=f"Document contains embedded image: {image.filename}"
                    )
                    self.file_references.append(ref)
    
    def _create_document_references(self, documents: List[FileGenerationPlan]):
        """Create cross-references between documents"""
        
        for i, doc in enumerate(documents):
            # Create 1-3 references to other documents
            other_docs = [d for d in documents if d.filename != doc.filename]
            if other_docs:
                num_refs = random.randint(1, min(3, len(other_docs)))
                referenced_docs = random.sample(other_docs, num_refs)
                
                for ref_doc in referenced_docs:
                    reference_types = [
                        f"See related document: {ref_doc.filename}",
                        f"Additional information in: {ref_doc.filename}",
                        f"Cross-reference: {ref_doc.filename}",
                        f"Supporting documentation: {ref_doc.filename}",
                        f"Referenced in document: {ref_doc.filename}",
                        f"See also: {ref_doc.filename} for complete details"
                    ]
                    
                    ref = FileReference(
                        source_file=doc.filename,
                        target_file=ref_doc.filename,
                        reference_type="document_reference",
                        context=random.choice(reference_types)
                    )
                    self.file_references.append(ref)
    
    def _create_spreadsheet_references(self, spreadsheets: List[FileGenerationPlan], other_files: List[FileGenerationPlan]):
        """Create references from spreadsheets to other files"""
        
        for sheet in spreadsheets:
            # Reference 2-4 other files
            if other_files:
                num_refs = random.randint(2, min(4, len(other_files)))
                referenced_files = random.sample(other_files, num_refs)
                
                for ref_file in referenced_files:
                    reference_contexts = [
                        f"Data source: {ref_file.filename}",
                        f"Supporting file: {ref_file.filename}",
                        f"Referenced document: {ref_file.filename}",
                        f"Source material: {ref_file.filename}",
                        f"Analysis based on: {ref_file.filename}",
                        f"Data extracted from: {ref_file.filename}"
                    ]
                    
                    ref = FileReference(
                        source_file=sheet.filename,
                        target_file=ref_file.filename,
                        reference_type="data_source",
                        context=random.choice(reference_contexts)
                    )
                    self.file_references.append(ref)
    
    def _create_project_references(self, all_files: List[FileGenerationPlan]):
        """Create project-based cross-references"""
        
        # Create fictional project groups
        project_names = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Phoenix', 'Titan', 'Nova', 'Apex']
        project_files = {}
        
        # Assign files to projects
        for file in all_files:
            if random.random() < 0.7:  # 70% of files belong to a project
                project = random.choice(project_names)
                if project not in project_files:
                    project_files[project] = []
                project_files[project].append(file)
        
        # Create cross-references within projects
        for project, files in project_files.items():
            if len(files) > 1:
                for file in files:
                    # Reference 1-2 other files in the same project
                    other_project_files = [f for f in files if f.filename != file.filename]
                    if other_project_files:
                        num_refs = random.randint(1, min(2, len(other_project_files)))
                        referenced = random.sample(other_project_files, num_refs)
                        
                        for ref_file in referenced:
                            ref = FileReference(
                                source_file=file.filename,
                                target_file=ref_file.filename,
                                reference_type="project_reference",
                                context=f"Project {project} file: {ref_file.filename}"
                            )
                            self.file_references.append(ref)
    
    def _create_version_references(self, all_files: List[FileGenerationPlan]):
        """Create version control references between files"""
        
        # Find files that could be versions of each other (similar names)
        base_names = {}
        for file in all_files:
            # Extract base name (remove version indicators)
            base_name = file.filename
            # Remove common version indicators
            for indicator in ['_v2', '_v3', '_final', '_draft', '_copy', '_backup', '_old']:
                base_name = base_name.replace(indicator, '')
            base_name = base_name.split('.')[0]  # Remove extension
            
            if base_name not in base_names:
                base_names[base_name] = []
            base_names[base_name].append(file)
        
        # Create version references for files with same base name
        for base_name, files in base_names.items():
            if len(files) > 1:
                for i, file in enumerate(files):
                    # Reference other versions
                    other_versions = [f for f in files if f.filename != file.filename]
                    for other_file in other_versions:
                        version_contexts = [
                            f"Previous version: {other_file.filename}",
                            f"Updated version of: {other_file.filename}",
                            f"See also version: {other_file.filename}",
                            f"Replaces: {other_file.filename}",
                            f"Related version: {other_file.filename}"
                        ]
                        
                        ref = FileReference(
                            source_file=file.filename,
                            target_file=other_file.filename,
                            reference_type="version_reference",
                            context=random.choice(version_contexts)
                        )
                        self.file_references.append(ref)
    
    def _create_password_references(self, files: List[FileGenerationPlan]):
        """Create references to passwords hidden in other files"""
        
        # Find files that need passwords
        password_protected = [f for f in self.encoded_files 
                            if f.password and f.original_plan in files]
        
        for protected_file in password_protected:
            # 70% chance to hide password reference in another file
            if random.random() < 0.7:
                # Choose a file to hide the password in
                possible_containers = [f for f in files 
                                     if f.filename != protected_file.original_plan.filename 
                                     and f.file_type in ['eml', 'txt', 'docx']]
                
                if possible_containers:
                    container = random.choice(possible_containers)
                    ref = FileReference(
                        source_file=container.filename,
                        target_file=protected_file.original_plan.filename,
                        reference_type="password",
                        context=f"Password for {protected_file.original_plan.filename}: {protected_file.password}"
                    )
                    self.file_references.append(ref)
    
    def _create_backup_references(self, documents: List[FileGenerationPlan], spreadsheets: List[FileGenerationPlan]):
        """Create backup file relationships"""
        
        for doc in documents[:len(documents)//3]:  # Only some documents have backups
            if spreadsheets:
                backup = random.choice(spreadsheets)
                ref = FileReference(
                    source_file=doc.filename,
                    target_file=backup.filename,
                    reference_type="backup",
                    context=f"Backup data stored in: {backup.filename}"
                )
                self.file_references.append(ref)
    
    def _create_data_references(self, spreadsheets: List[FileGenerationPlan], documents: List[FileGenerationPlan]):
        """Create data source references"""
        
        for sheet in spreadsheets[:len(spreadsheets)//2]:
            if documents:
                source_doc = random.choice(documents)
                ref = FileReference(
                    source_file=sheet.filename,
                    target_file=source_doc.filename,
                    reference_type="data",
                    context=f"Data source: {source_doc.filename}"
                )
                self.file_references.append(ref)
    
    def _update_email_content_with_references(self):
        """Update email content to include attachment references and password hints"""
        
        for encoded_file in self.encoded_files:
            if encoded_file.original_plan.file_type == 'eml':
                # Find references from this email
                email_refs = [ref for ref in self.file_references 
                            if ref.source_file == encoded_file.original_plan.filename]
                
                if email_refs:
                    # Regenerate email content with references
                    from templates import EMLTemplate
                    template = EMLTemplate(encoded_file.original_plan.language)
                    
                    # Create custom email content with attachments
                    attachments = [ref for ref in email_refs if ref.reference_type == "attachment"]
                    password_refs = [ref for ref in self.file_references 
                                   if ref.reference_type == "password" 
                                   and ref.source_file == encoded_file.original_plan.filename]
                    
                    custom_content = self._generate_email_with_references(template, attachments, password_refs)
                    encoded_file.encoded_content = custom_content.encode('utf-8')
    
    def _generate_email_with_references(self, template, attachments, password_refs) -> str:
        """Generate email content with attachment and password references"""
        
        sender = template.fake.email()
        recipient = template.fake.email()
        subject = template._generate_subject()
        date = template.fake.date_time_between(start_date='-1y', end_date='now')
        
        # Categorize attachments by type
        image_attachments = [att for att in attachments if att.target_file.lower().endswith(('.jpg', '.png'))]
        document_attachments = [att for att in attachments if att.target_file.lower().endswith(('.pdf', '.docx', '.txt'))]
        data_attachments = [att for att in attachments if att.target_file.lower().endswith(('.xlsx', '.csv'))]
        
        # Build email body with references
        body_parts = []
        body_parts.append(f"Dear {template.fake.first_name()},")
        body_parts.append("")
        
        # Add context based on attachment types
        if image_attachments and document_attachments:
            body_parts.append("I've attached the requested documents along with supporting visual materials.")
        elif image_attachments:
            body_parts.append("Please review the attached images and visual documentation.")
        elif document_attachments:
            body_parts.append("The attached documents contain the information we discussed.")
        else:
            body_parts.append(template.fake.text(max_nb_chars=200))
        
        body_parts.append("")
        
        if attachments:
            body_parts.append("Attachments included:")
            
            # Group attachments by type for better organization
            if document_attachments:
                body_parts.append("  Documents:")
                for att in document_attachments:
                    descriptions = [
                        f"    - {att.target_file} (contains detailed analysis)",
                        f"    - {att.target_file} (confidential - handle with care)",
                        f"    - {att.target_file} (requires immediate review)",
                        f"    - {att.target_file} (supporting documentation)",
                        f"    - {att.target_file} (latest version - please review)"
                    ]
                    body_parts.append(random.choice(descriptions))
            
            if image_attachments:
                body_parts.append("  Visual Materials:")
                for att in image_attachments:
                    descriptions = [
                        f"    - {att.target_file} (charts and diagrams)",
                        f"    - {att.target_file} (screenshot for reference)",
                        f"    - {att.target_file} (visual documentation)",
                        f"    - {att.target_file} (supporting graphics)",
                        f"    - {att.target_file} (embedded in related documents)"
                    ]
                    body_parts.append(random.choice(descriptions))
            
            if data_attachments:
                body_parts.append("  Data Files:")
                for att in data_attachments:
                    descriptions = [
                        f"    - {att.target_file} (raw data for analysis)",
                        f"    - {att.target_file} (spreadsheet with calculations)",
                        f"    - {att.target_file} (database export)",
                        f"    - {att.target_file} (financial data - confidential)"
                    ]
                    body_parts.append(random.choice(descriptions))
            
            body_parts.append("")
        
        if password_refs:
            body_parts.append("Security Notes:")
            for pwd_ref in password_refs:
                body_parts.append(f"  - {pwd_ref.context}")
            body_parts.append("")
        
        # Add cross-references to other files
        if random.random() < 0.6:
            other_refs = [
                "Additional related files may be found in the shared directory.",
                "See previous email thread for context on these attachments.",
                "Some images are embedded within the attached documents.",
                "Please ensure all files are reviewed together for complete understanding.",
                "Cross-reference these files with our project documentation."
            ]
            body_parts.append(random.choice(other_refs))
            body_parts.append("")
        
        # Add urgency or action items
        if random.random() < 0.4:
            actions = [
                "Please confirm receipt and review by end of week.",
                "Your feedback on the attached materials is requested.",
                "These files require your approval before proceeding.",
                "Please coordinate with the team on the attached documentation."
            ]
            body_parts.append(random.choice(actions))
            body_parts.append("")
        
        body_parts.append("Best regards,")
        body_parts.append(template.fake.name())
        
        body = "\\n".join(body_parts)
        
        # Enhanced email headers for more realism
        content_type = "multipart/mixed" if attachments else "text/plain"
        
        email_content = f"""From: {template.fake.name()} <{sender}>
To: {template.fake.name()} <{recipient}>
Subject: {subject}
Date: {date.strftime('%a, %d %b %Y %H:%M:%S %z')}
Message-ID: <{template.fake.uuid4()}@{sender.split('@')[1]}>
MIME-Version: 1.0
Content-Type: {content_type}; charset=utf-8
Content-Transfer-Encoding: 8bit
X-Priority: Normal
X-Attachments: {len(attachments)} file(s)

{body}

--
{template.fake.name()}
{template.fake.job()}
{template.fake.company()}
{template.fake.phone_number()}
"""
        return email_content
    
    def _update_document_content_with_references(self):
        """Update document content to include file references"""
        
        for encoded_file in self.encoded_files:
            if encoded_file.original_plan.file_type in ['txt', 'docx']:
                # Find references from this document
                doc_refs = [ref for ref in self.file_references 
                           if ref.source_file == encoded_file.original_plan.filename]
                
                if doc_refs:
                    # Add references to the document content
                    additional_content = "\n\nREFERENCED FILES:\n"
                    for ref in doc_refs:
                        additional_content += f"- {ref.context}\n"
                    
                    # For txt files, append directly to content
                    if encoded_file.original_plan.file_type == 'txt':
                        try:
                            current_content = encoded_file.encoded_content.decode('utf-8', errors='ignore')
                            new_content = current_content + additional_content
                            encoded_file.encoded_content = new_content.encode('utf-8')
                        except:
                            pass  # Skip if content is encoded
    
    def _update_spreadsheet_content_with_references(self):
        """Update spreadsheet content to include file references in comments/notes"""
        
        for encoded_file in self.encoded_files:
            if encoded_file.original_plan.file_type in ['csv']:
                # Find references from this spreadsheet
                sheet_refs = [ref for ref in self.file_references 
                             if ref.source_file == encoded_file.original_plan.filename]
                
                if sheet_refs:
                    # Add references as comments in CSV
                    try:
                        current_content = encoded_file.encoded_content.decode('utf-8', errors='ignore')
                        lines = current_content.split('\n')
                        
                        # Add reference comments at the top
                        reference_comments = ["# REFERENCED FILES:"]
                        for ref in sheet_refs:
                            reference_comments.append(f"# {ref.context}")
                        reference_comments.append("")  # Empty line
                        
                        # Combine comments with existing content
                        new_lines = reference_comments + lines
                        new_content = '\n'.join(new_lines)
                        encoded_file.encoded_content = new_content.encode('utf-8')
                    except:
                        pass  # Skip if content is encoded
    
    def _distribute_password_hints(self):
        """Add password hints to random text files and documents"""
        
        text_files = [f for f in self.encoded_files 
                     if f.original_plan.file_type in ['txt', 'docx']]
        
        # Distribute some passwords as hints
        all_passwords = list(self.passwords.items())
        random.shuffle(all_passwords)
        
        for i, (protected_filename, password) in enumerate(all_passwords[:len(text_files)//2]):
            if i < len(text_files):
                target_file = text_files[i]
                
                # Add password hint to the file content
                hint_formats = [
                    f"Note: Archive password for {protected_filename}: {password}",
                    f"Backup access code: {password} (for {protected_filename})",
                    f"Decryption key: {password}",
                    f"Access credentials - File: {protected_filename}, Pass: {password}",
                    f"Security memo: {protected_filename} requires password '{password}'"
                ]
                
                hint = random.choice(hint_formats)
                
                # Append hint to existing content
                if target_file.original_plan.file_type == 'txt':
                    # For text files, just append
                    current_content = target_file.encoded_content.decode('utf-8', errors='ignore')
                    new_content = current_content + f"\\n\\n{hint}\\n"
                    target_file.encoded_content = new_content.encode('utf-8')
                else:
                    # For DOCX files, we'd need to regenerate with the template
                    # For now, just add as a comment in the content
                    pass
    
    def get_file_references_for_file(self, filename: str) -> List[FileReference]:
        """Get all references originating from a specific file"""
        return [ref for ref in self.file_references if ref.source_file == filename]
    
    def get_encoding_summary(self) -> Dict[str, int]:
        """Get summary of encoding methods used"""
        summary = {}
        for encoded_file in self.encoded_files:
            method = encoded_file.encoding_method.value
            summary[method] = summary.get(method, 0) + 1
        return summary