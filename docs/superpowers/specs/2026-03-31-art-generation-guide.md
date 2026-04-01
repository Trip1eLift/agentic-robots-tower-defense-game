# ARIA: Defenders of Duskwall -- Art Generation Guide v2

**Date:** 2026-03-31
**Status:** Approved (post-review revision)
**Model:** Anything V5 (anything-v5.safetensors) via ComfyUI
**Hardware:** NVIDIA RTX 4060 (8GB VRAM)

---

## Review Fixes Applied

This revision addresses all 21 issues from the 5-stage review gauntlet:
- Sprite size: 48x48 -> **128x128** (AI art readable at this size)
- Gen resolution: 512x512 -> **384x384** for sprites (384/128 = 3x clean ratio)
- Backgrounds: 1920x1080 -> **generate at 512x288, upscale to 1920x1080** (SD 1.5 training distribution)
- Death splashes: 1024x576 -> **MVP: portrait + dark overlay + effects in-engine** (overscoped for AI gen)
- Background removal: flood-fill -> **bright green chroma-key** (protects light hair colors)
- Added: **map tiles, barricade, wall structures, VFX notes**
- Fixed: Aurora hair inconsistency (locked to "golden blonde"), Rex prompt typos
- Fixed: Dead sprite hair colors match alive versions
- Fixed: Base sprite tags (removed chibi head/eyes tags for buildings)
- Added: **iteration strategy** (batch generate, pick best, refine)
- Added: **fallback plan** for failed generations
- Explicit: **animation is Phase 2**, static sprites for MVP
- Weapons verified: Rex=melee (shield+sword, NO gun), Aurora/Lily/Hana=ranged (guns)

---

## Table of Contents

1. [Shared Visual Language](#1-shared-visual-language)
2. [Character Lore & Design Sheets](#2-character-lore--design-sheets)
3. [Enemy Design](#3-enemy-design)
4. [Asset Manifest](#4-asset-manifest)
5. [Style Consistency Tags](#5-style-consistency-tags)
6. [Generation Parameters](#6-generation-parameters)
7. [Prompt Templates](#7-prompt-templates)
8. [Post-Processing](#8-post-processing)
9. [Iteration Strategy](#9-iteration-strategy)
10. [Scope & Deferrals](#10-scope--deferrals)

---

## 1. Shared Visual Language

All ARIA units share these design elements to visually unify them as products of the same technology. These tags MUST appear in every ARIA prompt.

### ARIA Chassis (shared across all units)

- **Base chassis:** White/silver metallic body visible at joints (neck seams, elbow joints, knee joints, finger segments). Not full-body metal -- more like synthetic skin over mechanical structure.
- **Anima core indicator:** Small glowing cyan diamond shape on center of forehead. This is the visual marker of an active Anima consciousness. All 4 units have this. When dead/offline, this diamond is dark/cracked.
- **Eye color:** All ARIA units have identical cyan glowing eyes (RGB: 64, 224, 255). Pupils are visible but the iris glows.
- **Panel lines:** Subtle seam lines on skin at temples, along jawline, down the sides of the neck, and on the backs of hands. Faint -- like a porcelain doll with visible joins.
- **Age appearance:** 18-20 years old. Youthful but not childish.
- **Skin tone:** Pale but warm. Slightly luminous. Porcelain with a faint inner glow.
- **Body type:** Feminine humanoid. Athletic and functional, not exaggerated.

### Color Palette (exact values)

**Theme color = hair color.** Each ARIA's hair IS their identity color. Armor, accents, and UI echo this hue.

| Element | Hex | RGB | Usage |
|---------|-----|-----|-------|
| Anima cyan | #40E0FF | 64, 224, 255 | Eyes, forehead diamond, Rex sword edge |
| Chassis white | #E8E0D8 | 232, 224, 216 | Joint plates, base armor |
| Panel line gray | #A0A0A8 | 160, 160, 168 | Seam lines on skin |
| **Rex reddish-pink** | #E85580 | 232, 85, 128 | Hair, armor, scarf |
| Rex reddish-pink dark | #B83060 | 184, 48, 96 | Shadow |
| **Aurora golden blonde** | #E6C878 | 230, 200, 120 | Hair, armor accent |
| Aurora gold accent | #E6B832 | 230, 184, 50 | Armor plating |
| **Lily elf green** | #66CC88 | 102, 204, 136 | Hair, coat, healing glow |
| Lily elf green dark | #449966 | 68, 153, 102 | Shadow |
| **Hana dark brown** | #3A2820 | 58, 40, 32 | Hair |
| Hana brown highlight | #5C4030 | 92, 64, 48 | Hair light areas |
| Hana cobalt blue | #5599DD | 85, 153, 221 | Jumpsuit, goggles strap |
| Zombie pale lavender | #998899 | 153, 136, 153 | Skin (anime-style) |
| Zombie eyes | #FF6666 | 255, 102, 102 | Glowing eyes (soft red) |

### World Palette

| Element | Hex | RGB | Usage |
|---------|-----|-----|-------|
| Irradiated sky orange | #CC6622 | 204, 102, 34 | Horizon glow |
| Duskwall stone | #555566 | 85, 85, 102 | Walls/fortifications |
| Wasteland brown | #8B7355 | 139, 115, 85 | Ground, dirt |
| Dead vegetation | #9B8B4A | 155, 139, 74 | Dead grass |
| Toxic green fog | #446633 | 68, 102, 51 | Zombie atmosphere |

---

## 2. Character Lore & Design Sheets

### Weapon Summary

| Unit | Class | Combat Type | Primary Weapon | Secondary |
|------|-------|-------------|----------------|-----------|
| Rex | Vanguard | **MELEE** (range 50) | Tower shield (LEFT) + Broadsword (RIGHT) | None -- no gun |
| Aurora | Striker | **RANGED** (range 200) | Oversized sniper rifle | Thigh holster sidearm |
| Lily | Medic | **RANGED** (range 60) | Energy pistol (RIGHT) | Healing glow (LEFT hand) |
| Hana | Architect | **RANGED** (range 80) | Pistol (LEFT hip holster) | Oversized wrench (RIGHT, melee/build tool) |

### REX -- Vanguard Unit 01

**Anima Origin:** Patterned after Lieutenant Reika Tanaka, who held the North Bridge checkpoint alone for six hours during the Fall of Citadel Seven, buying time for 200 civilians to evacuate. She died when the bridge collapsed.

**Physical Design:**
- **Hair:** Short, choppy, reddish-pink (#E85580). Vibrant -- this IS her identity color. Messy, wind-swept. Bangs swept right, exposing forehead Anima diamond. Longest strands reach jawline.
- **Eyes:** Cyan (#40E0FF), sharp and intense. Narrow/focused.
- **Face:** Strong jawline. Determined expression. Small scar-like panel line across left cheek.
- **Build:** Stocky, reinforced frame, wider shoulders. Shortest of the four.

**Equipment (MUST be visible in ALL art):**
- **Shield (LEFT, DOMINANT):** Tower shield, rectangular with rounded top, TALLER THAN HER TORSO. Brushed steel (#88909A) with reddish-pink trim. Battle-scarred: impact marks, diagonal crack, worn Duskwall crest. THIS DEFINES HER SILHOUETTE.
- **Sword (RIGHT):** Broad sword. Blade has faint cyan glow along cutting edge. Gold cross-guard. Dark leather grip.
- **Armor:** Heavy reddish-pink (#E85580) plate over white chassis. Layered pauldrons (left larger for shield arm). Battle damage: scratches, dents, scorch marks.
- **Scarf:** Tattered reddish-pink fabric. Wrapped around neck, trailing behind right shoulder. Belonged to original Reika.
- **NO GUN.** Rex is pure melee. Never depict with a firearm.

**Silhouette Test:** Oversized shield (left) + sword (right) + pauldron bulk + trailing scarf.

---

### AURORA -- Striker Unit 02

**Anima Origin:** Patterned after Yuki Ashford, championship precision shooter with 14 world records. Volunteered for Anima extraction when diagnosed with terminal radiation sickness.

**Physical Design:**
- **Hair:** Long, straight, golden blonde (#E6C878). Reaches mid-back. Perfectly maintained. Parts at center, frames face symmetrically.
- **Eyes:** Cyan (#40E0FF). Left eye visible. Right eye behind targeting visor. Cold gaze.
- **Face:** Elegant, angular. Minimal expression. High cheekbones.
- **Build:** Slender, tall, elegant. Tallest of the four. Long legs.

**Equipment (MUST be visible in ALL art):**
- **Sniper Rifle (DOMINANT):** Anti-materiel rifle, LONGER THAN SHE IS TALL. Dark gunmetal (#3A3A40) with gold (#E6B832) accent stripes. Prominent red scope (#CC3333). Bipod folded. THIS IS HER IDENTITY.
- **Targeting Visor:** Red/amber monocle over right eye. Thin metallic frame. Faint data readout visible (crosshair, distance). Glows faintly red.
- **Armor:** Lightweight gold/amber (#E6B832) recon plating. Form-fitting. Chest plate, forearm guards, thigh plates. Dark bodysuit (#2A2A30) underneath.
- **Holster:** Small sidearm in thigh holster (right leg). Subtle.

**Silhouette Test:** Extremely long rifle extending past body + visor + slender frame + flowing hair.

---

### LILY -- Medic Unit 03

**Anima Origin:** Patterned after Dr. Sakura Mori, battlefield surgeon who operated 72 consecutive hours during the Siege of Citadel Four, saving 31 lives.

**Physical Design:**
- **Hair:** Long, wavy, elf green (#66CC88). Reaches mid-back. Soft curls. Luminous green like forest leaves in sunlight. THIS IS HER IDENTITY COLOR. Matches coat and healing glow.
- **Eyes:** Cyan (#40E0FF), large and warm. Softer glow. Expressive, kind.
- **Face:** Soft, rounded. Gentle smile. Beauty mark below left eye.
- **Build:** Medium, graceful. Second shortest (slightly taller than Rex).

**Equipment (MUST be visible in ALL art):**
- **Healing Glow (LEFT HAND, PRIMARY):** Soft emerald green aura from palm and fingertips. Floating light particles. THIS IS HER MOST DISTINCTIVE FEATURE.
- **Energy Pistol (RIGHT HAND):** Compact, sleek, white with green accents. Held loosely at side, not aimed. Secondary weapon.
- **Coat:** Emerald green (#55CC66) tactical long coat over white medical uniform. Green cross emblem (#FFFFFF cross on #55CC66 circle) on left breast.
- **Medical Cross:** Appears on: coat breast, left shoulder armband, medical satchel. Consistent across all art.
- **Medical Satchel:** Cross-body bag at right hip. Tan leather with green cross.

**Silhouette Test:** Flowing coat + healing glow from hand + satchel + wavy hair.

---

### HANA -- Architect Unit 04

**Anima Origin:** Patterned after Mei Zhang, structural engineer who built emergency shelters housing 3,000 survivors during the first winter after the Fall.

**Physical Design:**
- **Hair:** Dark blackish-brown (#3A2820), almost black with warm highlights (#5C4030) in light. High ponytail, thick. Bangs across forehead. Contrasts with bright blue jumpsuit.
- **Eyes:** Cyan (#40E0FF), bright and inquisitive. Spark of mischief.
- **Face:** Approachable, confident grin showing teeth. Grease smudge on right cheek.
- **Build:** Athletic, medium height. Strong arms (builder's frame). Rolled-up sleeves exposing forearm chassis.

**Equipment (MUST be visible in ALL art):**
- **Wrench (RIGHT HAND, DOMINANT):** Oversized mechanical wrench/hammer hybrid. From her hand to the ground when held at side. Brushed steel (#A0A0B0) with cobalt blue grip. Doubles as melee weapon.
- **Pistol (LEFT HIP):** Standard-issue sidearm in hip holster. Dark gunmetal. Her ranged weapon.
- **Goggles:** Pushed up on forehead above Anima diamond. Round amber lenses (#CCAA33). As iconic as Aurora's visor.
- **Jumpsuit:** Cobalt blue (#5599DD). Zippered front. Sleeves rolled to elbows. Reinforced knee pads.
- **Tool Belt:** Wide brown leather (#8B6640). Overstuffed: wrench, pliers, wire, hammer, measuring tape.

**Silhouette Test:** Oversized wrench extending down + goggles on head + ponytail + tool belt bulk.

---

## 3. Enemy Design

### ZOMBIE (Irradiated Mutant)

Mutated living creatures, not classic undead. **Same anime art style as ARIA** -- stylized, not realistic horror. Think Dragon Quest monsters or Bleach hollows. Threatening but not disturbing.

**Physical Design:**
- **Skin:** Pale lavender-gray (#998899). Smooth anime rendering, not gore-textured. Slight purple undertone.
- **Eyes:** Glowing soft red (#FF6666). Large anime-style but vacant/hungry. Single pair.
- **Mouth:** Slightly too wide. Anime fangs. "Cute-menacing" not grotesque.
- **Hair:** Messy, stringy, dark desaturated purple (#554455). Anime hair, not realistic.
- **Body:** Slightly hunched, one arm subtly longer. Torn faded purple-brown rags (#665555). Stylized crack patterns (not gore). Bandage wrappings.
- **Tone:** Anime monster. Threatening but fits the anime world.

---

## 4. Asset Manifest

**Total: 26 assets** (20 core + 5 map/structures + 1 projectile)

### Backgrounds

Generate at **512x288** (16:9 within SD 1.5 range), then upscale to **1920x1080** via Real-ESRGAN or Lanczos.

| # | Filename | Gen Size | Final Size | Description |
|---|----------|----------|-----------|-------------|
| 1 | `bg_lore.png` | 512x288 | 1920x1080 | Ruined civilization. Irradiated orange sky, crumbling skyscraper silhouettes, desolate wasteland, toxic haze, no characters. Dark and somber. Will be overlaid with 50% black filter. |
| 2 | `bg_briefing.png` | 512x288 | 1920x1080 | Zombie horde approaching. Dozens of silhouettes with glowing red eyes in green fog. Duskwall wall at bottom. Dark sky. Menacing. Will be overlaid with 50% black filter. |

### Portraits (briefing cards)

| # | Filename | Gen Size | Final Size | Description |
|---|----------|----------|-----------|-------------|
| 3 | `rex_portrait.png` | 512x768 | 512x768 | Upper body. Shield on left edge, sword handle at bottom right. Reddish-pink scarf. Duskwall gate background (shared). |
| 4 | `aurora_portrait.png` | 512x768 | 512x768 | Upper body. Rifle barrel past top of frame. Visor glowing. Golden hair flowing. Duskwall gate background (shared). |
| 5 | `lily_portrait.png` | 512x768 | 512x768 | Upper body. Healing glow from left hand. Pistol at side. Medical satchel strap. Duskwall gate background (shared). |
| 6 | `hana_portrait.png` | 512x768 | 512x768 | Upper body. Wrench on right shoulder. Goggles. Pistol holster visible. Duskwall gate background (shared). |

### In-Game Sprites -- Alive

Generate at **384x384** (384/128 = 3x clean downscale ratio), downscale to **128x128**.

| # | Filename | Gen Size | Final Size | Description |
|---|----------|----------|-----------|-------------|
| 7 | `rex_sprite.png` | 384x384 | 128x128 | Chibi Rex. BIG SHIELD on left, sword on right. Reddish-pink armor+scarf. Wide stance. NO GUN. Bright green background for chroma-key. |
| 8 | `aurora_sprite.png` | 384x384 | 128x128 | Chibi Aurora. OVERSIZED RIFLE diagonal/on shoulder. Visor. Golden blonde hair. Bright green background. |
| 9 | `lily_sprite.png` | 384x384 | 128x128 | Chibi Lily. HEALING GLOW left hand. Pistol right hand at side. Green coat, cross emblem. Elf green hair. Bright green background. |
| 10 | `hana_sprite.png` | 384x384 | 128x128 | Chibi Hana. WRENCH on right shoulder. Pistol in left hip holster. Goggles on forehead. Dark brown ponytail. Bright green background. |

### In-Game Sprites -- Dead

Generate at **384x384**, downscale to **128x128**. Hair colors SAME as alive (desaturated by 30% in post-processing, not in prompt).

| # | Filename | Gen Size | Final Size | Description |
|---|----------|----------|-----------|-------------|
| 11 | `rex_dead.png` | 384x384 | 128x128 | Chibi Rex fallen on side. Shield cracked, sword dropped. Reddish-pink armor broken. Scarf torn. Diamond dark. Eyes closed. Bright green background. |
| 12 | `aurora_dead.png` | 384x384 | 128x128 | Chibi Aurora collapsed over broken rifle. Visor cracked. Golden hair splayed. Diamond dark. Eyes closed. Bright green background. |
| 13 | `lily_dead.png` | 384x384 | 128x128 | Chibi Lily on back. Coat spread. No glow. Pistol dropped. Satchel spilled. Elf green hair spread. Diamond dark. Bright green background. |
| 14 | `hana_dead.png` | 384x384 | 128x128 | Chibi Hana slumped. Wrench dropped. Goggles cracked beside her. Tools scattered. Dark brown hair loose. Diamond dark. Bright green background. |

### Death Splash -- MVP Approach

**NOT full AI-generated scene art.** Instead, use the existing portrait image with in-engine effects:
1. Display portrait (512x768) with dark red tint overlay
2. Particle effects: sparks, fading cyan diamonds
3. Vignette border (dark edges)
4. Text: "[Name] -- OFFLINE" at bottom
5. Skip on click (prevents blocking gameplay)

This approach is reliable, consistent, and avoids the hardest-to-generate images. Full scene death art is deferred to post-MVP polish.

### Enemies

| # | Filename | Gen Size | Final Size | Description |
|---|----------|----------|-----------|-------------|
| 15 | `zombie_sprite.png` | 384x384 | 96x96 | Chibi anime zombie. Pale lavender skin. Big red eyes, vacant. Anime fangs. Dark purple messy hair. Torn rags. Hunched, arms reaching. Bright green background. |

### Structures

| # | Filename | Gen Size | Final Size | Description |
|---|----------|----------|-----------|-------------|
| 16 | `base.png` | 384x384 | 128x128 | Fortified bunker. Metal walls, antenna, reinforced door, warm orange window light. Sandbags. Duskwall crest. Slight top-down angle. Bright green background. |
| 17 | `wall.png` | 384x384 | 64x64 | Metal barricade wall segment. Corrugated steel, rivets, rust patches. Vertical. Bright green background. |
| 18 | `barricade.png` | 384x384 | 64x64 | Sandbags + scrap metal low barrier. Stacked sandbags with metal scrap on top. Bright green background. |

### Projectile

| # | Filename | Gen Size | Final Size | Description |
|---|----------|----------|-----------|-------------|
| 19 | `projectile.png` | N/A | 16x16 | Simple energy bolt. Bright cyan/white glow. Programmatic (Pillow), not AI-generated. Used for Aurora, Lily, Hana ranged attacks. Rex has no projectile (melee). |

Note: Projectile is simple enough that programmatic generation is better than AI. A glowing cyan-white circle with a short trail.

### Map Tiles

Generate at **256x256**, downscale to **64x64** (4x clean ratio).

| # | Filename | Gen Size | Final Size | Description |
|---|----------|----------|-----------|-------------|
| 19 | `tile_dirt.png` | 256x256 | 64x64 | Cracked dry brown ground. Tileable. No characters/objects. |
| 20 | `tile_dead_grass.png` | 256x256 | 64x64 | Dirt with sparse yellowed grass tufts. Tileable. |
| 21 | `tile_rubble.png` | 256x256 | 64x64 | Small rocks and concrete debris on dirt. Tileable. |
| 22 | `tile_road.png` | 256x256 | 64x64 | Cracked dark gray asphalt. Faded markings. Tileable. |
| 23 | `tile_rust.png` | 256x256 | 64x64 | Ground with embedded rusted metal scraps. Tileable. |
| 24 | `tile_bridge.png` | 256x256 | 64x64 | Weathered wooden planks. Rope/nail details. Tileable. |
| 25 | `tile_dead_tree.png` | 256x256 | 64x64 | Leafless trunk with bare branches. Decorative overlay. Transparent bg. |

---

## 5. Style Consistency Tags

### Art Style: Genshin Impact

ALL art in this project follows the **Genshin Impact visual style**. This means:
- **Color-coded character identity:** Each character is defined by a dominant color (hair = theme)
- **Clean, vibrant linework:** Smooth outlines, saturated colors, no gritty textures
- **Fantasy-military hybrid aesthetic:** Elegant armor/gear with fantastical elements (glowing accents, flowing fabrics)
- **Expressive but grounded faces:** Large eyes but not extreme chibi proportions in portraits. Detailed, emotive.
- **Cel-shaded lighting feel:** Clear light/shadow division, not painterly gradients
- **Elemental glow effects:** Glowing accents on weapons, eyes, abilities (our equivalent: cyan Anima glow)

The tag `genshin impact style` is added to every prompt. This is the single most important tag for visual consistency.

### Tag Block A: Realistic Anime (portraits, backgrounds)

```
masterpiece, best quality, ultra detailed,
genshin impact style, anime game CG, official game art,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
cel shaded, clean linework, vibrant colors,
```

### Tag Block B: Chibi Sprites (all in-game sprites, enemy, structures)

```
masterpiece, best quality, chibi, game sprite,
genshin impact style, anime game CG,
cute, super deformed, big head, big eyes, small body,
full body, single character,
cel shaded, clean linework, vibrant colors,
game asset,
```

Note: Use "solid bright green background" (NOT white) for chroma-key removal.
Note: Do NOT include "big head, big eyes" for structure/building assets.

### Tag Block C: ARIA Shared Features (every ARIA prompt)

```
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
subtle panel lines on skin,
```

### Tag Block E: Duskwall Gate Background (ALL portraits)

All 4 ARIA portraits share this background to create visual cohesion. They are standing at the Duskwall gate -- the last door between civilization and the wasteland. This replaces per-character backgrounds.

```
duskwall citadel gate background,
massive reinforced metal gate partially open behind her,
thick fortified concrete and steel wall stretching to both sides,
warm orange flood lights mounted on wall,
irradiated orange sky with dust haze above,
desolate wasteland visible through gate opening,
dark atmospheric ground fog,
background slightly blurred depth of field,
```

### Tag Block D: Negative Prompt (ALL images)

```
bad anatomy, bad hands, missing fingers, extra fingers, extra digit,
fewer digits, blurry, low quality, worst quality, normal quality,
watermark, text, signature, username, artist name,
cropped, out of frame, deformed, disfigured, ugly,
duplicate, morbid, mutilated, poorly drawn face,
poorly drawn hands, extra arms, extra legs,
fused fingers, too many fingers, long neck,
multiple characters, 2girls, multiple views, split screen,
male, masculine, boy, man,
jpeg artifacts, error,
```

**IMPORTANT:** In all prompt templates below, "[Tag Block D]" means copy-paste the full text above. ComfyUI does not support macros.

---

## 6. Generation Parameters

### ComfyUI Sampler Settings

| Parameter | Portraits | Sprites (384) | Backgrounds (512x288) | Tiles (256) |
|-----------|-----------|--------------|----------------------|-------------|
| **Model** | anything-v5 | anything-v5 | anything-v5 | anything-v5 |
| **Sampler** | euler_ancestral | euler_ancestral | euler_ancestral | euler_ancestral |
| **Scheduler** | normal | normal | normal | normal |
| **Steps** | 30 | 25 | 30 | 20 |
| **CFG** | 7.5 | 7.0 | 7.5 | 7.0 |
| **Width** | 512 | 384 | 512 | 256 |
| **Height** | 768 | 384 | 288 | 256 |

### Seed Registry

| Asset | Seed | Asset | Seed |
|-------|------|-------|------|
| bg_lore | 5001 | rex_dead | 3001 |
| bg_briefing | 5002 | aurora_dead | 3002 |
| rex_portrait | 1001 | lily_dead | 3003 |
| aurora_portrait | 1002 | hana_dead | 3004 |
| lily_portrait | 1003 | zombie_sprite | 6001 |
| hana_portrait | 1004 | base | 7001 |
| rex_sprite | 2001 | wall | 7002 |
| | | projectile | N/A (programmatic) |
| aurora_sprite | 2002 | barricade | 7003 |
| lily_sprite | 2003 | tile_dirt | 8001 |
| hana_sprite | 2004 | tile_dead_grass | 8002 |
| | | tile_rubble | 8003 |
| | | tile_road | 8004 |
| | | tile_rust | 8005 |
| | | tile_bridge | 8006 |
| | | tile_dead_tree | 8007 |

---

## 7. Prompt Templates

### 7.1 Backgrounds

**bg_lore.png** (512x288, 30 steps, CFG 7.5, Seed 5001)
```
Prompt:
masterpiece, best quality, ultra detailed,
genshin impact style, anime game CG, official game art,
cinematic lighting, dramatic atmosphere, depth of field,
cel shaded, clean linework, vibrant colors,
post-apocalyptic landscape, wide panoramic view,
ruined civilization, crumbling skyscrapers in silhouette,
irradiated orange sky, red sun through dust and haze,
desolate wasteland foreground with cracked earth and debris,
toxic haze hanging low, crepuscular rays through dust clouds,
abandoned vehicles rusting, shattered highway,
no characters, no people, empty world,
dark somber mood, loss and desolation,
muted colors with orange and brown dominant,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, people, characters, anime girl, bright colors, happy, cheerful, green vegetation, blue sky, clean
```

**bg_briefing.png** (512x288, 30 steps, CFG 7.5, Seed 5002)
```
Prompt:
masterpiece, best quality, ultra detailed,
genshin impact style, anime game CG, official game art,
cinematic lighting, dramatic atmosphere, depth of field,
cel shaded, clean linework, vibrant colors,
zombie horde approaching from distance,
dozens of dark silhouettes with glowing red eyes,
green toxic fog rolling across ground,
fortified wall at bottom foreground with metal plating,
dramatic dark sky with ominous clouds,
sense of impending siege and menace,
red eyes piercing through darkness and fog,
dark oppressive atmosphere, no characters in foreground,
dark fantasy atmosphere, dread, approaching doom,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, people, anime girl, bright colors, happy, cheerful, blue sky, daylight, clean
```

### 7.2 Portraits

**rex_portrait.png** (512x768, 30 steps, CFG 7.5, Seed 1001)
```
Prompt:
masterpiece, best quality, ultra detailed,
genshin impact style, anime game CG, official game art,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
cel shaded, clean linework, vibrant colors,
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
subtle panel lines on skin,
1girl, upper body portrait,
short choppy reddish pink hair,
sharp intense cyan glowing eyes,
heavy reddish pink plate armor, layered pauldrons,
chest plate with shield crest engraving,
battle damaged scratched dented armor,
large tower shield visible on left edge of frame,
broad sword handle visible at bottom right,
tattered reddish pink scarf around neck trailing behind,
strong determined protective expression,
dramatic warm orange side lighting from left,
looking at viewer,
duskwall citadel gate background,
massive reinforced metal gate partially open behind her,
thick fortified concrete and steel wall stretching to both sides,
warm orange flood lights mounted on wall,
irradiated orange sky with dust haze above,
desolate wasteland visible through gate opening,
dark atmospheric ground fog,
background slightly blurred depth of field,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, gun, firearm, rifle, pistol
```

**aurora_portrait.png** (512x768, 30 steps, CFG 7.5, Seed 1002)
```
Prompt:
masterpiece, best quality, ultra detailed,
genshin impact style, anime game CG, official game art,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
cel shaded, clean linework, vibrant colors,
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
subtle panel lines on skin,
1girl, upper body portrait,
long straight golden blonde hair flowing,
cyan glowing eyes, red targeting monocle visor over right eye,
visor data readout visible on lens,
lightweight gold amber recon armor, form fitting,
dark bodysuit underneath,
oversized sniper rifle barrel extending past top of frame,
cold focused calculating expression,
cool blue backlighting,
looking at viewer slightly to right,
duskwall citadel gate background,
massive reinforced metal gate partially open behind her,
thick fortified concrete and steel wall stretching to both sides,
warm orange flood lights mounted on wall,
irradiated orange sky with dust haze above,
desolate wasteland visible through gate opening,
dark atmospheric ground fog,
background slightly blurred depth of field,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error
```

**lily_portrait.png** (512x768, 30 steps, CFG 7.5, Seed 1003)
```
Prompt:
masterpiece, best quality, ultra detailed,
genshin impact style, anime game CG, official game art,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
cel shaded, clean linework, vibrant colors,
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
subtle panel lines on skin,
1girl, upper body portrait,
long wavy elf green hair flowing softly,
warm gentle cyan glowing eyes,
white medical uniform, emerald green tactical long coat,
green cross emblem on left breast,
compact energy pistol in right hand at side,
medical satchel strap crossing chest,
soft green healing glow from left hand illuminating face,
green light particles floating,
gentle compassionate expression, warm smile,
beauty mark below left eye,
looking at viewer,
duskwall citadel gate background,
massive reinforced metal gate partially open behind her,
thick fortified concrete and steel wall stretching to both sides,
warm orange flood lights mounted on wall,
irradiated orange sky with dust haze above,
desolate wasteland visible through gate opening,
dark atmospheric ground fog,
background slightly blurred depth of field,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error
```

**hana_portrait.png** (512x768, 30 steps, CFG 7.5, Seed 1004)
```
Prompt:
masterpiece, best quality, ultra detailed,
genshin impact style, anime game CG, official game art,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
cel shaded, clean linework, vibrant colors,
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
subtle panel lines on skin,
1girl, upper body portrait,
dark blackish brown hair in high ponytail, bangs across forehead,
bright inquisitive cyan glowing eyes,
cobalt blue engineer jumpsuit, rolled up sleeves,
amber goggles pushed up on forehead,
oversized mechanical wrench resting on right shoulder,
pistol in holster on left hip,
loaded brown leather tool belt,
confident energetic grin showing teeth,
grease smudge on right cheek,
looking at viewer,
duskwall citadel gate background,
massive reinforced metal gate partially open behind her,
thick fortified concrete and steel wall stretching to both sides,
warm orange flood lights mounted on wall,
irradiated orange sky with dust haze above,
desolate wasteland visible through gate opening,
dark atmospheric ground fog,
background slightly blurred depth of field,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error
```

### 7.3 In-Game Sprites (Alive)

**rex_sprite.png** (384x384, 25 steps, CFG 7.0, Seed 2001)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
genshin impact style, anime game CG,
cute, super deformed, big head, big eyes, small body,
full body, single character, game asset,
cel shaded, clean linework, vibrant colors,
solid bright green background,
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
1girl chibi,
short choppy reddish pink hair,
big cute cyan glowing eyes, determined expression, blush,
heavy reddish pink plate armor, large pauldrons,
oversized tower shield in left hand,
broad sword with cyan glowing edge in right hand,
tattered reddish pink scarf trailing behind,
wide battle stance, no gun, no firearm,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, detailed background, scenery, gun, pistol, rifle, firearm
```

**aurora_sprite.png** (384x384, 25 steps, CFG 7.0, Seed 2002)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
genshin impact style, anime game CG,
cute, super deformed, big head, big eyes, small body,
full body, single character, game asset,
cel shaded, clean linework, vibrant colors,
solid bright green background,
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
1girl chibi,
long straight golden blonde hair,
big cute cyan glowing eyes, focused expression, blush,
red targeting visor over right eye,
lightweight gold amber armor, dark bodysuit,
oversized sniper rifle held diagonally,
red glowing scope on rifle,
elegant standing pose,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, detailed background, scenery
```

**lily_sprite.png** (384x384, 25 steps, CFG 7.0, Seed 2003)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
genshin impact style, anime game CG,
cute, super deformed, big head, big eyes, small body,
full body, single character, game asset,
cel shaded, clean linework, vibrant colors,
solid bright green background,
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
1girl chibi,
long wavy elf green hair,
big cute warm cyan glowing eyes, gentle smile, blush,
white uniform, emerald green long coat, green cross emblem,
soft green healing glow from left hand,
compact energy pistol in right hand at side,
medical satchel at hip,
gentle standing pose,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, detailed background, scenery
```

**hana_sprite.png** (384x384, 25 steps, CFG 7.0, Seed 2004)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
genshin impact style, anime game CG,
cute, super deformed, big head, big eyes, small body,
full body, single character, game asset,
cel shaded, clean linework, vibrant colors,
solid bright green background,
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
1girl chibi,
dark blackish brown hair in high ponytail, bangs,
big cute bright cyan glowing eyes, confident grin, blush,
cobalt blue engineer jumpsuit, rolled up sleeves,
amber goggles pushed up on forehead,
oversized mechanical wrench on right shoulder,
loaded tool belt at hips,
pistol in left hip holster,
energetic standing pose,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, detailed background, scenery
```

### 7.4 In-Game Sprites (Dead)

All dead sprites use the SAME hair color as alive versions. Desaturation is applied in post-processing, not in the prompt.

**rex_dead.png** (384x384, 25 steps, CFG 7.0, Seed 3001)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
genshin impact style, anime game CG,
cute, super deformed, big head, big eyes, small body,
full body, single character, game asset,
cel shaded, clean linework, vibrant colors,
solid bright green background,
feminine android, white silver chassis at joints,
dark cracked diamond on forehead,
1girl chibi,
short choppy reddish pink hair, messy,
eyes closed, dimmed, offline expression,
heavy reddish pink armor cracked and broken,
shattered tower shield pieces nearby,
sword dropped on ground beside her,
tattered reddish pink scarf torn and limp,
lying on side, fallen pose,
sparks from exposed joints, battle damage,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, detailed background, scenery, standing, happy, smiling, alive, glowing eyes
```

**aurora_dead.png** (384x384, 25 steps, CFG 7.0, Seed 3002)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
genshin impact style, anime game CG,
cute, super deformed, big head, big eyes, small body,
full body, single character, game asset,
cel shaded, clean linework, vibrant colors,
solid bright green background,
feminine android, white silver chassis at joints,
dark cracked diamond on forehead,
1girl chibi,
long golden blonde hair splayed on ground,
eyes closed, dimmed, offline expression,
gold amber armor cracked,
visor shattered and dark,
collapsed forward over broken sniper rifle,
fallen defeated pose,
sparks from joints,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, detailed background, scenery, standing, happy, smiling, alive, glowing eyes
```

**lily_dead.png** (384x384, 25 steps, CFG 7.0, Seed 3003)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
genshin impact style, anime game CG,
cute, super deformed, big head, big eyes, small body,
full body, single character, game asset,
cel shaded, clean linework, vibrant colors,
solid bright green background,
feminine android, white silver chassis at joints,
dark cracked diamond on forehead,
1girl chibi,
long wavy elf green hair spread around her,
eyes closed, dimmed, peaceful offline expression,
white uniform and green coat spread around her,
no healing glow, dark hands,
pistol dropped nearby,
medical satchel spilled open, bandages scattered,
lying on back, fallen pose,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, detailed background, scenery, standing, happy, smiling, alive, glowing eyes, healing glow
```

**hana_dead.png** (384x384, 25 steps, CFG 7.0, Seed 3004)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
genshin impact style, anime game CG,
cute, super deformed, big head, big eyes, small body,
full body, single character, game asset,
cel shaded, clean linework, vibrant colors,
solid bright green background,
feminine android, white silver chassis at joints,
dark cracked diamond on forehead,
1girl chibi,
dark blackish brown hair loose from ponytail, messy,
eyes closed, dimmed, offline expression,
cobalt blue jumpsuit torn and damaged,
goggles cracked fallen beside her,
wrench dropped on ground,
tools scattered from broken belt,
slumped sitting pose against invisible wall,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, detailed background, scenery, standing, happy, smiling, alive, glowing eyes
```

### 7.5 Enemy & Structure Sprites

**zombie_sprite.png** (384x384, 25 steps, CFG 7.0, Seed 6001)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
genshin impact style, anime game CG,
cute, super deformed, big head, big eyes, small body,
full body, single character, game asset,
cel shaded, clean linework, vibrant colors,
solid bright green background,
anime style zombie mutant,
pale lavender gray skin, stylized,
big round glowing red eyes, vacant hungry expression,
anime fangs, slightly too wide mouth,
messy stringy dark purple hair,
torn faded purple brown rags clothing,
bandage wrappings on arms,
one arm slightly longer reaching forward,
hunched shambling pose, tilted head,
stylized crack patterns on skin,
anime monster design, cute menacing,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, multiple views, split screen, jpeg artifacts, error, gore, blood, realistic, horror, scary, disgusting, grotesque, blue eyes, cyan eyes, pretty girl, beautiful girl, cute girl
```

**base.png** (384x384, 25 steps, CFG 7.0, Seed 7001)
```
Prompt:
masterpiece, best quality, game sprite,
genshin impact style, anime game CG,
game asset, cel shaded, clean linework,
solid bright green background,
simple clean background,
fortified military bunker building,
metal plating walls, reinforced riveted panels,
radio antenna on roof with blinking red light,
heavy reinforced metal door at front,
warm orange light glowing from small windows,
sandbags stacked around base perimeter,
shield crest emblem with D letter on door,
post apocalyptic military shelter,
top down slight angle view,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, people, characters, anime girl, detailed background, nature
```

**wall.png** (384x384, 25 steps, CFG 7.0, Seed 7002)
```
Prompt:
masterpiece, best quality, game sprite,
genshin impact style, anime game CG,
game asset, cel shaded, clean linework,
solid bright green background,
metal barricade wall segment,
corrugated steel sheet, rivets, rust patches,
vertical defensive wall, post apocalyptic,
simple object, no characters,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, people, characters, anime girl
```

**barricade.png** (384x384, 25 steps, CFG 7.0, Seed 7003)
```
Prompt:
masterpiece, best quality, game sprite,
genshin impact style, anime game CG,
game asset, cel shaded, clean linework,
solid bright green background,
sandbag barricade with scrap metal,
stacked sandbags, metal scrap on top,
low defensive barrier, post apocalyptic,
simple object, no characters,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, people, characters, anime girl
```

### 7.6 Map Tiles

All tiles: 256x256, 20 steps, CFG 7.0. All tile prompts include "genshin impact style, anime game CG" for consistency. Negative for all tiles: "people, characters, anime girl, text, watermark, blurry, low quality, realistic, photo"

**tile_dirt.png** (Seed 8001)
```
genshin impact style, anime game CG, seamless tileable texture, cracked dry brown earth ground,
post apocalyptic wasteland dirt, game texture, top down view
```

**tile_dead_grass.png** (Seed 8002)
```
genshin impact style, anime game CG, seamless tileable texture, dry brown ground with sparse yellowed dead grass,
post apocalyptic wasteland, game texture, top down view
```

**tile_rubble.png** (Seed 8003)
```
genshin impact style, anime game CG, seamless tileable texture, brown ground with scattered concrete rubble and small rocks,
post apocalyptic debris, game texture, top down view
```

**tile_road.png** (Seed 8004)
```
genshin impact style, anime game CG, seamless tileable texture, cracked dark gray asphalt road surface,
faded road markings, post apocalyptic, game texture, top down view
```

**tile_rust.png** (Seed 8005)
```
genshin impact style, anime game CG, seamless tileable texture, brown ground with embedded rusted metal scraps,
post apocalyptic junkyard, game texture, top down view
```

**tile_bridge.png** (Seed 8006)
```
genshin impact style, anime game CG, seamless tileable texture, weathered wooden planks bridge surface,
rope and nail details, brown wood, game texture, top down view
```

**tile_dead_tree.png** (Seed 8007)
```
Prompt:
genshin impact style, anime game CG,
dead leafless tree, bare branches, dark brown trunk,
post apocalyptic, game asset, cel shaded, clean linework,
solid bright green background,
side view, three quarter angle,

Negative:
bad anatomy, bad hands, missing fingers, extra fingers, extra digit, fewer digits, blurry, low quality, worst quality, normal quality, watermark, text, signature, username, artist name, cropped, out of frame, deformed, disfigured, ugly, duplicate, morbid, mutilated, poorly drawn face, poorly drawn hands, extra arms, extra legs, fused fingers, too many fingers, long neck, multiple characters, 2girls, multiple views, split screen, male, masculine, boy, man, jpeg artifacts, error, people, characters, anime girl
```

---

## 8. Post-Processing

### Background Upscaling
1. Generate at 512x288
2. Upscale to 1920x1080 using Lanczos interpolation (or Real-ESRGAN if installed)
3. Apply slight blur (radius 1px) to smooth upscaling artifacts

### Sprite Background Removal (Chroma-Key)
All sprites AND tile_dead_tree are generated on **bright green background** (#00FF00).
1. Remove all pixels within tolerance of pure green (hue 100-140, saturation > 50%)
2. Edge refinement: 1px erosion on alpha channel to remove green fringing
3. Save as RGBA PNG with transparent background
Applies to: all ARIA sprites (alive+dead), zombie, base, wall, barricade, tile_dead_tree.

### Sprite Downscaling
1. Generate at 384x384 (sprites) or 256x256 (tiles)
2. Save full-res as `{name}_fullres.png`
3. Downscale to target using **LANCZOS** (not NEAREST -- review found NEAREST at non-integer ratios produces artifacts; 384/128 = 3x is clean but Lanczos still looks better for AI art)
4. Save final as `{name}.png`

### Dead Sprite Desaturation
1. Take the generated dead sprite (full color)
2. Reduce saturation by 30% in post-processing
3. Reduce brightness by 15%
4. This ensures hair colors match alive versions but look "powered down"

### Death Splash Display (MVP -- in-engine, not AI-generated)
1. Load the character's portrait image (512x768)
2. Apply dark red tint overlay (Color(0.3, 0.0, 0.0, 0.5))
3. Add vignette (20% darker at edges)
4. Particle effects: cyan diamond fragments floating, sparks
5. Text at bottom: "[Name] -- OFFLINE" in white
6. Fade in 0.5s, display 2s, fade out 0.5s
7. **Skippable on click** (prevents blocking gameplay)
8. If multiple deaths, queue with 0.5s overlap

---

## 9. Iteration Strategy

AI generation rarely produces perfect results on first try. Follow this workflow:

### Per-Asset Generation
1. Generate **4 variants** per seed (use seeds: base, base+1, base+2, base+3)
2. Visually review all 4 at target resolution (not just full-res)
3. Pick the best one
4. **Color check:** Spot-check hair, eyes, Anima diamond against palette table. Adjust hue/saturation in post if drifted.
5. If none are acceptable, adjust prompt and re-batch

### Common Issues and Fixes
| Issue | Fix |
|-------|-----|
| Wrong weapon/missing equipment | Move weapon tags earlier in prompt, add to negative |
| Multiple characters | Add "solo, 1girl" weight, strengthen "single character" |
| Style inconsistent | Use same seed range for similar assets (e.g., all sprites 2001-2004) |
| Green bg leaking onto character | Increase bg removal tolerance, try magenta bg instead |
| Details lost at 128px | Keep at 384px full-res, reduce detail in prompt |
| Wrong hair color | Put hair color as first character descriptor |

### Fallback Plan
If AI generation consistently fails for an asset category after 3 batches:
- **Sprites:** Fall back to programmatic pixel art (generate_sprites.py)
- **Portraits:** Use a close-enough generation with post-processing (color correction, crop)
- **Backgrounds:** Use solid gradient backgrounds with particle overlays
- **Death splash:** Already MVP-simplified to portrait + effects

---

## 10. Scope & Deferrals

### MVP (this spec)
- 26 static assets: 2 backgrounds, 4 portraits, 8 sprites (alive+dead), 1 zombie, 3 structures, 1 projectile, 7 map tiles
- Death splash via portrait + in-engine effects (not AI art)
- Static sprites only (no animation frames)

### Phase 2 (deferred)
- **Animation:** 2-4 frame idle animations for ARIA and zombie (sprite sheet)
- **Zombie variants:** 2-3 visual variants (different poses, sizes)
- **Full death splash art:** AI-generated scene illustrations (from Section 4 death splash descriptions in v1)
- **Projectile VFX:** Bullet trails, sword slashes, heal particles (Godot particle system, not sprites)
- **UI assets:** Custom icons, health bars (currently using Godot theme)
- **Additional enemy types:** Runner, Brute, Spitter (Phase 4 enemies)
- **Portraits for briefing cards:** Display in the pre-combat briefing UI
