"""
Crop and background-remove ARIA character reference sheets.

Takes a generated character sheet (1536x1024) and crops it into:
- Portrait (left side) -> 512x768
- Front chibi (top-left of right grid) -> 128x128
- Back chibi (top-right of right grid) -> 128x128
- Left chibi (bottom-left of right grid) -> 128x128
- Right chibi (bottom-right of right grid) -> 128x128
- Dead chibi (bottom center of right section) -> 128x128

Background removal via BiRefNet (if available) or threshold-based fallback.

Usage:
    python crop_character_sheet.py --input output/sheets/aurora_sheet_seed3005.png --character aurora
    python crop_character_sheet.py --input output/sheets/aurora_sheet_seed3005.png --character aurora --manual

In --manual mode, opens the image and lets you click to define crop regions interactively.
"""

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image


# Default crop regions for 1536x1024 layout
# These are starting estimates -- adjust after seeing actual generation results
# Format: (left, top, right, bottom)
DEFAULT_REGIONS = {
    "portrait": (0, 0, 550, 1024),
    "front":    (550, 0, 1043, 512),
    "back":     (1043, 0, 1536, 512),
    "left":     (550, 512, 1043, 820),
    "right":    (1043, 512, 1536, 820),
    "dead":     (700, 820, 1380, 1024),
}

OUTPUT_SIZES = {
    "portrait": (512, 768),
    "front":    (128, 128),
    "back":     (128, 128),
    "left":     (128, 128),
    "right":    (128, 128),
    "dead":     (128, 128),
}

FILE_NAMES = {
    "portrait": "{name}_portrait.png",
    "front":    "{name}_sprite.png",
    "back":     "{name}_sprite_back.png",
    "left":     "{name}_sprite_left.png",
    "right":    "{name}_sprite_right.png",
    "dead":     "{name}_dead.png",
}

FULLRES_NAMES = {
    "portrait": "{name}_portrait_fullres.png",
    "front":    "{name}_sprite_fullres.png",
    "back":     "{name}_sprite_back_fullres.png",
    "left":     "{name}_sprite_left_fullres.png",
    "right":    "{name}_sprite_right_fullres.png",
    "dead":     "{name}_dead_fullres.png",
}


def remove_white_background(img: Image.Image, threshold: int = 240) -> Image.Image:
    """Remove white background using threshold-based alpha."""
    arr = np.array(img.convert("RGBA"))
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    white_mask = (r > threshold) & (g > threshold) & (b > threshold)
    arr[:, :, 3] = np.where(white_mask, 0, 255)
    # Clean up edges: alpha < 10 -> 0, > 245 -> 255
    alpha = arr[:, :, 3]
    alpha[alpha < 10] = 0
    alpha[alpha > 245] = 255
    arr[:, :, 3] = alpha
    return Image.fromarray(arr)


def try_birefnet_removal(img: Image.Image) -> Image.Image:
    """Try BiRefNet for background removal. Falls back to threshold if unavailable."""
    try:
        import torch
        from torchvision import transforms

        # Add BiRefNet to path
        birefnet_path = Path("D:/ComfyUI/custom_nodes/ComfyUI-BiRefNet")
        if birefnet_path.exists():
            sys.path.insert(0, str(birefnet_path))
            from models.baseline import BiRefNet
            from config import Config

            config = Config()
            model = BiRefNet()

            # Try to load pretrained weights
            weight_dir = Path("D:/ComfyUI/models/BiRefNet")
            weight_files = list(weight_dir.glob("*.pth")) if weight_dir.exists() else []

            if not weight_files:
                print("  BiRefNet weights not found, using threshold fallback")
                return remove_white_background(img)

            state_dict = torch.load(str(weight_files[0]), map_location="cpu")
            model.load_state_dict(state_dict, strict=False)
            model.eval()

            transform = transforms.Compose([
                transforms.Resize((config.size, config.size)),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ])

            input_tensor = transform(img.convert("RGB")).unsqueeze(0)
            with torch.no_grad():
                pred = model(input_tensor)[-1].sigmoid()

            mask = pred[0, 0].cpu().numpy()
            mask = (mask * 255).astype(np.uint8)
            mask = Image.fromarray(mask).resize(img.size, Image.LANCZOS)

            # Apply mask as alpha
            rgba = img.convert("RGBA")
            rgba.putalpha(mask)

            # Threshold cleanup
            arr = np.array(rgba)
            alpha = arr[:, :, 3]
            alpha[alpha < 10] = 0
            alpha[alpha > 245] = 255
            arr[:, :, 3] = alpha

            return Image.fromarray(arr)

    except Exception as e:
        print(f"  BiRefNet failed ({e}), using threshold fallback")

    return remove_white_background(img)


def crop_and_save(
    sheet: Image.Image,
    character: str,
    output_dir: Path,
    regions: dict = None,
    use_birefnet: bool = True,
):
    if regions is None:
        regions = DEFAULT_REGIONS

    output_dir.mkdir(parents=True, exist_ok=True)

    # Save full sheet
    sheet_path = output_dir / f"{character}_sheet_fullres.png"
    sheet.save(sheet_path)
    print(f"Full sheet: {sheet_path}")

    for region_name, bbox in regions.items():
        print(f"Processing {region_name}...")

        # Crop
        crop = sheet.crop(bbox)

        # Remove background
        if use_birefnet:
            clean = try_birefnet_removal(crop)
        else:
            clean = remove_white_background(crop)

        # Save fullres crop
        fullres_name = FULLRES_NAMES[region_name].format(name=character)
        clean.save(output_dir / fullres_name)
        print(f"  Fullres: {fullres_name} ({crop.size[0]}x{crop.size[1]})")

        # Resize to final size
        final_size = OUTPUT_SIZES[region_name]
        final = clean.resize(final_size, Image.LANCZOS)

        # Save final
        final_name = FILE_NAMES[region_name].format(name=character)
        final.save(output_dir / final_name)
        print(f"  Final:   {final_name} ({final_size[0]}x{final_size[1]})")

    print(f"\nAll crops saved to {output_dir}/")


def interactive_crop(sheet: Image.Image) -> dict:
    """Open image for visual inspection and prompt user for coordinates."""
    print(f"Sheet size: {sheet.size[0]}x{sheet.size[1]}")
    print()
    print("Default crop regions (left, top, right, bottom):")
    for name, bbox in DEFAULT_REGIONS.items():
        print(f"  {name:10s}: {bbox}")
    print()
    print("Review the image and adjust coordinates as needed.")
    print("Enter new coordinates as: region left top right bottom")
    print("Or press Enter to accept defaults, or 'done' to finish.")
    print()

    # Save a preview copy the user can open
    preview = Path("output/sheets/_preview.png")
    preview.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(preview)
    print(f"Preview saved to: {preview}")
    print()

    regions = dict(DEFAULT_REGIONS)

    while True:
        line = input("> ").strip()
        if not line or line.lower() == "done":
            break
        parts = line.split()
        if len(parts) == 5:
            name = parts[0]
            if name in regions:
                regions[name] = tuple(int(x) for x in parts[1:5])
                print(f"  Updated {name}: {regions[name]}")
            else:
                print(f"  Unknown region: {name}")
        else:
            print("  Format: region left top right bottom")

    return regions


def main():
    parser = argparse.ArgumentParser(description="Crop ARIA character sheets")
    parser.add_argument("--input", required=True, help="Path to character sheet PNG")
    parser.add_argument("--character", required=True, help="Character name (aurora, rex, lily, hana)")
    parser.add_argument("--output", default="godot/assets/aria", help="Output directory")
    parser.add_argument("--manual", action="store_true", help="Interactive crop coordinate adjustment")
    parser.add_argument("--no-birefnet", action="store_true", help="Skip BiRefNet, use threshold only")
    args = parser.parse_args()

    sheet = Image.open(args.input)
    print(f"Loaded: {args.input} ({sheet.size[0]}x{sheet.size[1]})")

    if sheet.size != (1536, 1024):
        print(f"WARNING: Expected 1536x1024, got {sheet.size[0]}x{sheet.size[1]}")
        print("Crop coordinates may need adjustment.")

    output_dir = Path(args.output)

    if args.manual:
        regions = interactive_crop(sheet)
    else:
        regions = DEFAULT_REGIONS

    crop_and_save(
        sheet=sheet,
        character=args.character,
        output_dir=output_dir,
        regions=regions,
        use_birefnet=not args.no_birefnet,
    )


if __name__ == "__main__":
    main()
