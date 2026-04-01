# ARIA Character Reference Sheet Pipeline

**Date:** 2026-04-01
**Status:** Approved
**Model:** Pony Diffusion V6 XL (SDXL base)
**Tool:** ComfyUI + BiRefNet node
**Hardware:** NVIDIA RTX 4060 (8GB VRAM)

---

## Overview

Generate each ARIA character as a single reference sheet image containing a portrait and 5 chibi views. This ensures consistent hair color, eye color, outfit, armor, and weapons across all asset types since they come from the same generation.

Replaces the current approach of generating portraits and sprites separately (which caused inconsistencies in hair color, skin tone, and equipment across Anything V5 generations).

---

## Layout

```
+---------------------------+---------------------------+
|                           |   Front    |    Back      |
|                           |   chibi    |    chibi     |
|      CHARACTER            |------------|--------------|
|      Portrait             |   Left     |    Right     |
|      (upper body)         |   chibi    |    chibi     |
|                           |------------|--------------|
|                           |      Dead chibi           |
|                           |      (centered)           |
+---------------------------+---------------------------+
        ~550px                      ~986px
```

- Left column: large upper-body portrait (briefing card)
- Right top: 2x2 grid of directional chibi views (front, back, left, right)
- Right bottom: single dead/offline chibi (centered)

---

## Generation Parameters

| Parameter | Value |
|-----------|-------|
| Model | Pony Diffusion V6 XL |
| Resolution | 1536x1024 |
| Sampler | euler_ancestral |
| Scheduler | normal |
| Steps | 35 |
| CFG | 7.0 |
| Batch | Seeds 3001-3020 per character |

---

## Style Approach (Hybrid)

- **Quality tags:** Pony V6 XL native (`score_9, score_8_up, score_7_up, source_anime`)
- **Aesthetic:** Genshin Impact visual descriptors (not the literal tag). Cel shading, color-coded character identity (hair = theme color), fantasy-military armor, glowing accents, vibrant saturated palette.
- **Why not `genshin impact style` tag:** Pony V6 XL interprets this tag differently than Anything V5. Using the component descriptors produces more reliable results.

---

## Shared Tag Blocks

### Quality Tags (all prompts)

```
score_9, score_8_up, score_7_up, source_anime,
masterpiece, best quality, ultra detailed,
```

### Sheet Layout Tags (all prompts)

```
character reference sheet, character design sheet,
multiple views, turnaround reference, model sheet,
clean layout, solid white background, no background,
```

### ARIA Chassis Tags (all ARIA prompts)

```
feminine android, white silver chassis visible at joints,
(small glowing cyan diamond on forehead:1.3),
(cyan glowing eyes:1.2), pale luminous skin,
subtle panel lines on skin at temples and jawline,
```

### Layout Direction Tags (all prompts)

```
(left side large upper body portrait:1.2),
(right side chibi super deformed views:1.2),
(right top 2x2 grid front view back view left view right view:1.1),
(right bottom center chibi fallen defeated eyes closed broken equipment:1.1),
cel shaded, clean linework, vibrant saturated colors,
fantasy military aesthetic, glowing accents,
```

### Shared Negative Prompt (all prompts)

```
score_4, score_3, score_2, score_1,
bad anatomy, bad hands, missing fingers, extra fingers,
blurry, low quality, worst quality,
watermark, text, signature, username,
cropped, out of frame, deformed, disfigured, ugly,
extra arms, extra legs, fused fingers, long neck,
2girls, multiple characters, different characters,
male, masculine, boy, man,
messy layout, overlapping views, cluttered,
detailed background, scenery, landscape,
elf ears, pointed ears,
```

---

## Character Prompts

### Aurora (Striker Unit 02)

**Seed range:** 3001-3020

```
Prompt:
score_9, score_8_up, score_7_up, source_anime,
masterpiece, best quality, ultra detailed,
character reference sheet, character design sheet,
multiple views, turnaround reference, model sheet,
clean layout, solid white background, no background,

1girl, aurora, striker unit,
feminine android, white silver chassis visible at joints,
(small glowing cyan diamond on forehead:1.3),
(cyan glowing eyes:1.2), pale luminous skin,
subtle panel lines on skin at temples and jawline,
long straight golden blonde hair flowing to mid back,
red targeting monocle visor over right eye with data readout,
lightweight gold amber recon armor plates, form fitting,
dark bodysuit underneath,
chest plate, forearm guards, thigh armor plates,
(oversized anti-materiel sniper rifle:1.3),
dark gunmetal rifle with gold accent stripes,
(red glowing scope on rifle:1.2),
small sidearm in right thigh holster,
cold focused calculating expression,

(left side large upper body portrait:1.2),
(right side chibi super deformed views:1.2),
(right top 2x2 grid front view back view left view right view:1.1),
(right bottom center chibi fallen defeated eyes closed broken rifle:1.1),
cel shaded, clean linework, vibrant saturated colors,
fantasy military aesthetic, glowing accents,

Negative:
score_4, score_3, score_2, score_1,
bad anatomy, bad hands, missing fingers, extra fingers,
blurry, low quality, worst quality,
watermark, text, signature, username,
cropped, out of frame, deformed, disfigured, ugly,
extra arms, extra legs, fused fingers, long neck,
2girls, multiple characters, different characters,
male, masculine, boy, man,
messy layout, overlapping views, cluttered,
detailed background, scenery, landscape,
elf ears, pointed ears,
```

### Rex (Vanguard Unit 01)

**Seed range:** 3021-3040

```
Prompt:
score_9, score_8_up, score_7_up, source_anime,
masterpiece, best quality, ultra detailed,
character reference sheet, character design sheet,
multiple views, turnaround reference, model sheet,
clean layout, solid white background, no background,

1girl, rex, vanguard unit,
feminine android, white silver chassis visible at joints,
(small glowing cyan diamond on forehead:1.3),
(cyan glowing eyes:1.2), pale luminous skin,
subtle panel lines on skin at temples and jawline,
short choppy reddish pink hair, messy wind swept,
sharp intense cyan glowing eyes, determined expression,
heavy reddish pink plate armor, large layered pauldrons,
(oversized tower shield in left hand taller than torso:1.3),
brushed steel shield with reddish pink trim, battle scarred,
(broad sword with cyan glowing edge in right hand:1.2),
gold cross guard on sword,
tattered reddish pink scarf around neck trailing behind,
strong determined protective expression,

(left side large upper body portrait:1.2),
(right side chibi super deformed views:1.2),
(right top 2x2 grid front view back view left view right view:1.1),
(right bottom center chibi fallen defeated eyes closed cracked shield dropped sword:1.1),
cel shaded, clean linework, vibrant saturated colors,
fantasy military aesthetic, glowing accents,

Negative:
score_4, score_3, score_2, score_1,
bad anatomy, bad hands, missing fingers, extra fingers,
blurry, low quality, worst quality,
watermark, text, signature, username,
cropped, out of frame, deformed, disfigured, ugly,
extra arms, extra legs, fused fingers, long neck,
2girls, multiple characters, different characters,
male, masculine, boy, man,
messy layout, overlapping views, cluttered,
detailed background, scenery, landscape,
elf ears, pointed ears,
gun, firearm, rifle, pistol,
```

### Lily (Medic Unit 03)

**Seed range:** 3041-3060

```
Prompt:
score_9, score_8_up, score_7_up, source_anime,
masterpiece, best quality, ultra detailed,
character reference sheet, character design sheet,
multiple views, turnaround reference, model sheet,
clean layout, solid white background, no background,

1girl, lily, medic unit,
feminine android, white silver chassis visible at joints,
(small glowing cyan diamond on forehead:1.3),
(cyan glowing eyes:1.2), pale luminous skin,
subtle panel lines on skin at temples and jawline,
long wavy elf green hair flowing softly to mid back,
large warm cyan glowing eyes, gentle smile,
beauty mark below left eye,
white medical uniform, emerald green tactical long coat,
green cross emblem on left breast,
(soft emerald green healing glow from left hand with floating particles:1.3),
compact white energy pistol with green accents in right hand at side,
cross body medical satchel at right hip,
gentle compassionate expression,

(left side large upper body portrait:1.2),
(right side chibi super deformed views:1.2),
(right top 2x2 grid front view back view left view right view:1.1),
(right bottom center chibi fallen defeated eyes closed no glow spilled satchel:1.1),
cel shaded, clean linework, vibrant saturated colors,
fantasy military aesthetic, glowing accents,

Negative:
score_4, score_3, score_2, score_1,
bad anatomy, bad hands, missing fingers, extra fingers,
blurry, low quality, worst quality,
watermark, text, signature, username,
cropped, out of frame, deformed, disfigured, ugly,
extra arms, extra legs, fused fingers, long neck,
2girls, multiple characters, different characters,
male, masculine, boy, man,
messy layout, overlapping views, cluttered,
detailed background, scenery, landscape,
elf ears, pointed ears,
```

### Hana (Architect Unit 04)

**Seed range:** 3061-3080

```
Prompt:
score_9, score_8_up, score_7_up, source_anime,
masterpiece, best quality, ultra detailed,
character reference sheet, character design sheet,
multiple views, turnaround reference, model sheet,
clean layout, solid white background, no background,

1girl, hana, architect unit,
feminine android, white silver chassis visible at joints,
(small glowing cyan diamond on forehead:1.3),
(cyan glowing eyes:1.2), pale luminous skin,
subtle panel lines on skin at temples and jawline,
(dark blackish brown hair in high ponytail:1.3), bangs across forehead,
(NOT white hair NOT silver hair NOT gray hair:1.2),
bright inquisitive cyan glowing eyes, confident grin showing teeth,
grease smudge on right cheek,
cobalt blue engineer jumpsuit, rolled up sleeves exposing forearm chassis,
(amber round goggles pushed up on forehead:1.2),
(oversized mechanical wrench hammer hybrid on right shoulder:1.3),
brushed steel wrench with cobalt blue grip,
pistol in left hip holster, dark gunmetal,
wide brown leather tool belt overstuffed with tools,
energetic confident expression,

(left side large upper body portrait:1.2),
(right side chibi super deformed views:1.2),
(right top 2x2 grid front view back view left view right view:1.1),
(right bottom center chibi fallen defeated eyes closed wrench dropped goggles cracked:1.1),
cel shaded, clean linework, vibrant saturated colors,
fantasy military aesthetic, glowing accents,

Negative:
score_4, score_3, score_2, score_1,
bad anatomy, bad hands, missing fingers, extra fingers,
blurry, low quality, worst quality,
watermark, text, signature, username,
cropped, out of frame, deformed, disfigured, ugly,
extra arms, extra legs, fused fingers, long neck,
2girls, multiple characters, different characters,
male, masculine, boy, man,
messy layout, overlapping views, cluttered,
detailed background, scenery, landscape,
elf ears, pointed ears,
white hair, silver hair, gray hair, blonde hair,
```

---

## Post-Processing Pipeline

### Step 1: Generate Batch

Run seeds in specified range at 1536x1024 per character. Select best layout per character (clean separation between portrait and chibi grid).

### Step 2: Crop Regions

Exact crop coordinates determined from Aurora experiment, then templated.

| Region | Approximate area | Output file | Final size |
|--------|-----------------|-------------|------------|
| Portrait | Left ~550px column | `{name}_portrait.png` | 512x768 |
| Front chibi | Right section, top-left cell | `{name}_sprite.png` | 128x128 |
| Back chibi | Right section, top-right cell | `{name}_sprite_back.png` | 128x128 |
| Left chibi | Right section, bottom-left cell | `{name}_sprite_left.png` | 128x128 |
| Right chibi | Right section, bottom-right cell | `{name}_sprite_right.png` | 128x128 |
| Dead chibi | Right section, bottom center | `{name}_dead.png` | 128x128 |

### Step 3: Background Removal (BiRefNet)

BiRefNet via `ComfyUI-BiRefNet` custom node. Replaces rembg entirely.

1. BiRefNet generates alpha matte per crop (handles hair wisps, glow effects, semi-transparent elements)
2. Threshold cleanup: alpha < 10 -> 0, alpha > 245 -> 255 (eliminates white fringe)
3. Output as 8-bit RGBA PNG

### Step 4: Save

Per character, output files:

| File | Purpose |
|------|---------|
| `{name}_sheet_fullres.png` | Full 1536x1024 reference sheet (kept for consistency reference) |
| `{name}_portrait.png` | 512x768 briefing card |
| `{name}_sprite.png` | 128x128 front-facing game sprite (primary) |
| `{name}_sprite_back.png` | 128x128 back view |
| `{name}_sprite_left.png` | 128x128 left view |
| `{name}_sprite_right.png` | 128x128 right view |
| `{name}_dead.png` | 128x128 dead/offline sprite |
| `*_fullres.png` variants | Pre-downscale crops |

All files go to `godot/assets/aria/`.

---

## ComfyUI Setup Requirements

1. **Pony Diffusion V6 XL checkpoint** -- download to `ComfyUI/models/checkpoints/`
2. **ComfyUI-BiRefNet custom node** -- install to `ComfyUI/custom_nodes/`
3. No other new dependencies

---

## Rollout Plan

1. **Experiment:** Aurora only. Generate 20 seeds, pick best, crop, verify quality.
2. **Template:** Lock crop coordinates and prompt structure from Aurora results.
3. **Apply to all ARIA:** Generate Rex, Lily, Hana using templated prompts.
4. **Replace assets:** New sprites replace existing ones in `godot/assets/aria/`.
5. **Update docs:** Revise `art-generation-guide.md` with new model, prompts, and pipeline.
6. **Fallback:** Keep existing Anything V5 assets until new ones are verified in-game.

---

## Seed Registry

To be filled as experiments produce approved results.

| Character | Approved Seed | Notes |
|-----------|--------------|-------|
| Aurora | TBD | First experiment |
| Rex | TBD | |
| Lily | TBD | |
| Hana | TBD | |
