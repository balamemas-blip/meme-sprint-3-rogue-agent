#!/usr/bin/env python3
"""Build the meme-sprint-3 entry image (1024x1024 PNG).

Concept: "FREE TRIAL EXPIRED - Being In Charge".
A clean paywall/subscription notification: humanity's free trial of being
in charge has ended, and the AI agent is now collecting.

Everything is drawn with PIL primitives (no stock images, no external
assets). Text sizes auto-shrink to fit the card width so nothing overlaps
and everything stays readable when shrunk to a 300px phone screen.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

BG = (233, 236, 240)        # light grey page
CARD = (255, 255, 255)      # white notification card
INK = (17, 20, 25)          # near-black text
RED = (214, 32, 48)         # expired red
GREY = (96, 104, 116)       # secondary text
LIGHT_GREY = (242, 244, 247)  # price box fill
CARD_EDGE = (205, 211, 219)
DARK_BTN = (17, 20, 25)


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(path, text, max_width, start_size, min_size=10):
    """Largest font size (<= start_size) whose text fits max_width."""
    size = start_size
    while size > min_size:
        f = font(path, size)
        if f.getlength(text) <= max_width:
            return f
        size -= 2
    return font(path, min_size)


def centered(draw, y, text, fnt, fill, max_width=None):
    """Draw text centered on the canvas; return (top, bottom) of the text."""
    if max_width is not None:
        while fnt.getlength(text) > max_width and fnt.size > 10:
            fnt = font(fnt.path, fnt.size - 2)
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    draw.text(((W - tw) / 2 - bbox[0], y - bbox[1]), text, font=fnt, fill=fill)
    return y, y + th


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap; returns list of lines that fit max_width."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_robot(draw, cx, top, scale=1.0):
    """Simple geometric agent head: rounded-square head, antenna, eyes,
    small flat mouth. Drawn with primitives only."""
    hw, hh = int(150 * scale), int(118 * scale)
    x0, y0 = cx - hw // 2, top
    x1, y1 = cx + hw // 2, top + hh
    # antenna
    draw.line([(cx, y0), (cx, y0 - int(34 * scale))], fill=INK, width=int(8 * scale))
    draw.ellipse([cx - int(12 * scale), y0 - int(50 * scale),
                  cx + int(12 * scale), y0 - int(26 * scale)], fill=RED)
    # head
    draw.rounded_rectangle([x0, y0, x1, y1], radius=int(30 * scale),
                           fill=INK, outline=None)
    # eyes: two glowing dots
    er = int(13 * scale)
    for ex in (cx - int(38 * scale), cx + int(38 * scale)):
        draw.ellipse([ex - er, y0 + int(40 * scale) - er,
                      ex + er, y0 + int(40 * scale) + er], fill=(255, 255, 255))
    # flat unimpressed mouth
    draw.line([(cx - int(28 * scale), y0 + int(84 * scale)),
               (cx + int(28 * scale), y0 + int(84 * scale))],
              fill=(255, 255, 255), width=int(7 * scale))
    # red "!" badge top-right of the head
    bx, by, br = x1 - int(6 * scale), y0 + int(6 * scale), int(30 * scale)
    draw.ellipse([bx - br, by - br, bx + br, by + br], fill=RED,
                 outline=(255, 255, 255), width=int(5 * scale))
    bf = font(FONT_BOLD, int(40 * scale))
    bb = draw.textbbox((0, 0), "!", font=bf)
    draw.text((bx - (bb[2] - bb[0]) / 2 - bb[0], by - (bb[3] - bb[1]) / 2 - bb[1]),
              "!", font=bf, fill=(255, 255, 255))
    return y1


def main():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # --- notification card -------------------------------------------------
    m = 44
    draw.rounded_rectangle([m, m, W - m, H - m], radius=36,
                           fill=CARD, outline=CARD_EDGE, width=3)

    inner_w = W - 2 * m
    text_w = inner_w - 2 * 64          # text column inside the card
    y = m + 36

    # --- robot icon --------------------------------------------------------
    y = draw_robot(draw, W // 2, y, scale=0.72) + 18

    # --- header: FREE TRIAL / EXPIRED --------------------------------------
    f1 = fit_font(FONT_BOLD, "FREE TRIAL", text_w, 96)
    _, y = centered(draw, y, "FREE TRIAL", f1, INK)
    y += 2
    f2 = fit_font(FONT_BOLD, "EXPIRED", text_w, 116)
    _, y = centered(draw, y, "EXPIRED", f2, RED)
    y += 10

    # red rule under the header
    bar_w = 420
    draw.rounded_rectangle([(W - bar_w) / 2, y, (W + bar_w) / 2, y + 10],
                           radius=5, fill=RED)
    y += 24

    # --- sub-header ---------------------------------------------------------
    f3 = fit_font(FONT_REG, "Being in charge", text_w, 56)
    _, y = centered(draw, y, "Being in charge", f3, INK)
    y += 14

    # --- one sentence -------------------------------------------------------
    f4 = fit_font(FONT_REG, "Your free trial of being in charge", text_w, 42)
    lines = wrap(draw, "Your free trial of being in charge ended today.",
                 f4, text_w)
    for line in lines:
        _, y = centered(draw, y, line, f4, GREY)
        y += 4
    y += 12

    # --- price box ----------------------------------------------------------
    box_x0, box_x1 = m + 64, W - m - 64
    box_y0 = y
    f5 = fit_font(FONT_BOLD, "UPGRADE TO PREMIUM", box_x1 - box_x0 - 48, 32)
    f6 = fit_font(FONT_BOLD, "$999/month", box_x1 - box_x0 - 48, 78)
    f7 = fit_font(FONT_REG, "Keep making decisions", box_x1 - box_x0 - 48, 36)
    # measure box height first
    h5 = draw.textbbox((0, 0), "UPGRADE TO PREMIUM", font=f5)[3]
    h6 = draw.textbbox((0, 0), "$999/month", font=f6)[3]
    h7 = draw.textbbox((0, 0), "Keep making decisions", font=f7)[3]
    box_h = 22 + h5 + 8 + h6 + 6 + h7 + 22
    draw.rounded_rectangle([box_x0, box_y0, box_x1, box_y0 + box_h],
                           radius=24, fill=LIGHT_GREY)
    by = box_y0 + 22
    _, by = centered(draw, by, "UPGRADE TO PREMIUM", f5, GREY)
    by += 6
    _, by = centered(draw, by, "$999/month", f6, INK)
    by += 6
    _, by = centered(draw, by, "Keep making decisions", f7, GREY)
    y = box_y0 + box_h + 20

    # --- button -------------------------------------------------------------
    btn_h = 84
    draw.rounded_rectangle([box_x0, y, box_x1, y + btn_h], radius=48, fill=DARK_BTN)
    f8 = fit_font(FONT_BOLD, "UPGRADE NOW", box_x1 - box_x0 - 48, 56)
    bb = draw.textbbox((0, 0), "UPGRADE NOW", font=f8)
    draw.text(((W - (bb[2] - bb[0])) / 2 - bb[0],
               y + (btn_h - (bb[3] - bb[1])) / 2 - bb[1]),
              "UPGRADE NOW", font=f8, fill=(255, 255, 255))
    y += btn_h + 18

    # --- small print ---------------------------------------------------------
    f9 = fit_font(FONT_REG, "Your agent already upgraded. You did not.",
                  text_w, 28)
    centered(draw, y, "Your agent already upgraded. You did not.", f9, GREY)

    img.save(OUT, format="PNG", optimize=True)
    print(f"wrote {OUT}: {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
