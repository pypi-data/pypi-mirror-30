"""
Argument parser for the duo method
"""

import argparse
from .control import control_main
from .rov import rov_main
from edurov.utils import valid_resolution, args_resolution_help, STANDARD_RESOLUTIONS

def main(args=None):
    choices = {'control': control_main, 'rov': rov_main}
    parser = argparse.ArgumentParser(
        description='Stream video from picamera to machine on same network',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        'role',
        choices=choices,
        help='which role to play')
    parser.add_argument(
        'ip',
        help="""IP address the server listens at and ROV sends to\nuse "" for server to listen at all ports""",
        type=str)
    parser.add_argument(
        '-p',
        metavar='PORT',
        type=int,
        default=1060,
        help='IP port (default 1060)')
    parser.add_argument(
        '-r',
        metavar='RESOLUTION',
        type=str,
        default='1024x768',
        help='''resolution, use format WIDTHxHEIGHT or an integer 0-{}\n(default 1024x600)'''.format(
            len(STANDARD_RESOLUTIONS) - 1))
    parser.add_argument(
        '-f',
        action="store_true",
        help='when used, video will show in fullscreen')
    parser.add_argument(
        '--resolutions',
        action="store_true",
        help='print the resolutions to use with the -r flag')

    args = parser.parse_args()
    if args.resolutions:
        args_resolution_help()

    res = valid_resolution(args.r)

    function_ = choices[args.role]
    if function_ is rov_main:
        rov_main(
            host=args.ip,
            port=args.p,
            resolution=res)
    elif function_ is control_main:
        control_main(
            ip=args.ip,
            port=args.p,
            resolution=res,
            fullscreen=args.f)

if __name__ == '__main__':
    main()
