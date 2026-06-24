"""Generate pixel art sprites for ARIA: Defenders of Duskwall.

Chibi anime ARIA units (48x48), zombies (32x32), base (64x64),
structures (16x16), map tiles (16x16).
"""
from PIL import Image
from pathlib import Path


def px(img, x, y, color):
    """Set a pixel if in bounds."""
    if 0 <= x < img.width and 0 <= y < img.height:
        img.putpixel((x, y), color)


def fill_rect(img, x1, y1, x2, y2, color):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            px(img, x, y, color)


def row(img, y, xs, color):
    for x in xs:
        px(img, x, y, color)


# ============================================================
# ARIA UNITS (48x48 chibi)
# ============================================================

def make_rex():
    """Rex - Vanguard. Heavy red armor, shield+sword, red scarf, stocky."""
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))

    hair = (139, 32, 32, 255)
    hair_l = (176, 48, 48, 255)
    skin = (240, 200, 160, 255)
    skin_s = (212, 168, 120, 255)
    armor = (204, 51, 51, 255)
    armor_l = (224, 85, 85, 255)
    armor_d = (139, 26, 26, 255)
    eye = (64, 224, 255, 255)
    eye_s = (32, 160, 204, 255)
    white = (255, 255, 255, 255)
    dark = (26, 10, 10, 255)
    blush = (255, 153, 153, 255)
    metal = (102, 119, 136, 255)
    metal_l = (136, 153, 170, 255)
    metal_d = (85, 102, 119, 255)
    gold = (204, 153, 51, 255)
    scarf = (255, 68, 68, 255)
    scarf_d = (221, 34, 34, 255)
    outline = (60, 20, 20, 255)

    # === HUGE HEAD (rows 2-21, ~20px tall = 42% of sprite) ===
    # Hair top
    for x in range(14, 34): px(img, x, 2, hair)
    for x in range(13, 35): px(img, x, 3, hair)
    for x in range(12, 36): px(img, x, 4, hair)
    for x in range(12, 36): px(img, x, 5, hair)
    for x in range(12, 36): px(img, x, 6, hair)
    # Hair highlights
    for x in [16, 17, 18, 28, 29, 30]: px(img, x, 3, hair_l)
    for x in [15, 16, 17, 29, 30, 31]: px(img, x, 4, hair_l)

    # Face (wide)
    for y in range(7, 18):
        for x in range(13, 35): px(img, x, y, skin)
    # Side hair
    for y in range(7, 16):
        px(img, 11, y, hair); px(img, 12, y, hair)
        px(img, 35, y, hair); px(img, 36, y, hair)
    # Chin
    for x in range(15, 33): px(img, x, 18, skin_s)

    # BIG EYES (5x4 each)
    for y in range(10, 14):
        for x in range(15, 20): px(img, x, y, white)
        for x in range(28, 33): px(img, x, y, white)
    # Left eye
    px(img, 16, 10, eye); px(img, 17, 10, eye); px(img, 18, 10, eye)
    px(img, 16, 11, eye); px(img, 17, 11, eye_s); px(img, 18, 11, eye_s)
    px(img, 16, 12, dark); px(img, 17, 12, dark); px(img, 18, 12, dark)
    px(img, 15, 11, dark)
    px(img, 18, 10, (170, 238, 255, 255))  # shine
    px(img, 17, 10, (200, 245, 255, 255))  # shine
    # Right eye
    px(img, 29, 10, eye); px(img, 30, 10, eye); px(img, 31, 10, eye)
    px(img, 29, 11, eye); px(img, 30, 11, eye_s); px(img, 31, 11, eye_s)
    px(img, 29, 12, dark); px(img, 30, 12, dark); px(img, 31, 12, dark)
    px(img, 32, 11, dark)
    px(img, 31, 10, (170, 238, 255, 255))
    px(img, 30, 10, (200, 245, 255, 255))

    # Blush
    for x in [15, 16, 17]: px(img, x, 14, blush)
    for x in [30, 31, 32]: px(img, x, 14, blush)

    # Mouth (small determined)
    px(img, 23, 16, (224, 128, 128, 255)); px(img, 24, 16, (224, 128, 128, 255))

    # === TINY BODY (rows 19-32) ===
    # Neck
    px(img, 23, 19, skin); px(img, 24, 19, skin)

    # Compact torso armor
    fill_rect(img, 21, 20, 26, 27, armor)
    px(img, 22, 21, armor_l); px(img, 23, 21, armor_l); px(img, 24, 21, armor_l); px(img, 25, 21, armor_l)
    px(img, 23, 22, armor_l); px(img, 24, 22, armor_l)
    for x in range(21, 27): px(img, x, 28, armor_d)

    # Shoulder plates
    fill_rect(img, 17, 20, 20, 22, armor)
    fill_rect(img, 27, 20, 30, 22, armor)
    px(img, 18, 20, armor_l); px(img, 19, 20, armor_l)
    px(img, 28, 20, armor_l); px(img, 29, 20, armor_l)

    # Stubby arms
    for y in range(23, 27):
        px(img, 19, y, armor); px(img, 20, y, armor_d)
        px(img, 27, y, armor_d); px(img, 28, y, armor)
    px(img, 19, 27, skin); px(img, 28, 27, skin)

    # === OVERSIZED SHIELD (left, 14px tall) ===
    fill_rect(img, 4, 16, 18, 32, metal)
    for y in range(16, 33): px(img, 4, y, metal_d); px(img, 18, y, metal_d)
    for x in range(4, 19): px(img, x, 16, metal_d); px(img, x, 32, metal_d)
    fill_rect(img, 7, 19, 10, 24, metal_l)
    # Shield emblem (red cross)
    fill_rect(img, 10, 24, 12, 28, armor)
    px(img, 9, 25, armor); px(img, 13, 25, armor)
    px(img, 9, 26, armor); px(img, 13, 26, armor)
    px(img, 9, 27, armor); px(img, 13, 27, armor)

    # === OVERSIZED SWORD (right, 20px tall) ===
    px(img, 30, 8, white); px(img, 30, 9, white)
    px(img, 30, 10, (221, 221, 238, 255)); px(img, 30, 11, (221, 221, 238, 255))
    for y in range(12, 26): px(img, 30, y, metal_l)
    px(img, 31, 13, metal); px(img, 31, 14, metal)  # blade width
    # Crossguard
    for x in range(28, 33): px(img, x, 26, gold)
    px(img, 29, 27, gold); px(img, 30, 27, gold); px(img, 31, 27, gold)

    # Scarf (flowing)
    px(img, 20, 19, scarf); px(img, 19, 20, scarf); px(img, 18, 20, scarf)
    px(img, 17, 21, scarf); px(img, 16, 22, scarf_d)
    px(img, 15, 23, scarf_d); px(img, 14, 24, scarf_d)
    px(img, 13, 25, scarf_d)

    # Short legs
    for y in range(29, 34):
        px(img, 22, y, armor); px(img, 21, y, armor_d)
        px(img, 25, y, armor); px(img, 26, y, armor_d)

    # Boots
    fill_rect(img, 20, 34, 23, 36, armor_d)
    fill_rect(img, 24, 34, 27, 36, armor_d)
    px(img, 21, 34, armor); px(img, 25, 34, armor)

    return img


def make_aurora():
    """Aurora - Striker. Gold armor, sniper rifle, visor, sleek."""
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))

    hair = (230, 200, 120, 255)
    hair_l = (245, 225, 160, 255)
    skin = (240, 200, 160, 255)
    skin_s = (212, 168, 120, 255)
    armor = (230, 184, 50, 255)
    armor_l = (245, 210, 100, 255)
    armor_d = (176, 136, 32, 255)
    eye = (64, 224, 255, 255)
    eye_s = (32, 160, 204, 255)
    white = (255, 255, 255, 255)
    dark = (26, 10, 10, 255)
    blush = (255, 180, 180, 255)
    metal = (80, 80, 90, 255)
    metal_l = (120, 120, 130, 255)
    visor = (200, 50, 50, 255)

    # === HUGE HEAD (rows 2-18) ===
    for x in range(14, 34): px(img, x, 2, hair)
    for x in range(13, 35): px(img, x, 3, hair)
    for x in range(12, 36): px(img, x, 4, hair)
    for x in range(12, 36): px(img, x, 5, hair)
    for x in range(12, 36): px(img, x, 6, hair)
    for x in [16, 17, 18, 28, 29, 30]: px(img, x, 3, hair_l)
    for x in [15, 16, 29, 30]: px(img, x, 4, hair_l)
    # Long hair sides
    for y in range(7, 22):
        px(img, 11, y, hair); px(img, 12, y, hair)
        px(img, 35, y, hair); px(img, 36, y, hair)

    # Face
    for y in range(7, 18):
        for x in range(13, 35): px(img, x, y, skin)
    for x in range(15, 33): px(img, x, 18, skin_s)

    # BIG EYES (5x4)
    for y in range(10, 14):
        for x in range(15, 20): px(img, x, y, white)
        for x in range(28, 33): px(img, x, y, white)
    px(img, 16, 10, eye); px(img, 17, 10, eye); px(img, 18, 10, eye)
    px(img, 16, 11, eye); px(img, 17, 11, eye_s); px(img, 18, 11, eye_s)
    px(img, 16, 12, dark); px(img, 17, 12, dark); px(img, 18, 12, dark)
    px(img, 15, 11, dark)
    px(img, 18, 10, (170, 238, 255, 255)); px(img, 17, 10, (200, 245, 255, 255))
    px(img, 29, 10, eye); px(img, 30, 10, eye); px(img, 31, 10, eye)
    px(img, 29, 11, eye); px(img, 30, 11, eye_s); px(img, 31, 11, eye_s)
    px(img, 29, 12, dark); px(img, 30, 12, dark); px(img, 31, 12, dark)
    px(img, 32, 11, dark)
    px(img, 31, 10, (170, 238, 255, 255)); px(img, 30, 10, (200, 245, 255, 255))

    # Visor (over right eye, bright)
    for x in range(27, 34): px(img, x, 9, visor)
    px(img, 27, 10, visor); px(img, 33, 10, visor)

    # Blush
    for x in [15, 16, 17]: px(img, x, 14, blush)
    for x in [30, 31, 32]: px(img, x, 14, blush)
    # Focused mouth
    px(img, 23, 16, (200, 100, 100, 255)); px(img, 24, 16, (200, 100, 100, 255))

    # === TINY BODY ===
    px(img, 23, 19, skin); px(img, 24, 19, skin)
    fill_rect(img, 21, 20, 26, 27, armor)
    px(img, 22, 21, armor_l); px(img, 23, 21, armor_l); px(img, 24, 21, armor_l); px(img, 25, 21, armor_l)
    for x in range(21, 27): px(img, x, 28, armor_d)

    # Arms
    for y in range(20, 26):
        px(img, 19, y, armor); px(img, 20, y, armor)
        px(img, 27, y, armor); px(img, 28, y, armor)
    px(img, 19, 26, skin); px(img, 28, 26, skin)

    # === MASSIVE SNIPER RIFLE (right side, 28px tall!) ===
    # Barrel (long, bright so it's visible)
    for y in range(4, 28):
        px(img, 38, y, metal_l); px(img, 39, y, metal)
    # Barrel tip (bright)
    px(img, 38, 3, (200, 200, 210, 255)); px(img, 39, 3, (200, 200, 210, 255))
    # Scope (bright red, eye-catching)
    fill_rect(img, 37, 10, 40, 13, visor)
    px(img, 37, 11, (255, 100, 100, 255)); px(img, 40, 11, (255, 100, 100, 255))
    # Body of rifle (wider section)
    fill_rect(img, 37, 18, 41, 24, metal)
    px(img, 38, 19, metal_l); px(img, 39, 19, metal_l)
    # Stock
    fill_rect(img, 37, 25, 40, 30, metal)
    px(img, 38, 25, metal_l)
    # Muzzle flash hint
    px(img, 38, 2, (255, 255, 200, 180)); px(img, 39, 2, (255, 200, 100, 150))

    # Short legs
    for y in range(29, 34):
        px(img, 22, y, armor); px(img, 21, y, armor_d)
        px(img, 25, y, armor); px(img, 26, y, armor_d)
    fill_rect(img, 20, 34, 23, 36, armor_d)
    fill_rect(img, 24, 34, 27, 36, armor_d)

    return img


def make_lily():
    """Lily - Medic. Green coat, healing hands, gentle pose, pink hair."""
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))

    hair = (220, 140, 180, 255)
    hair_l = (240, 170, 200, 255)
    skin = (240, 200, 160, 255)
    skin_s = (212, 168, 120, 255)
    coat = (85, 204, 102, 255)
    coat_l = (120, 224, 140, 255)
    coat_d = (51, 136, 68, 255)
    white_u = (230, 230, 240, 255)
    eye = (64, 224, 255, 255)
    eye_s = (32, 160, 204, 255)
    white = (255, 255, 255, 255)
    dark = (26, 10, 10, 255)
    blush = (255, 170, 170, 255)
    cross = (255, 255, 255, 255)
    glow = (100, 255, 150, 128)

    # === HUGE HEAD ===
    for x in range(14, 34): px(img, x, 2, hair)
    for x in range(13, 35): px(img, x, 3, hair)
    for x in range(12, 36): px(img, x, 4, hair)
    for x in range(12, 36): px(img, x, 5, hair)
    for x in range(12, 36): px(img, x, 6, hair)
    for x in [16, 17, 28, 29]: px(img, x, 3, hair_l)
    for x in [15, 16, 29, 30]: px(img, x, 4, hair_l)
    # Long pink hair
    for y in range(7, 24):
        px(img, 11, y, hair); px(img, 12, y, hair)
        px(img, 35, y, hair); px(img, 36, y, hair)

    # Face
    for y in range(7, 18):
        for x in range(13, 35): px(img, x, y, skin)
    for x in range(15, 33): px(img, x, 18, skin_s)

    # BIG EYES
    for y in range(10, 14):
        for x in range(15, 20): px(img, x, y, white)
        for x in range(28, 33): px(img, x, y, white)
    px(img, 16, 10, eye); px(img, 17, 10, eye); px(img, 18, 10, eye)
    px(img, 16, 11, eye); px(img, 17, 11, eye_s); px(img, 18, 11, eye_s)
    px(img, 16, 12, dark); px(img, 17, 12, dark); px(img, 18, 12, dark)
    px(img, 15, 11, dark)
    px(img, 18, 10, (170, 238, 255, 255)); px(img, 17, 10, (200, 245, 255, 255))
    px(img, 29, 10, eye); px(img, 30, 10, eye); px(img, 31, 10, eye)
    px(img, 29, 11, eye); px(img, 30, 11, eye_s); px(img, 31, 11, eye_s)
    px(img, 29, 12, dark); px(img, 30, 12, dark); px(img, 31, 12, dark)
    px(img, 32, 11, dark)
    px(img, 31, 10, (170, 238, 255, 255)); px(img, 30, 10, (200, 245, 255, 255))

    # Blush + gentle smile
    for x in [15, 16, 17]: px(img, x, 14, blush)
    for x in [30, 31, 32]: px(img, x, 14, blush)
    for x in [22, 23, 24, 25]: px(img, x, 16, (224, 128, 128, 255))

    # === TINY BODY ===
    px(img, 23, 19, skin); px(img, 24, 19, skin)
    # White uniform + green coat
    fill_rect(img, 21, 20, 26, 27, white_u)
    fill_rect(img, 19, 20, 20, 29, coat)
    fill_rect(img, 27, 20, 28, 29, coat)
    px(img, 19, 20, coat_l); px(img, 27, 20, coat_l)
    fill_rect(img, 18, 28, 29, 30, coat)
    for x in range(18, 30): px(img, x, 30, coat_d)
    # Cross emblem
    px(img, 23, 22, cross); px(img, 24, 22, cross)
    px(img, 22, 23, cross); px(img, 23, 23, cross); px(img, 24, 23, cross); px(img, 25, 23, cross)
    px(img, 23, 24, cross); px(img, 24, 24, cross)

    # Arms
    for y in range(20, 26):
        px(img, 17, y, coat); px(img, 18, y, coat)
        px(img, 29, y, coat); px(img, 30, y, coat)

    # Left hand -- HEALING GLOW (bright, visible)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            px(img, 15 + dx, 25 + dy, glow)
    fill_rect(img, 14, 24, 16, 26, (100, 255, 150, 200))
    px(img, 15, 25, skin)

    # Right hand -- PISTOL (oversized for visibility)
    px(img, 31, 25, skin)
    pistol = (100, 100, 115, 255)
    pistol_l = (140, 140, 155, 255)
    fill_rect(img, 32, 22, 34, 26, pistol)  # gun body
    px(img, 33, 22, pistol_l); px(img, 33, 23, pistol_l)
    fill_rect(img, 35, 23, 38, 25, pistol)  # barrel
    px(img, 35, 23, pistol_l); px(img, 36, 23, pistol_l)
    px(img, 39, 24, (255, 200, 100, 200))  # muzzle flash hint

    # Short legs
    for y in range(31, 35):
        px(img, 22, y, white_u); px(img, 25, y, white_u)
    fill_rect(img, 21, 35, 23, 37, coat_d)
    fill_rect(img, 24, 35, 26, 37, coat_d)

    return img


def make_hana():
    """Hana - Architect. Blue jumpsuit, goggles, wrench, tool belt."""
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))

    hair = (139, 90, 50, 255)
    hair_l = (170, 120, 70, 255)
    skin = (240, 200, 160, 255)
    skin_s = (212, 168, 120, 255)
    suit = (85, 153, 221, 255)
    suit_l = (120, 180, 240, 255)
    suit_d = (51, 102, 153, 255)
    eye = (64, 224, 255, 255)
    eye_s = (32, 160, 204, 255)
    white = (255, 255, 255, 255)
    dark = (26, 10, 10, 255)
    blush = (255, 170, 170, 255)
    goggle = (200, 180, 50, 255)
    goggle_lens = (150, 220, 255, 255)
    belt = (139, 100, 60, 255)
    metal = (160, 160, 170, 255)
    metal_l = (190, 190, 200, 255)
    metal_d = (120, 120, 130, 255)

    # === HUGE HEAD ===
    for x in range(14, 34): px(img, x, 2, hair)
    for x in range(13, 35): px(img, x, 3, hair)
    for x in range(12, 36): px(img, x, 4, hair)
    for x in range(12, 36): px(img, x, 5, hair)
    for x in range(12, 36): px(img, x, 6, hair)
    for x in [16, 17, 28, 29]: px(img, x, 3, hair_l)
    for x in [15, 16, 29, 30]: px(img, x, 4, hair_l)
    # Ponytail (right side, long)
    for y in range(7, 26):
        px(img, 36, y, hair); px(img, 37, y, hair)
    for y in range(9, 24):
        px(img, 38, y, hair)
    # Side hair
    for y in range(7, 14):
        px(img, 12, y, hair)
        px(img, 35, y, hair)

    # Goggles (bright, on forehead)
    for x in range(14, 34): px(img, x, 6, goggle)
    for x in range(14, 34): px(img, x, 7, goggle)
    fill_rect(img, 16, 6, 19, 7, goggle_lens)
    fill_rect(img, 28, 6, 31, 7, goggle_lens)

    # Face
    for y in range(8, 18):
        for x in range(13, 35): px(img, x, y, skin)
    for x in range(15, 33): px(img, x, 18, skin_s)

    # BIG EYES
    for y in range(10, 14):
        for x in range(15, 20): px(img, x, y, white)
        for x in range(28, 33): px(img, x, y, white)
    px(img, 16, 10, eye); px(img, 17, 10, eye); px(img, 18, 10, eye)
    px(img, 16, 11, eye); px(img, 17, 11, eye_s); px(img, 18, 11, eye_s)
    px(img, 16, 12, dark); px(img, 17, 12, dark); px(img, 18, 12, dark)
    px(img, 15, 11, dark)
    px(img, 18, 10, (170, 238, 255, 255)); px(img, 17, 10, (200, 245, 255, 255))
    px(img, 29, 10, eye); px(img, 30, 10, eye); px(img, 31, 10, eye)
    px(img, 29, 11, eye); px(img, 30, 11, eye_s); px(img, 31, 11, eye_s)
    px(img, 29, 12, dark); px(img, 30, 12, dark); px(img, 31, 12, dark)
    px(img, 32, 11, dark)
    px(img, 31, 10, (170, 238, 255, 255)); px(img, 30, 10, (200, 245, 255, 255))

    # Blush + confident grin
    for x in [15, 16, 17]: px(img, x, 14, blush)
    for x in [30, 31, 32]: px(img, x, 14, blush)
    for x in [22, 23, 24, 25]: px(img, x, 16, (224, 128, 128, 255))
    px(img, 25, 16, (200, 100, 100, 255))

    # === TINY BODY ===
    px(img, 23, 19, skin); px(img, 24, 19, skin)
    fill_rect(img, 21, 20, 26, 27, suit)
    px(img, 22, 21, suit_l); px(img, 23, 21, suit_l); px(img, 24, 21, suit_l); px(img, 25, 21, suit_l)
    # Tool belt
    for x in range(20, 27): px(img, x, 27, belt)
    px(img, 21, 27, goggle); px(img, 25, 27, goggle)

    # Arms
    for y in range(20, 26):
        px(img, 19, y, suit); px(img, 20, y, suit)
        px(img, 27, y, suit); px(img, 28, y, suit)
    px(img, 19, 26, skin); px(img, 28, 26, skin)

    # === OVERSIZED WRENCH (right, 22px tall!) ===
    # Handle
    for y in range(10, 28): px(img, 30, y, metal); px(img, 31, y, metal)
    px(img, 30, 11, metal_l); px(img, 31, 11, metal_l)
    # Wrench head (top, big jaw)
    fill_rect(img, 28, 6, 33, 10, metal)
    px(img, 29, 7, metal_l); px(img, 30, 7, metal_l); px(img, 31, 7, metal_l)
    px(img, 30, 6, metal_l); px(img, 31, 6, metal_l)
    # Jaw opening
    px(img, 30, 8, (40, 40, 50, 255)); px(img, 31, 8, (40, 40, 50, 255))

    # Left hand -- PISTOL (visible)
    px(img, 17, 25, skin)
    pistol = (100, 100, 115, 255)
    pistol_l = (140, 140, 155, 255)
    fill_rect(img, 13, 23, 16, 26, pistol)
    px(img, 14, 23, pistol_l); px(img, 15, 23, pistol_l)
    fill_rect(img, 10, 24, 12, 25, pistol)  # barrel
    px(img, 10, 24, pistol_l)

    # Short legs
    for y in range(28, 34):
        px(img, 22, y, suit); px(img, 21, y, suit_d)
        px(img, 25, y, suit); px(img, 26, y, suit_d)
    fill_rect(img, 20, 34, 23, 36, suit_d)
    fill_rect(img, 24, 34, 27, 36, suit_d)

    return img


# ============================================================
# ENEMIES
# ============================================================

def make_zombie():
    """Zombie - 32x32. Gray-green, torn clothes, red eyes, shambling."""
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))

    flesh = (102, 119, 85, 255)
    flesh_d = (80, 95, 65, 255)
    flesh_l = (120, 140, 100, 255)
    cloth = (90, 75, 60, 255)
    cloth_d = (60, 50, 40, 255)
    eye = (255, 50, 50, 255)
    dark = (30, 30, 20, 255)
    bone = (200, 190, 170, 255)

    # Head
    for x in range(11, 21): px(img, x, 3, flesh_d)
    for y in range(4, 10):
        for x in range(10, 22): px(img, x, y, flesh)
    # Uneven head shape
    px(img, 10, 5, flesh_d); px(img, 21, 4, flesh_d)

    # Eyes (glowing red, asymmetric)
    px(img, 13, 6, eye); px(img, 14, 6, eye)
    px(img, 18, 6, eye); px(img, 19, 7, eye)  # droopy right eye
    px(img, 13, 7, dark); px(img, 14, 7, dark)

    # Mouth (jagged)
    for x in [12, 13, 15, 17, 19]: px(img, x, 9, dark)

    # Neck
    px(img, 15, 10, flesh); px(img, 16, 10, flesh)

    # Torso (torn shirt)
    for y in range(11, 20):
        for x in range(11, 21): px(img, x, y, cloth)
    # Torn edges
    px(img, 11, 13, (0, 0, 0, 0)); px(img, 20, 15, (0, 0, 0, 0))
    px(img, 12, 12, flesh); px(img, 19, 14, flesh)  # exposed flesh
    px(img, 15, 16, bone)  # exposed rib

    # Arms (asymmetric - one reaching forward)
    for y in range(12, 19):
        px(img, 9, y, flesh); px(img, 10, y, flesh_d)
    # Right arm reaching
    for y in range(12, 17):
        px(img, 21, y, flesh); px(img, 22, y, flesh_d)
    px(img, 23, 14, flesh); px(img, 24, 14, flesh)
    px(img, 25, 13, flesh)  # reaching hand

    # Legs (shambling, one forward)
    for y in range(20, 27):
        px(img, 12, y, cloth); px(img, 13, y, cloth_d)
        px(img, 17, y, cloth); px(img, 18, y, cloth_d)
    # Left leg forward
    px(img, 11, 25, cloth); px(img, 12, 26, cloth)

    # Feet
    px(img, 11, 27, cloth_d); px(img, 12, 27, cloth_d); px(img, 13, 27, cloth_d)
    px(img, 17, 27, cloth_d); px(img, 18, 27, cloth_d); px(img, 19, 27, cloth_d)

    return img


# ============================================================
# BASE (64x64)
# ============================================================

def make_base():
    """Base - 64x64. Fortified bunker, antenna, warm glow."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))

    metal = (100, 105, 115, 255)
    metal_l = (130, 135, 145, 255)
    metal_d = (70, 75, 85, 255)
    wall = (80, 85, 95, 255)
    door = (60, 65, 75, 255)
    glow = (255, 200, 100, 200)
    glow_d = (200, 150, 50, 150)
    roof = (90, 95, 105, 255)
    antenna = (150, 150, 160, 255)
    red_light = (255, 50, 50, 255)
    emblem = (180, 60, 60, 255)

    # Antenna
    for y in range(5, 18): px(img, 32, y, antenna)
    px(img, 31, 5, antenna); px(img, 33, 5, antenna)
    px(img, 32, 4, red_light)

    # Roof
    fill_rect(img, 14, 18, 49, 22, roof)
    for x in range(14, 50): px(img, x, 18, metal_l)

    # Main building
    fill_rect(img, 14, 23, 49, 50, wall)
    # Side walls darker
    for y in range(23, 51):
        px(img, 14, y, metal_d); px(img, 15, y, metal_d)
        px(img, 48, y, metal_d); px(img, 49, y, metal_d)

    # Reinforcement plates
    fill_rect(img, 18, 25, 22, 32, metal)
    fill_rect(img, 41, 25, 45, 32, metal)
    px(img, 19, 26, metal_l); px(img, 20, 26, metal_l)
    px(img, 42, 26, metal_l); px(img, 43, 26, metal_l)

    # Door (center)
    fill_rect(img, 27, 35, 36, 50, door)
    fill_rect(img, 28, 36, 35, 49, metal_d)
    # Door handle
    px(img, 34, 42, metal_l); px(img, 34, 43, metal_l)

    # Windows with warm glow
    fill_rect(img, 19, 36, 24, 40, glow)
    fill_rect(img, 39, 36, 44, 40, glow)
    px(img, 20, 37, glow_d); px(img, 40, 37, glow_d)

    # Emblem above door (shield shape)
    px(img, 31, 28, emblem); px(img, 32, 28, emblem)
    for x in range(30, 34): px(img, x, 29, emblem)
    for x in range(30, 34): px(img, x, 30, emblem)
    px(img, 31, 31, emblem); px(img, 32, 31, emblem)
    # D letter
    px(img, 31, 29, metal_l); px(img, 32, 29, metal_l)

    # Foundation
    fill_rect(img, 12, 51, 51, 54, metal_d)
    for x in range(12, 52): px(img, x, 51, metal)

    # Sandbags around base
    for x in range(10, 54):
        if x % 4 < 3:
            px(img, x, 55, (180, 160, 120, 255))
            px(img, x, 56, (160, 140, 100, 255))

    return img


# ============================================================
# STRUCTURES (16x16)
# ============================================================

def make_wall():
    """Wall - 16x16. Rusted corrugated metal sheet."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    rust = (139, 85, 51, 255)
    rust_l = (170, 110, 70, 255)
    rust_d = (100, 60, 35, 255)
    metal = (120, 120, 130, 255)
    rivet = (160, 160, 170, 255)

    # Main sheet
    fill_rect(img, 2, 1, 13, 14, metal)
    # Corrugation lines
    for y in range(1, 15):
        px(img, 5, y, rust_d)
        px(img, 10, y, rust_d)
    # Rust patches
    fill_rect(img, 3, 8, 5, 11, rust)
    fill_rect(img, 9, 3, 12, 5, rust)
    px(img, 7, 12, rust_l); px(img, 8, 12, rust_l)
    # Rivets
    px(img, 3, 2, rivet); px(img, 12, 2, rivet)
    px(img, 3, 13, rivet); px(img, 12, 13, rivet)
    # Posts
    fill_rect(img, 1, 0, 2, 15, rust_d)
    fill_rect(img, 13, 0, 14, 15, rust_d)

    return img


def make_barricade():
    """Barricade - 16x16. Sandbags with scrap metal."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    sand = (180, 160, 120, 255)
    sand_d = (150, 130, 95, 255)
    sand_l = (200, 180, 145, 255)
    metal = (100, 100, 110, 255)

    # Bottom row sandbags
    for x in range(1, 15):
        px(img, x, 13, sand_d)
        px(img, x, 12, sand)
        px(img, x, 11, sand_l)
    # Middle row
    for x in range(2, 14):
        px(img, x, 10, sand_d)
        px(img, x, 9, sand)
        px(img, x, 8, sand_l)
    # Top row (fewer)
    for x in range(3, 13):
        px(img, x, 7, sand_d)
        px(img, x, 6, sand)
    # Bag separations
    for y in [8, 9, 10, 11, 12, 13]:
        px(img, 5, y, sand_d)
        px(img, 10, y, sand_d)
    # Scrap metal on top
    fill_rect(img, 4, 3, 11, 5, metal)
    px(img, 6, 3, (120, 120, 130, 255))
    px(img, 9, 4, (80, 80, 90, 255))

    return img


# ============================================================
# MAP TILES (16x16)
# ============================================================

def make_dirt():
    img = Image.new("RGBA", (16, 16), (90, 74, 55, 255))
    import random
    random.seed(42)
    for _ in range(20):
        x, y = random.randint(0, 15), random.randint(0, 15)
        v = random.randint(-15, 15)
        px(img, x, y, (90 + v, 74 + v, 55 + v, 255))
    # Cracks
    for x in [3, 4, 5]: px(img, x, 7, (70, 55, 40, 255))
    for x in [9, 10, 11, 12]: px(img, x, 12, (70, 55, 40, 255))
    px(img, 5, 8, (70, 55, 40, 255))
    return img


def make_dead_grass():
    img = Image.new("RGBA", (16, 16), (90, 74, 55, 255))
    grass = (155, 139, 74, 255)
    grass_d = (130, 115, 60, 255)
    # Grass tufts
    for pos in [(3, 4), (8, 2), (12, 7), (5, 12), (1, 9), (14, 13)]:
        px(img, pos[0], pos[1], grass)
        px(img, pos[0], pos[1] - 1, grass_d)
        px(img, pos[0] + 1, pos[1], grass_d)
    return img


def make_rubble():
    img = Image.new("RGBA", (16, 16), (90, 74, 55, 255))
    rock = (130, 130, 125, 255)
    rock_d = (100, 100, 95, 255)
    rock_l = (155, 155, 150, 255)
    # Scattered rocks
    fill_rect(img, 2, 10, 5, 13, rock)
    px(img, 3, 10, rock_l); px(img, 4, 11, rock_d)
    fill_rect(img, 8, 7, 11, 10, rock)
    px(img, 9, 7, rock_l)
    fill_rect(img, 12, 12, 14, 14, rock_d)
    px(img, 5, 5, rock); px(img, 6, 5, rock_d)
    return img


def make_road_cracked():
    img = Image.new("RGBA", (16, 16), (70, 70, 75, 255))
    crack = (45, 45, 50, 255)
    mark = (90, 90, 60, 255)
    # Cracks
    for p in [(3, 0), (4, 1), (4, 2), (5, 3), (5, 4), (6, 5), (6, 6), (7, 7)]:
        px(img, p[0], p[1], crack)
    for p in [(10, 9), (11, 10), (11, 11), (12, 12), (13, 13), (13, 14), (14, 15)]:
        px(img, p[0], p[1], crack)
    # Faded road marking
    for y in range(0, 16, 4):
        px(img, 8, y, mark); px(img, 8, y + 1, mark)
    return img


def make_rust_metal():
    img = Image.new("RGBA", (16, 16), (90, 74, 55, 255))
    rust = (139, 85, 51, 255)
    rust_d = (110, 65, 35, 255)
    # Metal scraps
    fill_rect(img, 2, 8, 7, 11, rust)
    px(img, 3, 8, rust_d); px(img, 6, 10, rust_d)
    fill_rect(img, 10, 3, 13, 6, rust)
    px(img, 11, 4, rust_d)
    px(img, 8, 13, rust); px(img, 9, 13, rust)
    return img


def make_dead_tree():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    trunk = (80, 60, 40, 255)
    trunk_d = (60, 45, 30, 255)
    # Trunk
    for y in range(5, 15):
        px(img, 7, y, trunk); px(img, 8, y, trunk_d)
    # Branches
    px(img, 6, 5, trunk); px(img, 5, 4, trunk); px(img, 4, 3, trunk)
    px(img, 9, 5, trunk); px(img, 10, 4, trunk); px(img, 11, 3, trunk)
    px(img, 6, 7, trunk); px(img, 5, 6, trunk)
    px(img, 9, 8, trunk); px(img, 10, 7, trunk); px(img, 11, 7, trunk)
    return img


def make_bridge_h():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    plank = (140, 110, 70, 255)
    plank_d = (110, 85, 50, 255)
    rope = (100, 80, 50, 255)
    # Planks (horizontal)
    for y in range(4, 12):
        for x in range(0, 16):
            px(img, x, y, plank if (y % 2 == 0) else plank_d)
    # Rope edges
    for x in range(0, 16):
        px(img, x, 3, rope); px(img, x, 12, rope)
    # Nail details
    for x in [2, 6, 10, 14]:
        px(img, x, 5, (80, 80, 90, 255))
        px(img, x, 10, (80, 80, 90, 255))
    return img


def make_bridge_v():
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    plank = (140, 110, 70, 255)
    plank_d = (110, 85, 50, 255)
    rope = (100, 80, 50, 255)
    # Planks (vertical)
    for x in range(4, 12):
        for y in range(0, 16):
            px(img, x, y, plank if (x % 2 == 0) else plank_d)
    # Rope edges
    for y in range(0, 16):
        px(img, 3, y, rope); px(img, 12, y, rope)
    # Nails
    for y in [2, 6, 10, 14]:
        px(img, 5, y, (80, 80, 90, 255))
        px(img, 10, y, (80, 80, 90, 255))
    return img


# ============================================================
# GENERATE ALL
# ============================================================

def main():
    base_dir = Path(__file__).parent / "godot" / "assets"

    assets = {
        "aria/rex_sprite.png": make_rex(),
        "aria/aurora_sprite.png": make_aurora(),
        "aria/lily_sprite.png": make_lily(),
        "aria/hana_sprite.png": make_hana(),
        "enemies/zombie_sprite.png": make_zombie(),
        "structures/base.png": make_base(),
        "structures/wall.png": make_wall(),
        "structures/barricade.png": make_barricade(),
        "tiles/dirt.png": make_dirt(),
        "tiles/dead_grass.png": make_dead_grass(),
        "tiles/rubble.png": make_rubble(),
        "tiles/road_cracked.png": make_road_cracked(),
        "tiles/rust_metal.png": make_rust_metal(),
        "tiles/dead_tree.png": make_dead_tree(),
        "tiles/bridge_h.png": make_bridge_h(),
        "tiles/bridge_v.png": make_bridge_v(),
    }

    for path, img in assets.items():
        out = base_dir / path
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(out))
        print(f"  {out.relative_to(base_dir)}  ({img.width}x{img.height})")

    print(f"\nGenerated {len(assets)} sprites.")


if __name__ == "__main__":
    main()
