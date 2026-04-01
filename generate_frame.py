#!/usr/bin/env python3
"""
Generate device frame templates for iPhone and Android (Pixel).
Output: assets/device_frame_ios.png and assets/device_frame_android.png

compose.py positions these dynamically based on text height and platform.
"""

import os
from PIL import Image, ImageDraw, ImageChops

# ── iPhone dimensions (from original skill) ────────────────────────
IOS_DEVICE_W = 1030
IOS_DEVICE_H = 2800           # tall enough to bleed off any canvas
IOS_DEVICE_CORNER_R = 77
IOS_BEZEL = 15
IOS_SCREEN_CORNER_R = 62
IOS_DI_W = 130               # Dynamic Island width
IOS_DI_H = 38                # Dynamic Island height
IOS_DI_TOP = 14              # offset from top of screen
IOS_SCREEN_W = IOS_DEVICE_W - 2 * IOS_BEZEL
IOS_SCREEN_H = IOS_DEVICE_H - 2 * IOS_BEZEL

# ── Android (Pixel) dimensions ─────────────────────────────────────
ANDROID_DEVICE_W = 820
ANDROID_DEVICE_H = 1780
ANDROID_DEVICE_CORNER_R = 52
ANDROID_BEZEL = 12
ANDROID_SCREEN_CORNER_R = 40
ANDROID_SCREEN_W = ANDROID_DEVICE_W - 2 * ANDROID_BEZEL
ANDROID_SCREEN_H = ANDROID_DEVICE_H - 2 * ANDROID_BEZEL


def generate_ios():
    """Generate iPhone device frame with Dynamic Island."""
    frame = Image.new("RGBA", (IOS_DEVICE_W, IOS_DEVICE_H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # Device body (dark grey outer, darker inner)
    fd.rounded_rectangle(
        [0, 0, IOS_DEVICE_W - 1, IOS_DEVICE_H - 1],
        radius=IOS_DEVICE_CORNER_R,
        fill=(30, 30, 30, 255),
    )
    fd.rounded_rectangle(
        [1, 1, IOS_DEVICE_W - 2, IOS_DEVICE_H - 2],
        radius=IOS_DEVICE_CORNER_R - 1,
        fill=(20, 20, 20, 255),
    )

    # Screen cutout (transparent)
    screen_x = IOS_BEZEL
    screen_y = IOS_BEZEL
    cutout = Image.new("L", (IOS_DEVICE_W, IOS_DEVICE_H), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + IOS_SCREEN_W, screen_y + IOS_SCREEN_H],
        radius=IOS_SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # Dynamic Island
    di_x = (IOS_DEVICE_W - IOS_DI_W) // 2
    di_y = screen_y + IOS_DI_TOP
    ImageDraw.Draw(frame).rounded_rectangle(
        [di_x, di_y, di_x + IOS_DI_W, di_y + IOS_DI_H],
        radius=IOS_DI_H // 2,
        fill=(0, 0, 0, 255),
    )

    # Side buttons
    btn_color = (25, 25, 25, 255)
    fd2 = ImageDraw.Draw(frame)
    fd2.rounded_rectangle([IOS_DEVICE_W, 340, IOS_DEVICE_W + 4, 460], radius=2, fill=btn_color)
    fd2.rounded_rectangle([-4, 280, 0, 360], radius=2, fill=btn_color)
    fd2.rounded_rectangle([-4, 380, 0, 460], radius=2, fill=btn_color)
    fd2.rounded_rectangle([-4, 180, 0, 220], radius=2, fill=btn_color)

    out = os.path.join("assets", "device_frame_ios.png")
    os.makedirs("assets", exist_ok=True)
    frame.save(out, "PNG")
    print(f"✓ {out} ({IOS_DEVICE_W}×{IOS_DEVICE_H})")
    print(f"  BEZEL={IOS_BEZEL}, SCREEN_W={IOS_SCREEN_W}, SCREEN_CORNER_R={IOS_SCREEN_CORNER_R}")


def generate_android():
    """Generate Android (Pixel-style) device frame with punch-hole camera."""
    frame = Image.new("RGBA", (ANDROID_DEVICE_W, ANDROID_DEVICE_H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)

    # Device body
    fd.rounded_rectangle(
        [0, 0, ANDROID_DEVICE_W - 1, ANDROID_DEVICE_H - 1],
        radius=ANDROID_DEVICE_CORNER_R,
        fill=(30, 30, 30, 255),
    )
    fd.rounded_rectangle(
        [1, 1, ANDROID_DEVICE_W - 2, ANDROID_DEVICE_H - 2],
        radius=ANDROID_DEVICE_CORNER_R - 1,
        fill=(20, 20, 20, 255),
    )

    # Screen cutout (transparent)
    screen_x = ANDROID_BEZEL
    screen_y = ANDROID_BEZEL
    cutout = Image.new("L", (ANDROID_DEVICE_W, ANDROID_DEVICE_H), 255)
    ImageDraw.Draw(cutout).rounded_rectangle(
        [screen_x, screen_y, screen_x + ANDROID_SCREEN_W, screen_y + ANDROID_SCREEN_H],
        radius=ANDROID_SCREEN_CORNER_R,
        fill=0,
    )
    frame.putalpha(ImageChops.multiply(frame.getchannel("A"), cutout))

    # Camera punch-hole (centered)
    camera_r = 10
    camera_cx = ANDROID_DEVICE_W // 2
    camera_cy = screen_y + 36
    ImageDraw.Draw(frame).ellipse(
        (camera_cx - camera_r, camera_cy - camera_r,
         camera_cx + camera_r, camera_cy + camera_r),
        fill=(20, 20, 20, 200),
    )

    # Side buttons (right side)
    btn_color = (25, 25, 25, 255)
    fd2 = ImageDraw.Draw(frame)
    fd2.rounded_rectangle([ANDROID_DEVICE_W, 340, ANDROID_DEVICE_W + 4, 420], radius=2, fill=btn_color)
    fd2.rounded_rectangle([ANDROID_DEVICE_W, 460, ANDROID_DEVICE_W + 4, 520], radius=2, fill=btn_color)
    fd2.rounded_rectangle([ANDROID_DEVICE_W, 535, ANDROID_DEVICE_W + 4, 595], radius=2, fill=btn_color)

    out = os.path.join("assets", "device_frame_android.png")
    os.makedirs("assets", exist_ok=True)
    frame.save(out, "PNG")
    print(f"✓ {out} ({ANDROID_DEVICE_W}×{ANDROID_DEVICE_H})")
    print(f"  BEZEL={ANDROID_BEZEL}, SCREEN_W={ANDROID_SCREEN_W}, SCREEN_CORNER_R={ANDROID_SCREEN_CORNER_R}")


if __name__ == "__main__":
    generate_ios()
    generate_android()
