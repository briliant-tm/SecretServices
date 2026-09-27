import hashlib
import random
import struct

from PIL import Image

from .crypto import decrypt_message, encrypt_message


MAGIC = b"STEG"
VERSION = 1
HEADER_FORMAT = ">4sBI"  # magic, version, encrypted payload length
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def calculate_capacity_bytes(image: Image.Image) -> int:
    """Capacity using 1 LSB per RGB channel, minus the fixed header."""
    rgb = image.convert("RGB")
    total_bits = rgb.width * rgb.height * 3
    return max(0, (total_bits - HEADER_SIZE * 8) // 8)


def _seed_from_key(stego_key: str) -> int:
    digest = hashlib.sha256(stego_key.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _pixel_channel_positions(image: Image.Image, stego_key: str):
    """Return randomized RGB-channel positions based on the stego-key."""
    total_channels = image.width * image.height * 3
    positions = list(range(total_channels))
    rng = random.Random(_seed_from_key(stego_key))
    rng.shuffle(positions)
    return positions


def _bytes_to_bits(data: bytes):
    for byte in data:
        for bit in range(7, -1, -1):
            yield (byte >> bit) & 1


def _bits_to_bytes(bits):
    result = bytearray()
    current = 0
    count = 0

    for bit in bits:
        current = (current << 1) | bit
        count += 1
        if count == 8:
            result.append(current)
            current = 0
            count = 0

    if count != 0:
        raise ValueError("Incomplete byte sequence.")
    return bytes(result)


def _set_channel_lsb(image: Image.Image, position: int, bit: int):
    width = image.width
    pixel_index, channel = divmod(position, 3)
    x = pixel_index % width
    y = pixel_index // width

    r, g, b = image.getpixel((x, y))
    values = [r, g, b]
    values[channel] = (values[channel] & 0xFE) | bit
    image.putpixel((x, y), tuple(values))


def _get_channel_lsb(image: Image.Image, position: int) -> int:
    width = image.width
    pixel_index, channel = divmod(position, 3)
    x = pixel_index % width
    y = pixel_index // width

    pixel = image.getpixel((x, y))
    return pixel[channel] & 1


def _build_header(payload_length: int) -> bytes:
    return struct.pack(HEADER_FORMAT, MAGIC, VERSION, payload_length)


def _parse_header(header: bytes):
    magic, version, payload_length = struct.unpack(HEADER_FORMAT, header)
    if magic != MAGIC:
        raise ValueError("Invalid stego data or wrong stego-key.")
    if version != VERSION:
        raise ValueError("Unsupported steganography data version.")
    return payload_length


def embed_message(image: Image.Image, message: str, stego_key: str) -> Image.Image:
    if not message:
        raise ValueError("Message cannot be empty.")
    if not stego_key:
        raise ValueError("Stego-key cannot be empty.")

    source = image.convert("RGB")
    encrypted = encrypt_message(message, stego_key)
    header = _build_header(len(encrypted))
    payload = header + encrypted

    capacity = calculate_capacity_bytes(source)
    if len(encrypted) > capacity:
        raise ValueError(
            f"Message is too large.\n"
            f"Maximum payload capacity: {capacity:,} bytes\n"
            f"Encrypted message size: {len(encrypted):,} bytes"
        )

    result = source.copy()
    positions = _pixel_channel_positions(result, stego_key)
    bits = _bytes_to_bits(payload)

    for position, bit in zip(positions, bits):
        _set_channel_lsb(result, position, bit)

    return result


def extract_message(image: Image.Image, stego_key: str) -> str:
    if not stego_key:
        raise ValueError("Stego-key cannot be empty.")

    source = image.convert("RGB")
    positions = _pixel_channel_positions(source, stego_key)

    header_bits = [_get_channel_lsb(source, p) for p in positions[:HEADER_SIZE * 8]]
    header = _bits_to_bytes(header_bits)
    payload_length = _parse_header(header)

    capacity = calculate_capacity_bytes(source)
    if payload_length > capacity:
        raise ValueError("Invalid payload length. The image may be corrupted or the key is wrong.")

    start = HEADER_SIZE * 8
    end = start + payload_length * 8
    payload_bits = [_get_channel_lsb(source, p) for p in positions[start:end]]
    ciphertext = _bits_to_bytes(payload_bits)

    return decrypt_message(ciphertext, stego_key)


def visualize_lsb(image: Image.Image) -> Image.Image:
    """Create an enhanced visualization of the RGB LSB plane."""
    source = image.convert("RGB")
    out = Image.new("RGB", source.size)

    pixels = []
    for r, g, b in source.getdata():
        pixels.append((
            255 if (r & 1) else 0,
            255 if (g & 1) else 0,
            255 if (b & 1) else 0,
        ))

    out.putdata(pixels)
    return out
