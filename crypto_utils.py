#!/usr/bin/env python3
"""
Utility functions for password encryption/decryption.
Used for NAS password storage.
"""

import os
from cryptography.fernet import Fernet
from pathlib import Path


class PasswordCrypto:
    """Handle password encryption/decryption with Fernet."""
    
    def __init__(self, key_file="/home/pi/thinkcity-dashboard-v3/.dashboard.key"):
        """Initialize with key file path."""
        self.key_file = Path(key_file)
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _load_or_create_key(self):
        """Load existing key or create new one."""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            # Create new key
            key = Fernet.generate_key()
            
            # Ensure directory exists
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save key with restricted permissions
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Set file permissions to 600 (read/write for owner only)
            os.chmod(self.key_file, 0o600)
            
            return key
    
    def encrypt(self, password: str) -> str:
        """Encrypt password and return base64 encoded string."""
        if not password:
            return ""
        
        encrypted = self.cipher.encrypt(password.encode('utf-8'))
        return encrypted.decode('utf-8')
    
    def decrypt(self, encrypted_password: str) -> str:
        """Decrypt password from base64 encoded string."""
        if not encrypted_password:
            return ""
        
        try:
            decrypted = self.cipher.decrypt(encrypted_password.encode('utf-8'))
            return decrypted.decode('utf-8')
        except Exception as e:
            print(f"Decryption error: {e}")
            return ""


# Global instance for easy access
_crypto_instance = None

def get_crypto():
    """Get singleton PasswordCrypto instance."""
    global _crypto_instance
    if _crypto_instance is None:
        _crypto_instance = PasswordCrypto()
    return _crypto_instance


if __name__ == "__main__":
    # Test encryption/decryption
    crypto = PasswordCrypto("/tmp/test.key")
    
    test_password = "MySecretPassword123!"
    print(f"Original: {test_password}")
    
    encrypted = crypto.encrypt(test_password)
    print(f"Encrypted: {encrypted}")
    
    decrypted = crypto.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    assert test_password == decrypted, "Encryption/Decryption failed!"
    print("\n✅ Encryption test passed!")
