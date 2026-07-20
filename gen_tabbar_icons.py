"""Generate emoji-style tabBar icons for the WeChat mini-program.

Uses Windows' built-in emoji font (seguiemj.ttf) + Pillow's embedded_color
support to render real color emoji. WeChat tabBar needs separate PNG files
for iconPath and selectedIconPath; for emoji style we use the same colorful
PNG for both states and let `tabBar.color`/`selectedColor` tint the label
text (mirroring how the old Vue BottomNav worked: emoji always colored,
label changes color).

Output: uni-app/src/static/tabbar/{home,food,weight,pk,profile}.png
        (5 files; each used for both iconPath and selectedIconPath)
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "uni-app" / "src" / "static" / "tabbar"
OUT.mkdir(parents=True, exist_ok=True)

FONT_PATH = "C:/Windows/Fonts/seguiemj.ttf"
# Render on a large canvas, then crop to content + resize to target.
LARGE = 300
FINAL = 81  # WeChat recommended tabBar icon size
# Padding ratio so the emoji is not edge-to-edge.
PADDING = 0.10

ICONS = [
    ("home", "\U0001F3E0"),     # home
    ("food", "\U0001F34E"),    # apple
    ("weight", "\U0001F4C9"),  # chart decreasing (fat-loss trend)
    ("pk", "\U0001F3C6"),      # trophy
    ("profile", "\U0001F464"),  # bust in silhouette
]

font = ImageFont.truetype(FONT_PATH, LARGE)

for name, ch in ICONS:
    # 1. Render on large transparent canvas
    big = Image.new("RGBA", (LARGE, LARGE), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    bbox = d.textbbox((0, 0), ch, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (LARGE - w) / 2 - bbox[0]
    y = (LARGE - h) / 2 - bbox[1]
    d.text((x, y), ch, font=font, embedded_color=True)

    # 2. Crop to non-transparent content
    cropped = big.crop(big.getbbox(alpha_only=True) or big.getbbox())

    # 3. Scale to fit FINAL with padding (preserve aspect ratio)
    cw, ch_ = cropped.size
    avail = int(FINAL * (1 - 2 * PADDING))
    scale = min(avail / cw, avail / ch_)
    new_w = max(1, int(cw * scale))
    new_h = max(1, int(ch_ * scale))
    scaled = cropped.resize((new_w, new_h), Image.LANCZOS)

    # 4. Center on FINAL canvas
    out_img = Image.new("RGBA", (FINAL, FINAL), (0, 0, 0, 0))
    ox = (FINAL - new_w) // 2
    oy = (FINAL - new_h) // 2
    out_img.alpha_composite(scaled, (ox, oy))

    out = OUT / f"{name}.png"
    out_img.save(out, "PNG")
    print(f"  wrote {out.name} (content {cw}x{ch_} -> {new_w}x{new_h}, offset {ox},{oy})")

print("done")
