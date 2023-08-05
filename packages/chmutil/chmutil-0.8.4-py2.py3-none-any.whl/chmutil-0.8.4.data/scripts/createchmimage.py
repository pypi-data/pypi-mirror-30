#!python

import sys
import os
import argparse
import logging
import chmutil
from PIL import Image
from PIL import ImageOps
from PIL import ImageFilter

from chmutil.image import RowColumnImageTileGenerator
from chmutil.core import Parameters
from chmutil import core

LOG_FORMAT = "%(asctime)-15s %(levelname)s (%(process)d) %(name)s %(message)s"

# create logger
logger = logging.getLogger('chmutil.createchmimage')


class NoInputImageFoundError(Exception):
    """Raised if input image does not exist
    """
    pass


def _parse_arguments(desc, args):
    """Parses command line arguments using argparse.
    """
    parsed_arguments = Parameters()

    help_formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=help_formatter)
    parser.add_argument("image", help='Image to convert')
    parser.add_argument("output", help='Output image path, should have .png'
                                       ' extension, if not .png will be '
                                       'appended')
    parser.add_argument("--equalize", action='store_true',
                        help='Run ImageOps.equalize on image'
                             'with no mask')
    parser.add_argument("--autocontrast", action='store_true',
                        help='Run ImageOps.autocontrast '
                             'on image with no mask')
    parser.add_argument("--gaussianblur", action='store_true')
    parser.add_argument("--downsample", help='Amount of downsampling to '
                                             'perform ie 2 means make '
                                             'image 50%% of original size'
                                             '(default 0)',
                        default=0, type=int)
    parser.add_argument("--gentiles", action='store_true',
                        help='Generate image tiles of size --tilesize'
                             ' storing results in <output> directory')
    parser.add_argument("--tilesize", type=int, default=128,
                        help='Sets tile size in pixels if --gentiles is set.'
                             '(default 128)')
    parser.add_argument("--log", dest="loglevel", choices=['DEBUG',
                        'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help="Set the logging level (default WARNING)",
                        default='WARNING')
    parser.add_argument('--version', action='version',
                        version=('%(prog)s ' + chmutil.__version__))

    return parser.parse_args(args, namespace=parsed_arguments)


def _convert_image(image_file, dest_file, theargs):
    """Convert image
    :raises NoInputImageFoundError: if input image file does not exist
    """
    if not os.path.isfile(image_file):
        raise NoInputImageFoundError('Image ' + image_file + ' not found')
    logger.debug('Opening file ' + image_file)

    img = Image.open(image_file)

    logger.info('Running ImageOps.grayscale')
    img = ImageOps.grayscale(img)

    if theargs.equalize is True:
        logger.info('Running ImageOps.equalize')
        img = ImageOps.equalize(img)

    if theargs.autocontrast is True:
        logger.info('Running ImageOps.autocontrast')
        img = ImageOps.autocontrast(img)

    if theargs.gaussianblur:
        logger.info('Running Image.filter Gaussian Blur')
        img = img.filter(ImageFilter.GaussianBlur())

    if theargs.downsample > 0:
        ds = int(theargs.downsample)
        logger.info('Downsampling by factor of ' + str(ds))
        img = img.resize((int(img.size[0]/ds), int(img.size[1]/ds)))

    if theargs.gentiles:
        logger.info('Generating tiles of size: ' + str(theargs.tilesize) +
                    ' pixels')
        outpath = os.path.abspath(theargs.output)

        if not os.path.isdir(outpath):
            logger.info('Creating directory: ' + outpath)
            os.makedirs(outpath, mode=0o755)
        return _generate_tiles(img, theargs.tilesize, outpath)

    if not dest_file.endswith('.png'):
        dest_file += '.png'
    img.save(dest_file, "PNG")
    return 0


def _generate_tiles(img, tilesize, output):
    """Generates square tiles from image of size `tilesize`
       storing results in `output` directory
    :param img: PIL image
    :param tilesize: size of tiles as int in pixels ie 128
    :param output: output directory to write results to. If directory
                   does not exist, it will be created.
    :param includepartialtiles: boolean if True then code will output
                                tiles with only partial data. Size of
                                output tiles will be set b
    :returns: 0 upon success or non zero for error
    """
    tilegen = RowColumnImageTileGenerator(tilesize)
    zoom = '0'
    for tile in tilegen.get_image_tiles(img):
        name = (zoom + '-r' + str(tile.get_row()) + '_c' +
                str(tile.get_col()) + '.png')
        fp = os.path.join(output, name)
        tile.get_image().save(fp)
        tile.get_image().close()
    return 0


def main(arglist):
    """Main function
    :param arglist: Should be set to sys.argv which is list of arguments
                    passed on commandline including script being run as arg 0
    :returns: exit code. 0 is success otherwise failure
    """
    desc = """
              Version {version}

              Given an image, code will convert that image to grayscale,
              then optionally autolevel, blur, and downsample the image
              saving it in png format.

              By default only the conversion ot grayscale is performed.

              Please note, regardless of order of optional flags the
              operations are performed in this order:

              1. Grayscale
              2. Equalize
              3. AutoContrast
              4. GaussianBlur
              5. Downsample
              6. Generate Tiles

              Example Usage:

              createchmimage.py someimage.tif someimage.png

              """.format(version=chmutil.__version__)

    theargs = _parse_arguments(desc, arglist[1:])
    theargs.program = arglist[0]
    theargs.version = chmutil.__version__
    core.setup_logging(logger, log_format=LOG_FORMAT,
                       loglevel=theargs.loglevel)
    try:
        return _convert_image(os.path.abspath(theargs.image),
                              os.path.abspath(theargs.output),
                              theargs)
    finally:
        logging.shutdown()


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
