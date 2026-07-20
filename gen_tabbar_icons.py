"""Generate simple tabBar icons for the WeChat mini-program.

Produces 10 PNGs in src/static/tabbar/:
  home / home-active
  food / food-active
  weight / weight-active
  pk / pk-active
  profile / profile-active

Style: flat circle with a single emoji-like glyph drawn via Pillow's
default bitmap font (no system font dependency).  Color theme matches
the app: inactive #86868b, active #007aff.
"""

from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent / "uni-app" / "src" / "static" / "tabbar"
OUT.mkdir(parents=True, exist_ok=True)

SIZE = 81  # recommended icon size for WeChat tabBar
INACTIVE = (134, 134, 139, 255)   # #86868b
ACTIVE = (0, 122, 255, 255)       # #007aff

# Each entry: (filename-stem, glyph-draw-lambda(draw, size, color))
# Glyphs are simple geometric icons so we don't depend on font files.
def draw_home(draw, s, c):
    # house: triangle roof + square body
    pts_roof = [(s // 2, 8), (8, s // 2), (s - 8, s // 2)]
    draw.polygon(pts_roof, fill=c)
    draw.rectangle([20, s // 2, s - 20, s - 10], fill=c)

def draw_food(draw, s, c):
    # fork & spoon approximation: two thin rectangles + circle
    draw.rectangle([20, 12, 28, s - 12], fill=c)   # fork stem
    draw.rectangle([16, 12, 32, 28], fill=c)        # fork head
    draw.ellipse([s - 32, 12, s - 16, 32], fill=c)  # spoon head
    draw.rectangle([s - 28, 28, s - 20, s - 12], fill=c)

def draw_weight(draw, s, c):
    # scale: rectangle base + circle dial
    draw.rectangle([10, s - 20, s - 10, s - 8], fill=c)
    draw.ellipse([18, 12, s - 18, s - 22], outline=c, width=4)
    draw.line([(s // 2, s // 2 - 4), (s // 2 + 10, s // 2 + 4)], fill=c, width=3)

def draw_pk(draw, s, c):
    # crossed swords -> two diagonal bars
    draw.line([(10, 10), (s - 10, s - 10)], fill=c, width=6)
    draw.line([(s - 10, 10), (10, s - 10)], fill=c, width=6)
    draw.ellipse([s // 2 - 8, s // 2 - 8, s // 2 + 8, s // 2 + 8], fill=c)

def draw_profile(draw, s, c):
    # head + shoulders silhouette
    draw.ellipse([s // 2 - 12, 12, s // 2 + 12, 36], fill=c)
    draw.pieslice([16, 30, s - 16, s + 16], 180, 360, fill=c)

GLYPHS = [
    ("home", draw_home),
    ("food", draw_food),
    ("weight", draw_weight),
    ("pk", draw_pk),
    ("profile", draw_profile),
]

for name, drawer in GLYPHS:
    for suffix, color in (("", INACTIVE), ("-active", ACTIVE)):
        img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        drawer(d, SIZE, color)
        out_path = OUT / f"{name}{suffix}.png"
        img.save(out_path, "PNG")
        print(f"  wrote {out_path.name}")

print("done")
