# ARIA Character Reference Sheet Pipeline

**Date:** 2026-04-01
**Status:** Approved
**Model:** Pony Diffusion V6 XL via ComfyUI
**Hardware:** NVIDIA RTX 4060 (8GB VRAM)

---

## Overview

Generate each ARIA character as a single reference sheet image containing both a portrait and chibi sprites. This solves the consistency problem where separate generations produce different hair colors, outfits, and weapon designs for the same character.

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

Left side: large upper-body portrait for briefing cards and UI.
Right side: 2x2 grid of directional chibis (front, back, left, right) + dead chibi below.

## Generation Parameters

| Parameter | Value |
|-----------|-------|
| Model | Pony Diffusion V6 XL (ponyDiffusionV6XL.safetensors) |
| Resolution | 1536x1024 |
| Sampler | euler_ancestral |
| Scheduler | normal |
| Steps | 35 |
| CFG | 7.0 |
| Seed | Iterate per character (start at 3001) |

## Style (Hybrid Approach)

Pony V6 XL quality/rating tags for generation quality. Genshin-style visual descriptors for aesthetic consistency:

- Color-coded character identity (hair = theme color)
- Cel shading with clean linework
- Fantasy-military armor with glowing accents
- Vibrant saturated palette
- Feminine android chassis details (joints, forehead diamond, panel lines)

The literal tag `genshin impact style` is NOT used (Pony interprets it differently than Anything V5). Instead, the visual properties are described explicitly.

## Prompt Templates

### Aurora (Striker) -- Experiment Character

**Prompt:**
```
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
```

**Negative:**
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

### Rex (Vanguard) -- Apply After Aurora Validated

Swap character-specific tags:
- `short choppy reddish pink hair`
- `heavy reddish pink plate armor, large pauldrons`
- `(oversized tower shield in left hand:1.3)`
- `broad sword with cyan glowing edge in right hand`
- `tattered reddish pink scarf trailing behind`
- `strong determined protective expression`
- `no gun, no firearm` (prompt + negative)
- Dead chibi: `fallen on side, shield cracked, sword dropped`

### Lily (Medic) -- Apply After Aurora Validated

Swap character-specific tags:
- `long wavy elf green hair`
- `white medical uniform, emerald green tactical long coat`
- `green cross emblem on left breast`
- `(soft green healing glow from left hand:1.3)`
- `compact energy pistol in right hand at side`
- `medical satchel at hip`
- `gentle compassionate expression, warm smile`
- `beauty mark below left eye`
- Dead chibi: `fallen on back, coat spread, no glow, pistol dropped, satchel spilled`
- Extra negative: `elf ears, pointed ears` (model hallucination risk from "elf green")

### Hana (Architect) -- Apply After Aurora Validated

Swap character-specific tags:
- `long silver white hair in high ponytail, bangs across forehead`
- `black engineer jumpsuit, rolled up sleeves`
- `amber goggles pushed up on forehead`
- `(oversized mechanical wrench on right shoulder:1.3)`
- `pistol in left hip holster`
- `loaded brown leather tool belt`
- `confident energetic grin showing teeth`
- `grease smudge on right cheek`
- Dead chibi: `slumped, wrench dropped, goggles cracked beside her, tools scattered, hair loose`
- Extra negative: `white hair, silver hair, gray hair` (prevent color drift)

## Post-Processing Pipeline

### Step 1: Generate Batch

Run seeds 3001-3020 at 1536x1024 per character. Select best layout where:
- Portrait and chibi sections are cleanly separated
- All 5 chibi poses are distinct and non-overlapping
- Character identity (hair, weapon, armor) is consistent across all views

### Step 2: Crop Regions

| Region | Source Area | Output File | Final Size |
|--------|-----------|-------------|------------|
| Portrait | Left ~550px column | `{name}_portrait.png` | 512x768 |
| Front chibi | Right section, top-left cell | `{name}_sprite.png` | 128x128 |
| Back chibi | Right section, top-right cell | `{name}_sprite_back.png` | 128x128 |
| Left chibi | Right section, bottom-left cell | `{name}_sprite_left.png` | 128x128 |
| Right chibi | Right section, bottom-right cell | `{name}_sprite_right.png` | 128x128 |
| Dead chibi | Right section, bottom center | `{name}_dead.png` | 128x128 |

Exact crop coordinates determined from first successful Aurora generation, then templated.

### Step 3: Background Removal (BiRefNet)

BiRefNet via `ComfyUI-BiRefNet` node replaces the previous rembg + chroma-key approach.

Pipeline per crop:
1. BiRefNet generates alpha matte (handles hair wisps, glow effects, semi-transparent elements)
2. Threshold cleanup: alpha < 10 forced to 0, alpha > 245 forced to 255 (eliminates white fringe)
3. Output as 8-bit RGBA PNG

BiRefNet advantages over rembg:
- Superior hair edge detection (Aurora's flowing hair, Rex's scarf)
- Preserves glow effects (Anima diamond, Lily's healing glow, weapon glows)
- Handles semi-transparent elements (energy effects, particle glow)

### Step 4: Save Assets

| File | Purpose |
|------|---------|
| `{name}_sheet_fullres.png` | Full 1536x1024 reference sheet (consistency reference) |
| `{name}_portrait.png` | 512x768 briefing card |
| `{name}_sprite.png` | 128x128 front-facing game sprite |
| `{name}_sprite_back.png` | 128x128 back view (future directional sprites) |
| `{name}_sprite_left.png` | 128x128 left view (future directional sprites) |
| `{name}_sprite_right.png` | 128x128 right view (future directional sprites) |
| `{name}_dead.png` | 128x128 dead/offline sprite |
| `*_fullres.png` variants | Pre-downscale crops for each of the above |

## ComfyUI Setup Requirements

1. Download Pony Diffusion V6 XL checkpoint to `ComfyUI/models/checkpoints/`
2. Install `ComfyUI-BiRefNet` custom node in `ComfyUI/custom_nodes/`
3. No other new dependencies

## Rollout Plan

1. **Experiment:** Aurora only -- generate 20 seeds, pick best, crop, verify quality
2. **Template:** Lock crop coordinates and prompt structure from successful Aurora result
3. **Apply to all ARIA:** Generate Rex, Lily, Hana using same template with swapped tags
4. **Replace assets:** New sprites replace existing ones in `godot/assets/aria/`
5. **Update docs:** Revise `art-generation-guide.md` with new model, prompts, and pipeline

## Supersedes

This pipeline replaces the Anything V5 workflow documented in `2026-03-31-art-generation-guide.md` for ARIA character assets. Tile, structure, and background generation may continue using the previous pipeline or be migrated separately.
