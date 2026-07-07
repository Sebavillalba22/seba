"""
process_photos.py — Process uploaded photos for use in carousel slides.

Usage: place uploaded photos in /mnt/user-data/uploads/, then run with a mapping:

    from process_photos import process

    photos = {
        'cover':    '/mnt/user-data/uploads/IMG_001.jpeg',
        'second':   '/mnt/user-data/uploads/IMG_002.jpeg',
    }
    process(photos, out_dir='/home/claude/carrusel')

This will create /home/claude/carrusel/cover_b64.txt and second_b64.txt with
base64-encoded JPEGs ready to embed inline in HTML.

CRITICAL: always uses ImageOps.exif_transpose() to fix camera-rotated photos.
Never skip this — phone photos come out upside-down or sideways otherwise.
"""
from PIL import Image, ImageOps
import base64
import io
from pathlib import Path


def process(photos: dict, out_dir: str, max_size: int = 1600, quality: int = 88):
    """
    Process a dict of {name: path} into base64-encoded .txt files in out_dir.

    Args:
        photos: dict mapping a short name to the source photo path
        out_dir: directory where the b64 .txt files will be saved
        max_size: max dimension (long edge). Use 1800 for portrait headshots.
        quality: JPEG quality (88 is a good default)
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    for name, path in photos.items():
        img = Image.open(path)
        # ALWAYS apply EXIF orientation - critical for phone photos
        img = ImageOps.exif_transpose(img)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality, optimize=True)
        b64 = base64.b64encode(buf.getvalue()).decode('ascii')
        b64_path = out / f'{name}_b64.txt'
        b64_path.write_text(b64)
        print(f'{name}: {img.size}, {len(b64)/1024:.0f}KB → {b64_path}')


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('Usage: python process_photos.py <name>=<path> ... <out_dir>')
        sys.exit(1)
    out_dir = sys.argv[-1]
    photos = dict(arg.split('=', 1) for arg in sys.argv[1:-1])
    process(photos, out_dir)
