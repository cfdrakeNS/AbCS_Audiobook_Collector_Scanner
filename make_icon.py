"""Build window icon assets in graphics/ from source PNG or existing ICO."""

from pathlib import Path

from PIL import Image

GRAPHICS = Path("graphics")
SOURCE_PNG = GRAPHICS / "abcs_source_256.png"
SOURCE_ICO = GRAPHICS / "abcs_icon_256x256.ico"
OUT_PNG = GRAPHICS / "abcs_icon_256x256.png"
OUT_ICO = GRAPHICS / "abcs_icon_256x256.ico"


def _load_source() -> Image.Image:
    if SOURCE_PNG.is_file():
        return Image.open(SOURCE_PNG).convert("RGBA")
    if SOURCE_ICO.is_file():
        return Image.open(SOURCE_ICO).convert("RGBA")
    raise FileNotFoundError(
        "No icon source found. Place one of these in graphics/:\n"
        "  - abcs_source_256.png\n"
        "  - abcs_icon_256x256.ico  (copy from Windows build)"
    )


def main() -> None:
    GRAPHICS.mkdir(exist_ok=True)
    src = _load_source()
    src.save(OUT_PNG, format="PNG")
    src.save(
        OUT_ICO,
        format="ICO",
        sizes=[(256, 256), (48, 48), (32, 32), (16, 16)],
    )
    print(f"Done — wrote {OUT_PNG} and {OUT_ICO}")


if __name__ == "__main__":
    main()
