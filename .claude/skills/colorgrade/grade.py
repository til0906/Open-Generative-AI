#!/usr/bin/env python3
"""Color-grade photos. Usage: grade.py [--preset NAME] [--strength 0-2] [--letterbox] IN [IN ...] --out DIR"""
import argparse, os, numpy as np
from PIL import Image, ImageFilter, ImageOps

PRESETS = {
    # shadow tint, highlight tint, saturation, contrast, lift, vignette, grain, bloom
    "cinematic": dict(sh=(-0.05, 0.015, 0.05), hi=(0.05, 0.02, -0.04), sat=0.85, con=0.45, lift=0.04, vig=0.35, grain=0.022, bloom=0.5),
    "tealorange": dict(sh=(-0.09, 0.03, 0.09), hi=(0.09, 0.03, -0.07), sat=1.05, con=0.55, lift=0.03, vig=0.35, grain=0.018, bloom=0.4),
    "moody": dict(sh=(-0.03, 0.01, 0.06), hi=(0.01, 0.0, 0.02), sat=0.7, con=0.6, lift=0.06, vig=0.5, grain=0.03, bloom=0.3),
    "warm": dict(sh=(0.02, 0.0, -0.03), hi=(0.07, 0.035, -0.05), sat=1.0, con=0.35, lift=0.03, vig=0.3, grain=0.015, bloom=0.5),
    "film": dict(sh=(0.0, 0.03, 0.02), hi=(0.04, 0.03, -0.02), sat=0.8, con=0.4, lift=0.08, vig=0.3, grain=0.04, bloom=0.3),
    "bw": dict(sh=(0, 0, 0), hi=(0, 0, 0), sat=0.0, con=0.6, lift=0.04, vig=0.45, grain=0.035, bloom=0.3),
}

def grade(im, p, k, letterbox):
    a = np.asarray(im).astype(np.float32) / 255.0
    h, w, _ = a.shape
    s = a * a * (3 - 2 * a)
    a = (1 - p["con"] * k) * a + p["con"] * k * s
    a = p["lift"] + a * (1 - p["lift"] - 0.04)
    L = lambda x: (0.2126 * x[..., 0] + 0.7152 * x[..., 1] + 0.0722 * x[..., 2])[..., None]
    lum = L(a)
    a += k * (np.clip(1 - lum * 1.8, 0, 1) * np.array(p["sh"]) + np.clip((lum - 0.45) * 1.8, 0, 1) * np.array(p["hi"]))
    lum = L(a)
    a = lum + (a - lum) * (1 + (p["sat"] - 1) * min(k, 1.5))
    blur = np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(w / 60))).astype(np.float32) / 255
    a = 1 - (1 - a) * (1 - np.clip(blur - 0.6, 0, 1) * p["bloom"] * k)
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a *= (1 - p["vig"] * k * np.clip(d - 0.45, 0, 1) ** 1.5)[..., None]
    a += np.random.default_rng(7).normal(0, p["grain"] * k, (h, w, 1)).astype(np.float32) * (1 - np.abs(lum - 0.5) * 1.2)
    a = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    if letterbox:
        bar = int(h * 0.06) if h > w else int((h - w / 2.39) / 2)
        if bar > 0:
            a[:bar] = 0; a[-bar:] = 0
    return Image.fromarray(a)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--preset", default="cinematic", choices=PRESETS)
    ap.add_argument("--strength", type=float, default=1.0)
    ap.add_argument("--letterbox", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for f in a.inputs:
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        dst = os.path.join(a.out, f"{os.path.splitext(os.path.basename(f))[0]}_{a.preset}.jpg")
        grade(im, PRESETS[a.preset], a.strength, a.letterbox).save(dst, quality=95)
        print(dst)
