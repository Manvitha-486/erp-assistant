import os
import shutil

base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")
core = os.path.join(base, "core")

os.makedirs(core, exist_ok=True)

for f in os.listdir(base):
    if f.endswith('.pdf') or f.endswith('.txt'):
        src = os.path.join(base, f)
        dst = os.path.join(core, f)
        print(f"Moving {src} -> {dst}")
        shutil.move(src, dst)
        
print("Move complete.")
print("Files in core:", os.listdir(core))
