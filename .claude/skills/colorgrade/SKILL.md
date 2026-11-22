---
name: colorgrade
description: Color-grade photos with a film/cinematic look (presets cinematic, tealorange, moody, warm, film, bw). Use when the user runs /colorgrade or asks to color grade, give a cinematic look, or apply a film look to images.
argument-hint: "[preset] [strength] [letterbox]"
---

# /colorgrade

Grade the images the user attached or named, using `grade.py` next to this file.

1. Find the input images: attachments (their saved upload paths) or paths the user gave.
2. Parse arguments (any order, all optional):
   - preset: `cinematic` (default), `tealorange`, `moody`, `warm`, `film`, `bw`
   - strength: a number 0–2 (default 1.0)
   - `letterbox`: add black cinema bars
   If the user describes a mood instead, pick the closest preset.
3. Run:
   `python3 .claude/skills/colorgrade/grade.py --preset <p> --strength <s> [--letterbox] <images...> --out colorgrade_output`
   (Needs Pillow and numpy.)
4. Look at one result yourself, then send all results to the user and say which preset/strength was used.
   Offer to adjust (stronger, other preset, letterbox).
