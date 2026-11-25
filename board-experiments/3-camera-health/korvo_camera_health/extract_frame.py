"""Extract the first CRC-checked capture from a saved ESP-IDF monitor log."""
from pathlib import Path
import argparse,re,zlib
p=argparse.ArgumentParser();p.add_argument('log');p.add_argument('output');a=p.parse_args()
s=Path(a.log).read_text(errors='replace');s=re.sub(r'\x1b\[[0-9;]*m','',s)
m=re.search(r'FM_JPEG_BEGIN (\d+) ([0-9a-fA-F]{8})\s+(.*?)FM_JPEG_END',s,re.S)
if not m:raise SystemExit('No complete JPEG block. Save the complete monitor output and retry.')
rows=re.findall(r'^FM_HEX ([0-9a-fA-F]+)\s*$',m[3],re.M)
try:b=bytes.fromhex(''.join(rows))
except ValueError:raise SystemExit('Invalid hex payload')
if len(b)!=int(m[1]):raise SystemExit('Byte count mismatch: incomplete or corrupted capture')
if zlib.crc32(b)!=int(m[2],16):raise SystemExit('CRC mismatch: do not use this frame')
if not b.startswith(b'\xff\xd8') or not b.endswith(b'\xff\xd9'):raise SystemExit('JPEG boundary markers missing')
Path(a.output).write_bytes(b);print(f'Saved {len(b)} CRC-checked bytes to {a.output}. Open the image and inspect it before inference.')
