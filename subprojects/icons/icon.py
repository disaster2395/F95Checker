import pathlib
from PIL import Image
import shlex
import sys


def icon_generate_source(
    icon_path: pathlib.Path, symbol_name: str, source_path: pathlib.Path
):
    with Image.open(icon_path) as icon:
        if icon.mode == "RGB":
            pixel_bytes = icon.tobytes("raw", "RGBX")
        elif icon.mode == "RGBA":
            pixel_bytes = icon.tobytes("raw", "RGBA")
        else:
            pixel_bytes = icon.convert("RGBA").tobytes("raw", "RGBA")

        byte_length = len(f"0x{0:02X},")
        bytes_per_pixel = 4
        pixels_per_line = 8
        line_length = pixels_per_line * bytes_per_pixel * byte_length

        pixel_array = ",".join(f"0x{pixel:02X}" for pixel in pixel_bytes)
        pixel_lines = [
            pixel_array[i : i + line_length]
            for i in range(0, len(pixel_array), line_length)
        ]

        source = (
            f"// File: {repr(str(icon_path))} ({icon_path.stat().st_size} bytes)\n"
            f"// Exported using icon.py {shlex.join(sys.argv[1:])}\n"
            f"const unsigned int {symbol_name}_width = {icon.width};\n"
            f"const unsigned int {symbol_name}_height = {icon.height};\n"
            f"const unsigned char {symbol_name}_pixels[{len(pixel_bytes)}] =\n"
            "{\n"
            f"    {'\n    '.join(pixel_lines)}"
            "};\n\n"
        )

    source_path.write_text(source)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Generate C source for embedding icons")
        print("Usage: icon.py <icon path> <symbol name> <source path>")
        sys.exit(1)

    icon_path = pathlib.Path(sys.argv[1])
    symbol_name = sys.argv[2]
    source_path = pathlib.Path(sys.argv[3])
    icon_generate_source(icon_path, symbol_name, source_path)
