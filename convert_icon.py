from PIL import Image
import os

img_path = r"c:\Users\bbbvl\OneDrive\Desktop\ghost\assets\djinn_logo.png"
ico_path = r"c:\Users\bbbvl\OneDrive\Desktop\ghost\assets\djinn_logo.ico"

if os.path.exists(img_path):
    img = Image.open(img_path)
    # Convert and save as ico
    # We want various sizes for a good windows icon
    img.save(ico_path, format='ICO', sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (255, 255)])
    print(f"Icon saved to {ico_path}")
else:
    print(f"Source image not found: {img_path}")
