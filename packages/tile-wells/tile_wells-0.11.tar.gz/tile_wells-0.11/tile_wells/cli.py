"""
Place the well images of tiled fields in a layout similar to a multiwell
plate. This makes it easy to get an overview of the different conditions in
the plate.

positional arguments:
  path                  path to well images (default: current directory)

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT_FORMAT, --input-format INPUT_FORMAT
                        format for images to be tiled (default: jpg)
  -o OUTPUT_FORMAT, --output-format OUTPUT_FORMAT
                        format for the tiled output image (default: jpg)
"""
import argparse
from pathlib import Path
from datetime import datetime

from joblib import Parallel, delayed

from .tile_images import tile_images

def main():
    # `__doc__.split('\n\n')[0]` everything until the first newline in the docstring
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0],
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('path', default='./', nargs='?',
        help='path to well images (default: current directory)')
    parser.add_argument('-i', '--input-format', default='jpg',
        help='format for images to be tiled (default: %(default)s)')
    parser.add_argument('-o', '--output-format', default='jpg',
        help='format for the tiled output image (default: %(default)s)')

    args = parser.parse_args()
    output_format = args.output_format.lower()
    input_format = args.input_format.lower()
    img_dir = Path(args.path)
    channels = {x.name.split('-')[0] for x in img_dir.iterdir()
        if x.name.endswith(input_format)}
    path_match_string = '{}' + '*.{}'.format(input_format)
    well_dir = img_dir.joinpath(path_match_string)
    tiled_img_dir = img_dir.resolve().parent.joinpath('tiled-well-images')
    tiled_img_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    timestamp_dir = tiled_img_dir.joinpath(timestamp)
    timestamp_dir.mkdir()
    # Process each channel in parallel
    results = Parallel(n_jobs=-2)(delayed(tile_images) # Function
        (img_dir, channel, input_format, output_format, timestamp_dir) # Arguments
        for channel in channels) # Loop to parallelize


if __name__ == '__main__':
    main()
