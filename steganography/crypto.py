import hashlib


def derive_key(stego_key: str) -> bytes:
    """Derive a deterministic 32-byte key from the user stego-key."""
    if not stego_key:
        raise ValueError("Stego-key cannot be empty.")
    return hashlib.sha256(stego_key.encode("utf-8")).digest()


def xor_bytes(data: bytes, key: bytes) -> bytes:
    if not key:
        raise ValueError("Encryption key cannot be empty.")
    return bytes(byte ^ key[i % len(key)] for i, byte in enumerate(data))


def encrypt_message(message: str, stego_key: str) -> bytes:
    plaintext = message.encode("utf-8")
    key = derive_key(stego_key)
    return xor_bytes(plaintext, key)


def decrypt_message(ciphertext: bytes, stego_key: str) -> str:
    key = derive_key(stego_key)
    plaintext = xor_bytes(ciphertext, key)
    try:
        return plaintext.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Invalid stego-key or corrupted encrypted message.") from exc
