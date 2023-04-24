import sys
from pathlib import Path

from play.image_manipulation import add_noise
from play.image_manipulation import convert_sepia
from play.image_manipulation import open_image
from play.image_manipulation import save_image


if len(sys.argv) != 3:
    print("Usage: input_directory output_directory (created if does not exist)")
else:
    input_dir, output_dir = sys.argv[1:]

    if not Path(input_dir).exists():
        raise ValueError(f"<{input_dir}> does not exist")

    Path(output_dir).mkdir(exist_ok=True)

    for filename in Path(input_dir).glob("*"):
        if filename.stem.startswith("."):
            continue

        original = open_image(filename)

        # Convert to sepia
        sepia_image = convert_sepia(original)
        # blurred_image = sepia_image.filter(ImageFilter.BoxBlur(1))

        # vintage_colors(original)
        add_noise(sepia_image)

        # save_color_image(
        #     color_filter_from_greyscale_filter(greyscale_vignette)(get_color_image(sepia_image)),
        #     f"{output_dir}/{filename.stem}{filename.suffix}",
        # )

        result_image = sepia_image
        save_image(result_image, f"{output_dir}/{filename.stem}{filename.suffix}")
