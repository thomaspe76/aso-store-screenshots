#!/usr/bin/env python3
"""
App Store / Play Store Screenshot Composer
Composites headline text, device frame template, and app screenshot
into a pixel-perfect store-ready image.

Supports both iOS (App Store) and Android (Play Store) dimensions.

Usage:
  python compose.py --bg "#3D7A5F" --verb "TRACK" --desc "YOUR DOSES" \
                    --screenshot screen.png --output out.png --platform android
"""

import argparse
import os
from PIL import Image, ImageDraw, ImageFont, ImageChops

# ── Platform configurations ─────────────────────────────────────────
PLATFORMS = {
    "ios": {
        "canvas_w": 1290,
        "canvas_h": 2796,
        "device_w": 1030,
        "bezel": 15,
        "screen_corner_r": 62,
        "device_y": 720,
        "text_top": 200,
        "verb_size_max": 256,
        "verb_size_min": 150,
        "desc_size": 124,
        "frame_file": "device_frame_ios.png",
        "fonts": [
            "/Library/Fonts/SF-Pro-Display-Black.otf",
            "/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ],
    },
    "android": {
        "canvas_w": 1080,
        "canvas_h": 1920,
        "device_w": 820,
        "bezel": 12,
        "screen_corner_r": 40,
        "device_y": 640,
        "text_top": 100,
        "verb_size_max": 160,
        "verb_size_min": 90,
        "desc_size": 68,
        "frame_file": "device_frame_android.png",
        "fonts": [
            "/usr/share/fonts/truetype/roboto/Roboto-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/Library/Fonts/SF-Pro-Display-Black.otf",
        ],
    },
}

VERB_DESC_GAP = 20
DESC_LINE_GAP = 24


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def find_font(font_list):
    """Return the first available font path."""
    for f in font_list:
        if os.path.isfile(f):
            return f
    return None


def word_wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_font(text, max_w, size_max, size_min, font_path):
    """Return the largest font size where text fits within max_w."""
    dummy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    for size in range(size_max, size_min - 1, -4):
        font = ImageFont.truetype(font_path, size)
        bbox = dummy.textbbox((0, 0), text, font=font)
        if (bbox[2] - bbox[0]) <= max_w:
            return font
    return ImageFont.truetype(font_path, size_min)


def draw_centered(draw, y, text, font, canvas_w, max_w=None):
    lines = word_wrap(draw, text, font, max_w) if max_w else [text]
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        h = bbox[3] - bbox[1]
        draw.text((canvas_w // 2, y - bbox[1]), line, fill="white", font=font, anchor="mt")
        y += h + DESC_LINE_GAP
    return y


def compose(bg_hex, verb, desc, screenshot_path, output_path, platform="android"):
    cfg = PLATFORMS[platform]
    canvas_w = cfg["canvas_w"]
    canvas_h = cfg["canvas_h"]
    device_w = cfg["device_w"]
    bezel = cfg["bezel"]
    screen_w = device_w - 2 * bezel
    screen_corner_r = cfg["screen_corner_r"]

    bg = hex_to_rgb(bg_hex)

    # Find font
    font_path = find_font(cfg["fonts"])
    if not font_path:
        print(f"ERROR: No font found. Install Roboto-Bold or place a .ttf in assets/")
        return
    max_text_w = int(canvas_w * 0.92)

    # ── 1. Canvas ───────────────────────────────────────────────────
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (*bg, 255))
    draw = ImageDraw.Draw(canvas)

    # ── 2. Text ─────────────────────────────────────────────────────
    verb_font = fit_font(verb.upper(), max_text_w, cfg["verb_size_max"],
                         cfg["verb_size_min"], font_path)
    desc_font = ImageFont.truetype(font_path, cfg["desc_size"])

    y = cfg["text_top"]
    y = draw_centered(draw, y, verb.upper(), verb_font, canvas_w)
    y += VERB_DESC_GAP
    draw_centered(draw, y, desc.upper(), desc_font, canvas_w, max_w=max_text_w)

    # ── 3. Device positioning ───────────────────────────────────────
    device_y = cfg["device_y"]
    device_x = (canvas_w - device_w) // 2
    screen_x = device_x + bezel
    screen_y = device_y + bezel

    # ── 4. Screenshot into screen area ──────────────────────────────
    shot = Image.open(screenshot_path).convert("RGBA")
    scale = screen_w / shot.width
    sc_w = screen_w
    sc_h = int(shot.height * scale)
    shot = shot.resize((sc_w, sc_h), Image.LANCZOS)

    screen_h = canvas_h - screen_y + 500

    scr_mask = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(scr_mask).rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=screen_corner_r, fill=255,
    )
    scr_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(scr_layer).rounded_rectangle(
        [screen_x, screen_y, screen_x + screen_w, screen_y + screen_h],
        radius=screen_corner_r, fill=(0, 0, 0, 255),
    )
    scr_layer.paste(shot, (screen_x, screen_y))
    scr_layer.putalpha(scr_mask)
    canvas = Image.alpha_composite(canvas, scr_layer)

    # ── 5. Device frame template ────────────────────────────────────
    frame_path = os.path.join(os.path.dirname(__file__), "assets", cfg["frame_file"])
    if os.path.isfile(frame_path):
        frame_template = Image.open(frame_path).convert("RGBA")
        frame_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        frame_layer.paste(frame_template, (device_x, device_y))
        canvas = Image.alpha_composite(canvas, frame_layer)

    # ── 6. Save ─────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    canvas.convert("RGB").save(output_path, "PNG")
    print(f"✓ {output_path} ({canvas_w}×{canvas_h})")


def main():
    p = argparse.ArgumentParser(description="Compose App/Play Store screenshot")
    p.add_argument("--bg", required=True, help="Background hex colour (#3D7A5F)")
    p.add_argument("--verb", required=True, help="Action verb (TRACK)")
    p.add_argument("--desc", required=True, help="Benefit descriptor (YOUR DOSES)")
    p.add_argument("--screenshot", required=True, help="Simulator/emulator screenshot path")
    p.add_argument("--output", required=True, help="Output file path")
    p.add_argument("--platform", default="android", choices=["ios", "android"],
                   help="Target platform (default: android)")
    args = p.parse_args()

    compose(args.bg, args.verb, args.desc, args.screenshot, args.output, args.platform)


if __name__ == "__main__":
    main()
