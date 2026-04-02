"""
ARIA Character Sheet Generator with IP-Adapter

Uses a reference portrait image to guide chibi sheet generation,
ensuring consistent hair color, eye color, outfit, and weapons.

Usage:
    python generate_character_sheet.py --character aurora --seeds 3001-3005
    python generate_character_sheet.py --character aurora --seeds 3001-3005 --mode portrait
    python generate_character_sheet.py --character aurora --seeds 3001-3005 --mode chibi
    python generate_character_sheet.py --character aurora --seeds 3001-3005 --mode chibi --ref godot/assets/aria/aurora_portrait.png
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

COMFYUI_URL = "http://127.0.0.1:8188"

# Shared identity tags per character (used in BOTH portrait and chibi)
IDENTITY = {
    "aurora": {
        "tags": """1girl chibi,
(long flowing light golden blonde hair:1.4), hair past shoulders,
(big cute blue eyes:1.3),
(red headband:1.2),
(white armor:1.3), white chest plate, white shoulder guards,
(black undershirt:1.2), black bodysuit underneath,
(oversized sniper rifle:1.3), holding rifle,
small glowing cyan diamond on forehead,""",
        "extra_negative": "short hair, bob cut, dark armor, brown armor, cyan eyes, green eyes, ",
        "ref_portrait": "godot/assets/aria/aurora_portrait.png",
    },
    "rex": {
        "tags": """1girl chibi,
(pink hair:1.4), short hair to shoulders,
(big cute pink eyes:1.3),
(silver female breast armor:1.4),
(black bodysuit underneath:1.3), no exposed skin,
(silver shoulder pads:1.2), (silver arm guards:1.2),
(red accents:1.2),
(shield in left hand:1.3),
(sword in right hand:1.3),
no gun, no firearm,
large bust,""",
        "extra_negative": "gun, pistol, rifle, firearm, long hair, blue eyes, cyan eyes, multiple views, reference sheet, ",
        "ref_portrait": "godot/assets/aria/rex_portrait.png",
    },
    "lily": {
        "tags": """1girl, lily, medic unit,
feminine android, white silver chassis visible at joints,
(small glowing cyan diamond on forehead:1.3),
(cyan glowing eyes:1.2), pale luminous skin,
subtle panel lines on skin at temples and jawline,
long wavy elf green hair,
white medical uniform, emerald green tactical long coat,
green cross emblem on left breast,
(soft green healing glow from left hand:1.3),
compact energy pistol in right hand at side,
medical satchel at hip,
beauty mark below left eye,""",
        "extra_negative": "elf ears, pointed ears, ",
        "ref_portrait": "godot/assets/aria/lily_portrait.png",
    },
    "hana": {
        "tags": """1girl chibi,
(long silver white hair:1.4), high ponytail, bangs across forehead,
(big cute blue eyes:1.3),
(black tight suit:1.3), (black bodysuit:1.2), form fitting,
(amber goggles pushed up on forehead:1.2),
(holding short submachine gun in right hand:1.3),
loaded tool belt at hips, engineering tools, wrench on belt,
large bust,
small glowing cyan diamond on forehead,""",
        "extra_negative": "brown hair, dark hair, cyan eyes, green eyes, ",
        "ref_portrait": "godot/assets/aria/hana_portrait.png",
    },
}

# Portrait-specific prompt parts
PORTRAIT_PREFIX = """score_9, score_8_up, score_7_up, source_anime,
masterpiece, best quality, ultra detailed,
anime game CG, official game art,
cinematic lighting, dramatic atmosphere, depth of field,
highly detailed face, beautiful detailed eyes,
cel shaded, clean linework, vibrant colors,
"""

PORTRAIT_SUFFIX_BY_CHAR = {
    "aurora": "cold focused calculating expression,",
    "rex": "strong determined protective expression,",
    "lily": "gentle compassionate expression, warm smile,",
    "hana": "confident energetic grin showing teeth,",
}

PORTRAIT_SUFFIX = """
upper body portrait, looking at viewer,
(solid white background:1.3), simple background,
cel shaded, clean linework, vibrant saturated colors,
fantasy military aesthetic, glowing accents,"""

# Chibi sheet-specific prompt parts
CHIBI_PREFIX = """masterpiece, best quality, chibi, game sprite,
genshin impact style, anime game CG,
cute, super deformed, big head, big eyes, small body,
full body, single character, game asset,
cel shaded, clean linework, vibrant colors,
(solid bright green background:1.3),
"""

CHIBI_SUFFIX = """
front view, standing pose,
cute expression, blush,"""

CHIBI_DEAD_SUFFIX = """
fallen, collapsed, lying down, defeated,
eyes closed, unconscious, knocked out,
broken weapon nearby, sad, damaged armor,"""

DEAD_TAGS = {
    "aurora": "collapsed over broken sniper rifle, visor cracked,",
    "rex": "fallen on side, shield cracked, sword dropped nearby,",
    "lily": "lying on back, coat spread, no healing glow, pistol dropped,",
    "hana": "slumped forward, wrench dropped, goggles cracked beside her,",
}

NEGATIVE_BASE = """bad anatomy, bad hands, missing fingers, extra fingers,
blurry, low quality, worst quality,
watermark, text, signature, username,
cropped, out of frame, deformed, disfigured, ugly,
extra arms, extra legs, fused fingers, long neck,
2girls, multiple characters, different characters,
male, masculine, boy, man,
jpeg artifacts, error,"""

PORTRAIT_NEGATIVE_EXTRA = """
chibi, super deformed, big head,
detailed background, scenery, landscape,"""

CHIBI_NEGATIVE_EXTRA = """
realistic, detailed face, portrait,
detailed background, scenery, landscape,
multiple characters, multiple views, turnaround,"""


def build_portrait_workflow(character: str, seed: int) -> dict:
    char = IDENTITY[character]
    expression = PORTRAIT_SUFFIX_BY_CHAR.get(character, "")
    positive = PORTRAIT_PREFIX + char["tags"] + "\n" + expression + PORTRAIT_SUFFIX
    negative = char["extra_negative"] + NEGATIVE_BASE + PORTRAIT_NEGATIVE_EXTRA

    return _make_workflow(positive, negative, seed,
                         width=768, height=1024,
                         filename=f"{character}_portrait_seed{seed}")


def build_chibi_workflow(character: str, seed: int, ref_image: str = None) -> dict:
    """Build single front-view chibi sprite on Anything V5."""
    char = IDENTITY[character]
    positive = CHIBI_PREFIX + char["tags"] + CHIBI_SUFFIX
    negative = char["extra_negative"] + NEGATIVE_BASE + CHIBI_NEGATIVE_EXTRA

    return _make_workflow(positive, negative, seed,
                         width=384, height=384,
                         filename=f"{character}_chibi_seed{seed}",
                         checkpoint="anything-v5.safetensors",
                         steps=25, cfg=7.0)


def build_dead_workflow(character: str, seed: int) -> dict:
    """Build single dead/defeated chibi sprite on Anything V5."""
    char = IDENTITY[character]
    dead_extra = DEAD_TAGS.get(character, "")
    positive = CHIBI_PREFIX + char["tags"] + "\n" + dead_extra + CHIBI_DEAD_SUFFIX
    negative = char["extra_negative"] + NEGATIVE_BASE + CHIBI_NEGATIVE_EXTRA + "\nstanding, happy, smiling, open eyes,"

    return _make_workflow(positive, negative, seed,
                         width=384, height=384,
                         filename=f"{character}_dead_seed{seed}",
                         checkpoint="anything-v5.safetensors",
                         steps=25, cfg=7.0)


def _make_workflow(positive: str, negative: str, seed: int,
                   width: int, height: int, filename: str,
                   checkpoint: str = "ponyDiffusionV6XL.safetensors",
                   steps: int = 35, cfg: float = 7.0) -> dict:
    return {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": checkpoint,
            },
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1,
            },
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": positive,
                "clip": ["4", 1],
            },
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative,
                "clip": ["4", 1],
            },
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2],
            },
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": filename,
                "images": ["8", 0],
            },
        },
    }


def _make_ipadapter_workflow(positive: str, negative: str, seed: int,
                              width: int, height: int, filename: str,
                              ref_image: str, weight: float = 0.8) -> dict:
    """Workflow with IP-Adapter: loads reference image, extracts identity, guides generation."""
    return {
        # Load checkpoint
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": "ponyDiffusionV6XL.safetensors",
            },
        },
        # Load IP-Adapter + CLIP Vision (unified loader auto-detects)
        "10": {
            "class_type": "IPAdapterUnifiedLoader",
            "inputs": {
                "model": ["4", 0],
                "preset": "PLUS (high strength)",
            },
        },
        # Load reference image
        "11": {
            "class_type": "LoadImage",
            "inputs": {
                "image": ref_image,
            },
        },
        # Prep image for CLIP vision
        "12": {
            "class_type": "PrepImageForClipVision",
            "inputs": {
                "image": ["11", 0],
                "interpolation": "LANCZOS",
                "crop_position": "center",
                "sharpening": 0.0,
            },
        },
        # Apply IP-Adapter
        "13": {
            "class_type": "IPAdapter",
            "inputs": {
                "model": ["10", 0],
                "ipadapter": ["10", 1],
                "image": ["12", 0],
                "weight": weight,
                "start_at": 0.0,
                "end_at": 0.8,
                "weight_type": "style transfer",
            },
        },
        # Empty latent
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1,
            },
        },
        # CLIP encode positive
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": positive,
                "clip": ["4", 1],
            },
        },
        # CLIP encode negative
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {
                "text": negative,
                "clip": ["4", 1],
            },
        },
        # KSampler uses IP-Adapter-modified model
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": 35,
                "cfg": 7.0,
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["13", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0],
            },
        },
        # VAE decode
        "8": {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2],
            },
        },
        # Save
        "9": {
            "class_type": "SaveImage",
            "inputs": {
                "filename_prefix": filename,
                "images": ["8", 0],
            },
        },
    }


def queue_prompt(workflow: dict, base_url: str = COMFYUI_URL) -> str:
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{base_url}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    return result["prompt_id"]


def wait_for_completion(prompt_id: str, timeout: int = 300, base_url: str = COMFYUI_URL):
    start = time.time()
    while time.time() - start < timeout:
        try:
            resp = urllib.request.urlopen(f"{base_url}/history/{prompt_id}")
            history = json.loads(resp.read())
            if prompt_id in history:
                return history[prompt_id]
        except urllib.error.URLError:
            pass
        time.sleep(2)
    raise TimeoutError(f"Generation did not complete within {timeout}s")


def get_output_images(history: dict) -> list:
    images = []
    for node_id, node_output in history.get("outputs", {}).items():
        if "images" in node_output:
            for img_info in node_output["images"]:
                images.append(img_info)
    return images


def download_image(img_info: dict, output_dir: Path, base_url: str = COMFYUI_URL) -> Path:
    filename = img_info["filename"]
    subfolder = img_info.get("subfolder", "")
    url = f"{base_url}/view?filename={filename}&subfolder={subfolder}&type=output"
    resp = urllib.request.urlopen(url)
    out_path = output_dir / filename
    with open(out_path, "wb") as f:
        f.write(resp.read())
    return out_path


def parse_seed_range(seed_str: str) -> list:
    if "-" in seed_str:
        start, end = seed_str.split("-")
        return list(range(int(start), int(end) + 1))
    return [int(seed_str)]


def copy_ref_to_comfyui(ref_path: str) -> str:
    """Copy reference image to ComfyUI input directory and return filename."""
    import shutil
    src = Path(ref_path)
    if not src.exists():
        print(f"ERROR: Reference image not found: {ref_path}")
        sys.exit(1)
    dst_dir = Path("D:/ComfyUI/input")
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    shutil.copy2(src, dst)
    return src.name


def generate_batch(character: str, seeds: list, mode: str,
                   output_dir: Path, base_url: str, ref_image: str = None):
    ref_filename = None
    if mode == "chibi" and ref_image:
        ref_filename = copy_ref_to_comfyui(ref_image)
        print(f"Using reference image: {ref_image} -> ComfyUI input/{ref_filename}")
        print(f"IP-Adapter will extract character identity from this portrait")
        print()

    for seed in seeds:
        print(f"[{mode} seed {seed}] Queuing...")
        if mode == "portrait":
            workflow = build_portrait_workflow(character, seed)
        elif mode == "dead":
            workflow = build_dead_workflow(character, seed)
        else:
            workflow = build_chibi_workflow(character, seed, ref_image=ref_filename)

        prompt_id = queue_prompt(workflow, base_url)
        print(f"[{mode} seed {seed}] Waiting (prompt: {prompt_id[:8]}...)...")

        history = wait_for_completion(prompt_id, timeout=300, base_url=base_url)
        images = get_output_images(history)

        for img_info in images:
            path = download_image(img_info, output_dir, base_url)
            print(f"[{mode} seed {seed}] Saved: {path}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Generate ARIA character sheets with IP-Adapter")
    parser.add_argument("--character", required=True, choices=list(IDENTITY.keys()))
    parser.add_argument("--seeds", default="3001-3005", help="Seed or range (e.g. 3001 or 3001-3005)")
    parser.add_argument("--mode", default="chibi", choices=["portrait", "chibi", "dead", "both"],
                        help="Generate portrait, chibi, dead, or both (portrait+chibi)")
    parser.add_argument("--ref", default=None, help="Reference portrait image for IP-Adapter (chibi mode)")
    parser.add_argument("--weight", type=float, default=0.8, help="IP-Adapter weight (0.0-1.0)")
    parser.add_argument("--output", default="output/sheets", help="Output directory")
    parser.add_argument("--comfyui-url", default=COMFYUI_URL, help="ComfyUI API URL")
    args = parser.parse_args()

    base_url = args.comfyui_url
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    seeds = parse_seed_range(args.seeds)
    character = args.character

    # Determine reference image
    ref_image = None if args.ref == "none" else (args.ref or None)

    # Check ComfyUI is running
    try:
        urllib.request.urlopen(f"{base_url}/system_stats")
    except urllib.error.URLError:
        print(f"ERROR: ComfyUI not reachable at {base_url}")
        print("Start ComfyUI first, then re-run this script.")
        sys.exit(1)

    modes = ["portrait", "chibi"] if args.mode == "both" else [args.mode]

    for mode in modes:
        label = "portraits" if mode == "portrait" else "chibi sheets (IP-Adapter)" if ref_image else "chibi sheets"
        res = "768x1024" if mode == "portrait" else "1024x1024"
        print(f"=== Generating {character} {label} ({res}) ===")
        print(f"Seeds: {seeds[0]}-{seeds[-1]}")
        print()
        generate_batch(character, seeds, mode, output_dir, base_url,
                       ref_image=ref_image if mode == "chibi" else None)

    print(f"Done. All images saved to {output_dir}/")


if __name__ == "__main__":
    main()
