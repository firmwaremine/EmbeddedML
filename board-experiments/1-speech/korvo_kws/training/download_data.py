from pathlib import Path
import urllib.request,hashlib,zipfile
root=Path(__file__).resolve().parents[1]/'data';root.mkdir(exist_ok=True)
p=root/'mini_speech_commands.zip'
if not p.exists():urllib.request.urlretrieve('https://storage.googleapis.com/download.tensorflow.org/data/mini_speech_commands.zip',p)
assert hashlib.sha256(p.read_bytes()).hexdigest()=='49650f2341b26d886b46b3f4fb8fed59e30300b17550f1ee4a768b3106cf93a0'
with zipfile.ZipFile(p) as z:z.extractall(root)
print('Dataset downloaded and verified; see DATASET.md for attribution.')
