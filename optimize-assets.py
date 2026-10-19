from pathlib import Path
import sys
from PIL import Image

root = Path(__file__).parent / (sys.argv[1] if len(sys.argv) > 1 else 'dist')
source = root / 'architecture.png'
target = root / 'architecture.webp'
with Image.open(source) as image:
    image.convert('RGB').save(target, 'WEBP', quality=88, method=6)
print(f'Hero image: {source.stat().st_size:,} -> {target.stat().st_size:,} bytes; dimensions preserved.')
