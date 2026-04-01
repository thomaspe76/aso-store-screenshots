# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## What This Is

A Claude Code skill (`aso-store-screenshots`) that guides users through creating high-converting App Store AND Play Store screenshots. Based on [adamlyttleapps/claude-skill-aso-appstore-screenshots](https://github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots), extended with Android/Play Store support.

## Architecture

Four files + two assets make up the skill:

- **SKILL.md** — The skill prompt. Defines a multi-phase workflow: Platform Detection → Benefit Discovery → Screenshot Pairing → Generation. Uses Claude Code's memory system to persist state across conversations. Generation creates a deterministic scaffold via compose.py, then sends it to Nano Banana Pro for AI enhancement. Supports iOS, Android, or both.
- **compose.py** — Pillow-based compositing script. Accepts `--platform ios|android` to switch between App Store (1290×2796) and Play Store (1080×1920) dimensions, device frames, and font fallbacks.
- **generate_frame.py** — Generates two device frame templates: `assets/device_frame_ios.png` (iPhone with Dynamic Island) and `assets/device_frame_android.png` (Pixel-style with punch-hole camera).
- **showcase.py** — Generates side-by-side preview of final screenshots with optional URL footer. Cross-platform font support.
- **assets/device_frame_ios.png** — Pre-rendered iPhone frame template.
- **assets/device_frame_android.png** — Pre-rendered Android/Pixel frame template.

## Running compose.py

```bash
# Requires: pip install Pillow

# Android (Play Store)
python3 compose.py --bg "#3D7A5F" --verb "TRACK" --desc "YOUR DOSES" \
  --screenshot screen.png --output out.png --platform android

# iOS (App Store)
python3 compose.py --bg "#3D7A5F" --verb "TRACK" --desc "YOUR DOSES" \
  --screenshot screen.png --output out.png --platform ios
```

On Linux (no SF Pro font): falls back to Roboto Bold → DejaVu Sans Bold.
On macOS: uses SF Pro Display Black (preferred) with Roboto fallback.

## Key Design Decisions

- **Two-stage generation**: compose.py creates deterministic scaffold, Nano Banana Pro enhances it. Avoids inconsistencies of generating from scratch.
- **Platform-aware**: Single compose.py handles both iOS and Android with correct dimensions, frames, and fonts.
- **Device frames are template images** — not drawn at compose time. Regenerate with `python3 generate_frame.py`.
- **Verb text auto-sizes** to fit canvas width per platform.
- **Crop/resize is mandatory** after every AI generation — raw output is never correct dimensions.
- **Memory is central** — benefits, screenshots, pairings, brand colour, and generation state persist across conversations.
