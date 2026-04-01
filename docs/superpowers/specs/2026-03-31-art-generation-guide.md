# ARIA: Defenders of Duskwall -- Art Generation Guide

**Date:** 2026-03-31
**Status:** Approved
**Model:** Anything V5 (anythingV5_v5PrtRE.safetensors) via ComfyUI
**Hardware:** NVIDIA RTX 4060 (8GB VRAM)

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

---

## 1. Shared Visual Language

All ARIA units share these design elements to visually unify them as products of the same technology. These tags MUST appear in every ARIA prompt.

### ARIA Chassis (shared across all units)

- **Base chassis:** White/silver metallic body visible at joints (neck seams, elbow joints, knee joints, finger segments). Not full-body metal -- more like synthetic skin over mechanical structure.
- **Anima core indicator:** Small glowing cyan diamond shape on center of forehead. This is the visual marker of an active Anima consciousness. All 4 units have this. When dead/offline, this diamond is dark/cracked.
- **Eye color:** All ARIA units have identical cyan glowing eyes (RGB: 64, 224, 255). Pupils are visible but the iris glows. The glow intensifies during combat or emotional moments.
- **Panel lines:** Subtle seam lines on skin at temples, along jawline, down the sides of the neck, and on the backs of hands. These are faint -- not robotic, more like a porcelain doll with visible joins.
- **Age appearance:** All units appear 18-20 years old. Youthful but not childish. Mature enough to read as combat-capable.
- **Skin tone:** Pale but warm. Slightly luminous quality (the Anima energy beneath the synthetic skin). Not corpse-pale, not tanned. Think porcelain with a faint inner glow.
- **Body type:** Feminine humanoid. Athletic and functional, not exaggerated. Each class has a distinct build (see individual sheets).

### Color Palette (exact values)

| Element | Hex | RGB | Usage |
|---------|-----|-----|-------|
| Anima cyan | #40E0FF | 64, 224, 255 | Eyes, forehead diamond, weapon accents, healing glow |
| Chassis white | #E8E0D8 | 232, 224, 216 | Joint plates, base armor underlay |
| Panel line gray | #A0A0A8 | 160, 160, 168 | Seam lines on skin |
| Rex reddish-pink (theme) | #E85580 | 232, 85, 128 | Hair color, armor accent, scarf, identity color |
| Rex reddish-pink dark | #B83060 | 184, 48, 96 | Shadow/secondary |
| Aurora gold (theme) | #E6B832 | 230, 184, 50 | Hair color, armor accent, identity color |
| Aurora gold dark | #B08820 | 176, 136, 32 | Shadow/secondary |
| Lily elf green (theme) | #66CC88 | 102, 204, 136 | Hair color, coat accent, healing glow, identity color |
| Lily elf green dark | #449966 | 68, 153, 102 | Shadow/secondary |
| Hana dark brown (theme) | #3A2820 | 58, 40, 32 | Hair color, identity color |
| Hana dark brown mid | #5C4030 | 92, 64, 48 | Hair highlights |
| Hana accent blue | #5599DD | 85, 153, 221 | Jumpsuit, tool accents (secondary identity) |
| Zombie pale lavender | #998899 | 153, 136, 153 | Zombie skin (anime-style, not grotesque) |
| Zombie eyes | #FF6666 | 255, 102, 102 | Zombie glowing eyes (softer red) |

### World Palette

| Element | Hex | RGB | Usage |
|---------|-----|-----|-------|
| Irradiated sky orange | #CC6622 | 204, 102, 34 | Horizon glow in backgrounds |
| Duskwall stone | #555566 | 85, 85, 102 | Wall/fortification color |
| Wasteland brown | #8B7355 | 139, 115, 85 | Ground, dirt, ruins |
| Dead vegetation | #9B8B4A | 155, 139, 74 | Dead grass, dried plants |
| Toxic green fog | #446633 | 68, 102, 51 | Zombie ambient atmosphere |

---

## 2. Character Lore & Design Sheets

### REX -- Vanguard Unit 01

**Anima Origin:** Patterned after Lieutenant Reika Tanaka, a soldier who held the North Bridge checkpoint alone for six hours during the Fall of Citadel Seven, buying time for 200 civilians to evacuate. She died when the bridge collapsed. Her neural pattern was recovered from field medical records and became the template for Rex's Anima.

**Personality Traits (visible in art):** Determined, protective, slightly fierce. Stands like she's guarding something behind her. Never relaxed -- always battle-ready. Slight forward lean, weight on front foot.

**Physical Design:**
- **Hair:** Short, choppy, reddish-pink (#E85580). Vibrant and eye-catching -- this is her identity color. Messy, wind-swept, practical cut. Bangs swept to the right, exposing the forehead Anima diamond. Longest strands reach jawline. The pink-red hue contrasts against her heavy armor.
- **Eyes:** Cyan (#40E0FF), sharp and intense. Slight narrow/focused look. Inner glow visible.
- **Face:** Strong jawline for an android. Determined set to the mouth. Small scar-like panel line across left cheek (battle damage never repaired -- she refused).
- **Build:** Stocky for an ARIA unit. Reinforced frame -- wider shoulders, thicker limbs. Heaviest of the four. Stands with feet shoulder-width apart.
- **Height reference:** Shortest of the four (compact tank frame).

**Equipment Design:**
- **Armor:** Heavy reddish-pink (#E85580) tinted plate armor over white chassis. The armor matches her hair -- she is visually unified by color. Layered pauldrons (shoulder plates) -- left pauldron is larger (shield side). Chest plate has an engraved Duskwall crest (simple shield with "D" initial). Armor shows battle damage: scratches, dents, scorch marks. This is worn gear, not ceremonial.
- **Shield:** Tower shield, rectangular with rounded top, taller than her torso. Held in left hand/arm. Material: brushed steel (#88909A) with crimson trim. Surface has impact marks, a crack running diagonally, and the Duskwall crest painted in worn crimson at center. The shield defines her silhouette from the left side.
- **Sword:** Broad sword in right hand. Standard length (hip to ground when held down). Blade is steel with a faint cyan glow along the cutting edge (#40E0FF at 30% opacity). Cross-guard is gold (#CC9933). Grip wrapped in dark leather.
- **Scarf:** Tattered reddish-pink (#E85580) fabric scarf matching her hair color. Wrapped once around the neck, trailing behind over the right shoulder. Frayed edges, battle-worn. This is her signature emotional element -- it belonged to the original Reika.
- **Boots:** Heavy crimson armored boots. Knee-high. Steel toe caps. Functional, not decorative.

**Theme Color Rule:** Rex's reddish-pink hair IS her identity color. Her armor, scarf, and UI elements all echo this hue. When you see reddish-pink in any context, it means Rex.

**Silhouette Test:** From pure black silhouette, Rex is identifiable by: wide stance, oversized shield on left, sword on right, pauldron bulk, trailing scarf.

---

### AURORA -- Striker Unit 02

**Anima Origin:** Patterned after Yuki Ashford, a championship precision shooter who held 14 world records. She volunteered for Anima extraction when diagnosed with terminal radiation sickness, wanting her skills to outlive her body. Her pattern produces an Anima with inhuman patience and the refusal to ever waste a shot.

**Personality Traits (visible in art):** Cold, focused, calculating. Stands perfectly still. Minimal expression. One eye always behind the visor -- reading data. Slight head tilt as if tracking a target.

**Physical Design:**
- **Hair:** Long, straight, platinum blonde (#E6D078), reaching mid-back. Perfectly maintained (she's meticulous). Parts at center, frames face symmetrically. Two thin strands fall forward past shoulders.
- **Eyes:** Cyan (#40E0FF). Left eye visible and sharp. Right eye behind the targeting visor (visor glass is red/amber, faintly transparent showing the eye behind it). Cold gaze.
- **Face:** Elegant, angular features. Minimal expression -- resting neutral face. High cheekbones. Thin, precise lips.
- **Build:** Slender, tall, elegant. Longest/tallest of the four. Long legs. Designed for mobility and repositioning. Lean muscle, no bulk.
- **Height reference:** Tallest of the four.

**Equipment Design:**
- **Armor:** Lightweight gold/amber (#E6B832) recon plating. Form-fitting, minimal coverage -- chest plate, forearm guards, thigh plates. Prioritizes mobility over protection. White chassis visible at exposed midriff, arms, legs. Dark bodysuit underneath (#2A2A30).
- **Targeting visor:** Red/amber monocle device over right eye. Mounted on a thin metallic frame that wraps around the right side of the head. The lens has a faint data readout visible (crosshair lines, distance numbers). The visor is her most recognizable feature. It glows faintly red (#CC3333).
- **Sniper rifle:** Anti-materiel rifle, longer than she is tall. Held diagonally across body or resting on shoulder. Color: dark gunmetal (#3A3A40) with gold (#E6B832) accent stripes. Prominent red scope (#CC3333) mounted on top. Bipod folded against barrel. The rifle is comically large relative to her frame -- this is intentional for visual impact.
- **Holster:** Small sidearm in a thigh holster on right leg. Barely visible but present.
- **Boots:** Sleek, knee-high, gold-accented. Light armor. Built for running.

**Silhouette Test:** Identifiable by: extremely long rifle extending past body on one side, visor on head, slender tall frame, flowing hair.

---

### LILY -- Medic Unit 03

**Anima Origin:** Patterned after Dr. Sakura Mori, a battlefield surgeon who operated for 72 consecutive hours during the Siege of Citadel Four, saving 31 lives before collapsing from exhaustion. She survived but suffered permanent neural damage. Her pre-injury neural pattern was used for Lily's Anima, preserving her legendary composure under fire and her refusal to give up on any patient.

**Personality Traits (visible in art):** Gentle, compassionate, warm. Stands with open posture -- hands often slightly raised or open. Slight smile. Looks like she's about to help someone. Soft, approachable body language.

**Physical Design:**
- **Hair:** Long, wavy, elf green (#66CC88). Reaches mid-back. Soft curls, not perfectly straight. Luminous green like forest leaves in sunlight -- this is her identity color. Frames face gently. A few strands fall across forehead near the Anima diamond. Hair moves softly as if in a gentle breeze. The green hair matches her coat and healing glow, creating a unified verdant identity.
- **Eyes:** Cyan (#40E0FF), large and warm. Softer glow than others -- more gentle luminance. Expressive, kind. Slight upward curve to eyebrows (compassionate resting expression).
- **Face:** Soft, rounded features. Warm expression. Gentle smile with lips slightly parted. The kindest face of the four. Small beauty mark below left eye (a deliberate design choice -- Dr. Mori had one).
- **Build:** Medium frame. Graceful, balanced proportions. Neither bulky nor frail. Moves with careful precision (surgeon's hands).
- **Height reference:** Second shortest, slightly taller than Rex.

**Equipment Design:**
- **Uniform:** White medical uniform (#E6E0F0) as the base -- collared, buttoned, clean. Over this, an emerald green (#55CC66) tactical long coat that reaches mid-thigh. The coat has the green cross emblem (#FFFFFF cross on #55CC66 circle) on the left breast pocket. Coat is open in front, showing the white uniform beneath. Coat has utility pockets on both sides.
- **Medical cross:** The white cross on green circle appears on: left breast of coat, left shoulder armband, and on the medical satchel. This is her consistent marking across all art types.
- **Sidearm:** Compact energy pistol in right hand. Small, sleek, white with green accents. Clearly secondary to her role -- held loosely at side, not aimed.
- **Healing glow:** Left hand emits a soft emerald green aura (#55CC66 at 50% opacity). The glow radiates 5-10cm from the palm and fingertips. Small floating particles of light in the aura. This is her most visually distinctive feature.
- **Medical satchel:** Cross-body bag at right hip. Tan/brown leather with the green cross. Slightly open, showing bandages and vials inside.
- **Boots:** Low, practical, white with green trim. Not armored. Medical-grade clean.

**Silhouette Test:** Identifiable by: flowing coat outline, healing glow from one hand, satchel at hip, wavy hair, gentle posture.

---

### HANA -- Architect Unit 04

**Anima Origin:** Patterned after Mei Zhang, a structural engineer who designed and personally built the emergency shelters that housed 3,000 survivors during the first winter after the Fall. She worked until her hands bled, then kept working. Her neural pattern produces an Anima with boundless energy, practical creativity, and the belief that any problem can be solved with the right tool and enough stubbornness.

**Personality Traits (visible in art):** Confident, energetic, resourceful, slightly cocky. Stands with weight shifted, one hand on hip or gesturing. Grin, not a smile -- she's having fun. Looks like she just figured out how to fix everything. Most animated of the four.

**Physical Design:**
- **Hair:** Dark blackish-brown (#3A2820), almost black with warm brown highlights (#5C4030) in light. Pulled back in a practical high ponytail. Bangs across forehead, slightly messy. Ponytail is thick, reaches mid-back, has a slight curl at the end. A few loose strands escape the tie. The dark hair contrasts with her bright blue jumpsuit and amber goggles.
- **Eyes:** Cyan (#40E0FF), bright and inquisitive. Wide, alert, always looking at something with interest. Slight spark of mischief.
- **Face:** Approachable, rounded but defined features. Confident grin showing teeth. Slight smudge of grease on right cheek (she never cleans up). Eyebrows slightly raised -- perpetually interested expression.
- **Build:** Athletic, practical. Medium height, strong arms (builder's frame). Rolled-up sleeves showing forearm chassis joints. Most visibly "working" posture of the four.
- **Height reference:** Second tallest, between Aurora and Lily.

**Equipment Design:**
- **Jumpsuit:** Cobalt blue (#5599DD) engineer's jumpsuit. Full-body, zippered front, collar. Sleeves rolled up to elbows, exposing white chassis forearms. Reinforced knee pads (darker cobalt #336699). Several pockets on thighs and chest, some bulging with tools.
- **Goggles:** Pushed up on forehead, resting above hairline. Round lenses with amber/yellow tint (#CCAA33). Elastic strap is dark brown. The goggles are as iconic to Hana as the visor is to Aurora. They sit right above the Anima diamond.
- **Tool belt:** Wide brown leather belt (#8B6640) slung slightly low on hips. Loaded with: adjustable wrench, pliers, coil of wire, small hammer, measuring tape, and several unidentifiable gadgets. The belt jangles -- it's overstuffed.
- **Wrench:** Oversized mechanical wrench in right hand. Not a standard wrench -- it's a hybrid wrench/hammer with a reinforced head that doubles as a melee weapon. Length: from her hand to the ground when held at side. Color: brushed steel (#A0A0B0) with cobalt blue grip wrapping.
- **Pistol:** Standard-issue sidearm in a hip holster on left side. Dark gunmetal. Functional, not fancy.
- **Boots:** Heavy-duty cobalt work boots. Steel toe. Scuffed and worn. Practical.

**Silhouette Test:** Identifiable by: oversized wrench extending downward, goggles on head, ponytail, tool belt bulk, casual stance.

---

## 3. Enemy Design

### ZOMBIE (Irradiated Mutant)

These are not classic undead -- they are living creatures mutated by solar radiation. Former animals (and some former humans) whose DNA was rewritten by the eleven-day bombardment. They are driven purely by hunger. Visually, they follow the same anime art style as ARIA units -- stylized, not realistic horror. Think anime monster design, not Walking Dead.

**Physical Design:**
- **Skin:** Pale lavender-gray (#998899), smooth anime-style rendering. Not mottled or gore-textured. Clean enough to fit the anime aesthetic. Slight purple undertone suggests radiation mutation.
- **Eyes:** Glowing soft red (#FF6666). Round, large anime-style eyes but with a vacant hungry look. Single pair (not multiple -- keep it clean). The glow is the main threat indicator.
- **Mouth:** Slightly too wide, showing pointed teeth in an anime fang style. Not grotesque -- more "cute-menacing" like a chibi monster. Dark interior.
- **Body:** Humanoid, slightly hunched. One arm slightly longer (subtle asymmetry, not extreme). Torn remnants of pre-apocalypse clothing (faded purple-brown rags #665555). Visible cracks/veins on skin in a stylized pattern (not realistic gore). Some bandage wrappings on arms/legs.
- **Hair:** Messy, stringy, dark desaturated purple (#554455). Unkempt but still reads as anime hair, not realistic matted hair.
- **Movement:** Shambling, arms reaching forward. Tilted head. Lurching but with anime-proportioned limbs.
- **Size:** Similar to ARIA units but hunched, so appears shorter.
- **Overall tone:** Anime monster, not horror monster. Should look threatening but not disturbing. Think Slime from Dragon Quest or hollows from Bleach -- stylized enemies that fit in an anime world.

**Visual distinction from ARIA:** Zombies must be immediately distinguishable from ARIA. Key differences: desaturated palette (ARIA have vivid colors), red eyes (not cyan), no glowing cyan elements, vacant expression (ARIA have personality), hunched posture (ARIA stand upright), ragged clothing (ARIA have clean armor/uniforms).

---

## 4. Asset Manifest

### Backgrounds (displayed at native resolution, overlaid with semi-transparent dark filter)

| # | Filename | Resolution | Description |
|---|----------|-----------|-------------|
| 1 | `bg_lore.png` | 1920x1080 | Lore intro screen. Ruined civilization, irradiated orange sky, silhouettes of crumbling skyscrapers, desolate wasteland foreground, no characters, dark and somber, faint toxic haze, crepuscular rays through dust. Mood: loss, desolation, the world that was. |
| 2 | `bg_briefing.png` | 1920x1080 | Pre-combat briefing. Zombie horde approaching from distance, dozens of silhouettes with glowing red eyes in green fog, Duskwall fortification wall visible at bottom/foreground, dramatic dark sky, sense of impending siege. Mood: menace, urgency, the threat ahead. |

### Portraits (displayed in briefing cards, 512x768 each)

| # | Filename | Resolution | Description |
|---|----------|-----------|-------------|
| 3 | `rex_portrait.png` | 512x768 | Upper body portrait. Rex facing slightly left, shield visible on left edge, sword handle at bottom right. Dramatic side lighting from left (warm orange) casting shadows right. Post-apocalyptic ruins in background, out of focus. Red scarf catches the light. Expression: determined, ready. Eye glow prominent. |
| 4 | `aurora_portrait.png` | 512x768 | Upper body portrait. Aurora facing slightly right, rifle barrel extending past top of frame. Cool blue backlighting, visor data readout glowing. Sniper's perch backdrop (elevated ruins) out of focus. Expression: cold, calculating. Hair flowing. |
| 5 | `lily_portrait.png` | 512x768 | Upper body portrait. Lily facing center, slight turn to left. Healing glow from left hand illuminating her face from below (green accent lighting). Medical satchel strap crossing chest. Duskwall medical bay in background, out of focus. Expression: gentle, compassionate, warm smile. |
| 6 | `hana_portrait.png` | 512x768 | Upper body portrait. Hana facing slightly left, wrench resting on right shoulder. Goggles pushed up, reflecting orange light. Workshop/forge in background, out of focus, sparks. Expression: confident grin, energetic. Grease smudge on cheek. |

### In-Game Sprites -- Alive (generated at 512x512, downscaled to 48x48 with NEAREST neighbor)

| # | Filename | Gen Size | Final Size | Description |
|---|----------|----------|-----------|-------------|
| 7 | `rex_sprite.png` | 512x512 | 48x48 | Chibi Rex. Full body, standing battle-ready. Shield on left, sword on right. Red scarf trailing. Wide stance. White/solid background for removal. |
| 8 | `aurora_sprite.png` | 512x512 | 48x48 | Chibi Aurora. Full body, standing. Rifle held diagonally or resting on shoulder. Visor visible. Hair flowing. White/solid background. |
| 9 | `lily_sprite.png` | 512x512 | 48x48 | Chibi Lily. Full body, standing. Healing glow from left hand. Pistol in right hand at side. Coat visible. White/solid background. |
| 10 | `hana_sprite.png` | 512x512 | 48x48 | Chibi Hana. Full body, standing. Wrench in right hand resting on shoulder. Goggles on forehead. Tool belt visible. White/solid background. |

### In-Game Sprites -- Dead (generated at 512x512, downscaled to 48x48)

| # | Filename | Gen Size | Final Size | Description |
|---|----------|----------|-----------|-------------|
| 11 | `rex_dead.png` | 512x512 | 48x48 | Chibi Rex fallen. Lying on side. Shield cracked, sword dropped nearby. Armor broken, scarf torn. Forehead diamond dark. Eyes dim/closed. Sparks from joints. White/solid background. |
| 12 | `aurora_dead.png` | 512x512 | 48x48 | Chibi Aurora fallen. Collapsed forward over rifle. Visor cracked/dark. Hair splayed. Armor cracked. Forehead diamond dark. Eyes dim/closed. White/solid background. |
| 13 | `lily_dead.png` | 512x512 | 48x48 | Chibi Lily fallen. Lying on back. Coat spread around her. No healing glow. Pistol dropped. Satchel spilled open. Forehead diamond dark. Eyes dim/closed. White/solid background. |
| 14 | `hana_dead.png` | 512x512 | 48x48 | Chibi Hana fallen. Slumped against invisible wall. Wrench dropped. Goggles cracked, fallen beside her. Tools scattered. Forehead diamond dark. Eyes dim/closed. White/solid background. |

### Death Splash Art (full-screen popup, displayed for 3-5 seconds when ARIA is destroyed)

| # | Filename | Resolution | Description |
|---|----------|-----------|-------------|
| 15 | `rex_death_splash.png` | 1024x576 | Rex falling backward, reaching one hand toward camera/viewer. Shield shattered into pieces behind her. Sword falling from other hand. Scarf unfurling in slow-motion. Behind her: multiple zombies (3-5) emerging from green fog with glowing red eyes. Dark stormy sky. Sparks and debris. Her Anima diamond is cracking, cyan light leaking out. Expression: defiant even in death, teeth gritted. Dramatic upward camera angle. |
| 16 | `aurora_death_splash.png` | 1024x576 | Aurora collapsing sideways, rifle falling from hands. Visor shattered, both cyan eyes visible and dimming. Hair sweeping in an arc. Behind her: zombie silhouettes in fog, red eyes. Her last shot: a muzzle flash visible from rifle barrel, one zombie hit and falling. Even dying, she took one more. Expression: pain but satisfaction. Side view composition. |
| 17 | `lily_death_splash.png` | 1024x576 | Lily on her knees, reaching forward with both hands, healing glow fading from her palms. She died trying to save someone. Satchel spilled, medical supplies scattered. Behind her: zombies closing in from the darkness, red eyes in fog. Green healing particles dissolving into the air. Expression: sorrowful, desperate, refusing to stop healing. Front-facing composition. Most emotionally devastating of the four. |
| 18 | `hana_death_splash.png` | 1024x576 | Hana collapsed against a barricade she just finished building. The barricade stands strong even as she doesn't. Wrench still in hand, grip loosening. Goggles pushed up, eyes dimming. Behind her: zombies clawing at the barricade but unable to pass -- her final build holds. Expression: tired smile, satisfied that her work will protect the others. Behind the barricade: faint silhouettes of the other ARIA units still fighting. |

### Enemies & Structures (generated at 512x512, downscaled)

| # | Filename | Gen Size | Final Size | Description |
|---|----------|----------|-----------|-------------|
| 19 | `zombie_sprite.png` | 512x512 | 32x32 | Chibi zombie. Same chibi proportions as ARIA (big head, small body) but grotesque. Big glowing red eyes, distended jaw, gray-green skin, torn brown rags, one arm reaching forward. Shambling stance. White/solid background. |
| 20 | `base.png` | 512x512 | 64x64 | Chibi-style fortified bunker. Top-down-ish angle. Metal walls, antenna, reinforced door, warm orange light from windows, Duskwall crest on front. Sandbags around base. White/solid background. |

---

## 5. Style Consistency Tags

These tag blocks MUST be prepended to every prompt to ensure visual consistency across all 20 assets.

### Tag Block A: Realistic Anime (portraits, backgrounds, death splashes)

```
masterpiece, best quality, ultra detailed,
anime style, official art, league of legends splash art style,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
```

### Tag Block B: Chibi Sprites (in-game sprites, dead sprites, enemy, base)

```
masterpiece, best quality, chibi, game sprite,
cute, super deformed, big head, big eyes, small body,
full body, standing, solid white background,
simple clean background, single character,
pixel art style, game asset,
```

### Tag Block C: ARIA Shared Features (append to every ARIA prompt)

```
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
subtle panel lines on skin,
```

### Tag Block D: Negative Prompt (use for ALL images)

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

---

## 6. Generation Parameters

### ComfyUI Sampler Settings

| Parameter | Portraits | Sprites | Death Splash | Backgrounds |
|-----------|-----------|---------|-------------|-------------|
| **Model** | anything-v5.safetensors | anything-v5.safetensors | anything-v5.safetensors | anything-v5.safetensors |
| **Sampler** | euler_ancestral | euler_ancestral | euler_ancestral | euler_ancestral |
| **Scheduler** | normal | normal | normal | normal |
| **Steps** | 30 | 25 | 35 | 30 |
| **CFG scale** | 7.5 | 7.0 | 8.0 | 7.5 |
| **Width** | 512 | 512 | 1024 | 1920 |
| **Height** | 768 | 512 | 576 | 1080 |
| **Denoise** | 1.0 | 1.0 | 1.0 | 1.0 |

### Seed Registry

Fixed seeds ensure reproducibility. If regenerating, use these exact seeds.

| Asset | Seed |
|-------|------|
| bg_lore | 5001 |
| bg_briefing | 5002 |
| rex_portrait | 1001 |
| aurora_portrait | 1002 |
| lily_portrait | 1003 |
| hana_portrait | 1004 |
| rex_sprite | 2001 |
| aurora_sprite | 2002 |
| lily_sprite | 2003 |
| hana_sprite | 2004 |
| rex_dead | 3001 |
| aurora_dead | 3002 |
| lily_dead | 3003 |
| hana_dead | 3004 |
| rex_death_splash | 4001 |
| aurora_death_splash | 4002 |
| lily_death_splash | 4003 |
| hana_death_splash | 4004 |
| zombie_sprite | 6001 |
| base_sprite | 7001 |

---

## 7. Prompt Templates

Each prompt is constructed as: `[Tag Block A or B] + [Tag Block C if ARIA] + [Character-specific prompt]`

Negative prompt is always Tag Block D.

### 7.1 Backgrounds

**bg_lore.png** (Seed: 5001, 1920x1080, 30 steps, CFG 7.5)
```
Prompt:
masterpiece, best quality, ultra detailed,
anime style, official art, cinematic lighting,
dramatic atmosphere, depth of field,
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
[Tag Block D], people, characters, anime girl, bright colors, happy, cheerful, green vegetation, blue sky, clean
```

**bg_briefing.png** (Seed: 5002, 1920x1080, 30 steps, CFG 7.5)
```
Prompt:
masterpiece, best quality, ultra detailed,
anime style, official art, cinematic lighting,
dramatic atmosphere, depth of field,
zombie horde approaching from distance,
dozens of dark silhouettes with glowing red eyes,
green toxic fog rolling across ground,
fortified wall at bottom foreground with metal plating,
dramatic dark sky with ominous clouds,
sense of impending siege and menace,
red eyes piercing through darkness and fog,
dark oppressive atmosphere, no characters in foreground,
horror atmosphere, dread, approaching doom,

Negative:
[Tag Block D], people, anime girl, bright colors, happy, cheerful, blue sky, daylight, clean
```

### 7.2 Portraits

**rex_portrait.png** (Seed: 1001, 512x768, 30 steps, CFG 7.5)
```
Prompt:
masterpiece, best quality, ultra detailed,
anime style, official art, league of legends splash art style,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
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
tower shield visible on left edge of frame,
broad sword handle visible at bottom right,
reddish pink tattereddish pink scarf around neck trailing behind,
strong determined protective expression,
dramatic warm orange side lighting from left,
post-apocalyptic ruined city background blurred,
looking at viewer,

Negative:
[Tag Block D]
```

**aurora_portrait.png** (Seed: 1002, 512x768, 30 steps, CFG 7.5)
```
Prompt:
masterpiece, best quality, ultra detailed,
anime style, official art, league of legends splash art style,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
subtle panel lines on skin,
1girl, upper body portrait,
long straight platinum blonde hair flowing,
cyan glowing eyes, red targeting monocle visor over right eye,
visor data readout visible on lens,
lightweight gold amber recon armor, form fitting,
dark bodysuit underneath,
oversized sniper rifle barrel extending past top of frame,
cold focused calculating expression,
cool blue backlighting,
elevated ruins sniper perch background blurred,
looking at viewer slightly to right,

Negative:
[Tag Block D]
```

**lily_portrait.png** (Seed: 1003, 512x768, 30 steps, CFG 7.5)
```
Prompt:
masterpiece, best quality, ultra detailed,
anime style, official art, league of legends splash art style,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
subtle panel lines on skin,
1girl, upper body portrait,
long wavy elf green hair flowing softly,
warm gentle cyan glowing eyes,
white medical uniform, emerald green tactical long coat,
green cross emblem on left breast,
medical satchel strap crossing chest,
soft green healing glow from left hand illuminating face,
green light particles floating,
gentle compassionate expression, warm smile,
beauty mark below left eye,
medical bay background blurred,
looking at viewer,

Negative:
[Tag Block D]
```

**hana_portrait.png** (Seed: 1004, 512x768, 30 steps, CFG 7.5)
```
Prompt:
masterpiece, best quality, ultra detailed,
anime style, official art, league of legends splash art style,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
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
loaded brown leather tool belt,
confident energetic grin showing teeth,
grease smudge on right cheek,
workshop forge background with sparks blurred,
looking at viewer,

Negative:
[Tag Block D]
```

### 7.3 In-Game Sprites (Alive)

**rex_sprite.png** (Seed: 2001, 512x512, 25 steps, CFG 7.0)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
cute, super deformed, big head, big eyes, small body,
full body, standing, solid white background,
simple clean background, single character,
pixel art style, game asset,
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
1girl chibi,
short choppy reddish pink hair,
big cute cyan glowing eyes, determined expression, blush,
heavy reddish pink plate armor, large pauldrons,
oversized tower shield in left hand,
broad sword with cyan edge in right hand,
reddish pink tattereddish pink scarf trailing behind,
wide battle stance,

Negative:
[Tag Block D], detailed background, scenery
```

**aurora_sprite.png** (Seed: 2002, 512x512, 25 steps, CFG 7.0)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
cute, super deformed, big head, big eyes, small body,
full body, standing, solid white background,
simple clean background, single character,
pixel art style, game asset,
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
1girl chibi,
long straight platinum blonde hair,
big cute cyan glowing eyes, focused expression, blush,
red targeting visor over right eye,
lightweight gold amber armor, dark bodysuit,
oversized sniper rifle held diagonally,
red glowing scope on rifle,
elegant standing pose,

Negative:
[Tag Block D], detailed background, scenery
```

**lily_sprite.png** (Seed: 2003, 512x512, 25 steps, CFG 7.0)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
cute, super deformed, big head, big eyes, small body,
full body, standing, solid white background,
simple clean background, single character,
pixel art style, game asset,
feminine android, white silver chassis at joints,
small glowing cyan diamond on forehead,
cyan glowing eyes, pale luminous skin,
1girl chibi,
long wavy elf green hair,
big cute warm cyan glowing eyes, gentle smile, blush,
white uniform, emerald green long coat, green cross emblem,
soft green healing glow from left hand,
compact pistol in right hand at side,
medical satchel at hip,
gentle standing pose,

Negative:
[Tag Block D], detailed background, scenery
```

**hana_sprite.png** (Seed: 2004, 512x512, 25 steps, CFG 7.0)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
cute, super deformed, big head, big eyes, small body,
full body, standing, solid white background,
simple clean background, single character,
pixel art style, game asset,
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
[Tag Block D], detailed background, scenery
```

### 7.4 In-Game Sprites (Dead)

**rex_dead.png** (Seed: 3001, 512x512, 25 steps, CFG 7.0)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
cute, super deformed, big head, big eyes, small body,
full body, solid white background,
simple clean background, single character,
pixel art style, game asset,
feminine android, white silver chassis at joints,
dark cracked diamond on forehead,
1girl chibi,
short dark brown hair with crimson tips, messy,
eyes closed, dimmed, offline expression,
heavy crimson armor cracked and broken,
shattered tower shield pieces nearby,
sword dropped on ground beside her,
reddish pink scarf torn and limp,
lying on side, fallen pose,
sparks from exposed joints, battle damage,

Negative:
[Tag Block D], detailed background, scenery, standing, happy, smiling, alive, glowing eyes
```

**aurora_dead.png** (Seed: 3002, 512x512, 25 steps, CFG 7.0)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
cute, super deformed, big head, big eyes, small body,
full body, solid white background,
simple clean background, single character,
pixel art style, game asset,
feminine android, white silver chassis at joints,
dark cracked diamond on forehead,
1girl chibi,
long platinum blonde hair splayed on ground,
eyes closed, dimmed, offline expression,
gold amber armor cracked,
visor shattered and dark,
collapsed forward over broken sniper rifle,
fallen defeated pose,
sparks from joints,

Negative:
[Tag Block D], detailed background, scenery, standing, happy, smiling, alive, glowing eyes
```

**lily_dead.png** (Seed: 3003, 512x512, 25 steps, CFG 7.0)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
cute, super deformed, big head, big eyes, small body,
full body, solid white background,
simple clean background, single character,
pixel art style, game asset,
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
[Tag Block D], detailed background, scenery, standing, happy, smiling, alive, glowing eyes, healing glow
```

**hana_dead.png** (Seed: 3004, 512x512, 25 steps, CFG 7.0)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
cute, super deformed, big head, big eyes, small body,
full body, solid white background,
simple clean background, single character,
pixel art style, game asset,
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
[Tag Block D], detailed background, scenery, standing, happy, smiling, alive, glowing eyes
```

### 7.5 Death Splash Art

**rex_death_splash.png** (Seed: 4001, 1024x576, 35 steps, CFG 8.0)
```
Prompt:
masterpiece, best quality, ultra detailed,
anime style, official art, league of legends splash art style,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
feminine android, white silver chassis at joints,
cracking cyan diamond on forehead leaking light,
dimming cyan eyes,
1girl,
short choppy reddish pink hair,
heavy reddish pink plate armor shattered and breaking,
falling backward, reaching one hand toward viewer,
tower shield shattering into pieces behind her,
sword falling from other hand,
reddish pink scarf unfurling in slow motion,
defiant expression even in death, teeth gritted,
3 to 5 zombies emerging from green fog behind her,
zombies with glowing red eyes in darkness,
dark stormy sky, debris and sparks flying,
dramatic low camera angle looking up,
motion blur on falling debris,
rain drops,

Negative:
[Tag Block D], happy, smiling, cheerful, bright colors, blue sky, daylight
```

**aurora_death_splash.png** (Seed: 4002, 1024x576, 35 steps, CFG 8.0)
```
Prompt:
masterpiece, best quality, ultra detailed,
anime style, official art, league of legends splash art style,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
feminine android, white silver chassis at joints,
cracking cyan diamond on forehead leaking light,
dimming cyan eyes,
1girl,
long platinum blonde hair sweeping in arc,
gold amber armor cracked,
visor shattered, both eyes visible and dimming,
collapsing sideways, rifle falling from hands,
muzzle flash from rifle barrel, one last shot fired,
one zombie hit and falling in background,
zombie silhouettes in green fog with red eyes behind her,
dark atmosphere,
expression of pain but satisfaction,
side view composition,
motion blur, debris,

Negative:
[Tag Block D], happy, smiling, cheerful, bright colors, blue sky, daylight
```

**lily_death_splash.png** (Seed: 4003, 1024x576, 35 steps, CFG 8.0)
```
Prompt:
masterpiece, best quality, ultra detailed,
anime style, official art, league of legends splash art style,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
feminine android, white silver chassis at joints,
cracking cyan diamond on forehead leaking light,
dimming cyan eyes, tears,
1girl,
long wavy elf green hair flowing,
white uniform and green coat torn,
on her knees, reaching forward with both hands,
healing glow fading from palms,
green light particles dissolving into air,
medical supplies scattered on ground,
she died trying to heal someone,
zombies closing in from darkness behind her,
red eyes in green fog,
sorrowful desperate expression, refusing to stop,
front facing composition,
emotional devastating scene,
rain, dark atmosphere,

Negative:
[Tag Block D], happy, smiling, cheerful, bright colors, blue sky, daylight
```

**hana_death_splash.png** (Seed: 4004, 1024x576, 35 steps, CFG 8.0)
```
Prompt:
masterpiece, best quality, ultra detailed,
anime style, official art, league of legends splash art style,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
feminine android, white silver chassis at joints,
cracking cyan diamond on forehead leaking light,
dimming cyan eyes,
1girl,
dark blackish brown hair loose from ponytail,
cobalt blue jumpsuit torn,
goggles pushed up, eyes dimming,
collapsed against a metal barricade she just built,
wrench still in hand but grip loosening,
tired satisfied smile,
zombies clawing at barricade behind her but cannot pass,
her final build holds strong,
faint silhouettes of other ARIA units fighting beyond,
dark atmosphere, orange firelight,

Negative:
[Tag Block D], happy, cheerful, bright colors, blue sky, daylight
```

### 7.6 Enemies & Structures

**zombie_sprite.png** (Seed: 6001, 512x512, 25 steps, CFG 7.0)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
cute, super deformed, big head, big eyes, small body,
full body, standing, solid white background,
simple clean background, single character,
pixel art style, game asset,
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
[Tag Block D], gore, blood, realistic, horror, scary, disgusting, grotesque, blue eyes, cyan eyes, pretty girl
```

**base.png** (Seed: 7001, 512x512, 25 steps, CFG 7.0)
```
Prompt:
masterpiece, best quality, chibi, game sprite,
game asset, solid white background,
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
[Tag Block D], people, characters, anime girl, detailed background, nature
```

---

## 8. Post-Processing

### Background Overlay
Backgrounds (`bg_lore.png`, `bg_briefing.png`) are displayed with a semi-transparent dark overlay in the game UI. The overlay color is `Color(0.0, 0.0, 0.0, 0.5)` -- 50% black. The backgrounds should therefore be painted darker than normal to compensate, but still have enough detail to be visible through the overlay.

### Sprite Background Removal
All sprites (in-game, dead, zombie, base) must have backgrounds removed. Process:
1. Generate with "solid white background" in prompt
2. Apply flood-fill background removal from corners (tolerance: 50)
3. Manual check: ensure no white artifacts remain on character edges
4. Save as RGBA PNG with transparent background

### Sprite Downscaling
1. Generate at 512x512
2. Save full-resolution version as `{name}_fullres.png` for reference
3. Downscale to target size using **NEAREST NEIGHBOR** interpolation (preserves pixel art crispness)
4. Save final version as `{name}.png`

### Death Splash Display
Death splashes are displayed as a temporary full-screen overlay:
1. Fade in over 0.5s
2. Display for 3 seconds
3. Fade out over 0.5s
4. Dark vignette border (20% darker at edges)
5. Character name displayed at bottom: "[Name] -- OFFLINE" in white text

### Quality Check
After generation, verify each image against:
- [ ] Correct character features (hair color, eye color, weapon, outfit)
- [ ] Anima diamond on forehead visible (alive) or cracked (dead)
- [ ] Cyan eyes (alive) or dim/closed (dead)
- [ ] Class color correct (red/gold/green/blue)
- [ ] No extra characters in the image
- [ ] No watermarks or text artifacts
- [ ] Consistent art style across all images of same type
