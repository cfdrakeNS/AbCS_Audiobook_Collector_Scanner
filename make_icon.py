from PIL import Image

src = Image.open("graphics/abcs_source_256.png").convert("RGBA")

src.save("graphics/abcs_icon_256x256.png", format="PNG")
src.save(
    "graphics/abcs_icon_256x256.ico",
    format="ICO",
    sizes=[(256, 256), (48, 48), (32, 32), (16, 16)],
)

print("Done — graphics/abcs_icon_256x256.png and .ico written.")
