from watchdog.observers import Observer
from handbrake import Handbrake
import os
import time
import argparse


def validate_arg_path(path):
    if os.path.exists(path):
        return os.path.abspath(path)
    else:
        raise argparse.ArgumentError(f'{path} doesn\'t exist.')


def parse_args():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--dir', dest='dir_to_monitor', type=validate_arg_path,
                        help='Directories to monitor.', required=True)
    parser.add_argument('--handbrake', dest='handbrake_path', type=validate_arg_path,
                        default="C:\Program Files\HandBrake\HandBrakeCLI.exe")
    parser.add_argument('--transcode_dir', dest='transcode_dir', type=validate_arg_path,
                        help='Directories to transcode in.', required=True)
    parser.add_argument('--preset_path', dest='preset_path', type=validate_arg_path,
                        help='Handbrake preset path', required=True)
    parser.add_argument('--preset_name', dest='preset_name', type=str,
                        help='Handbrake preset name', required=True)
    parser.add_argument('--4k', dest='process_uhd', type=bool, default=False,
                        help='Process 4k and/or HDR10')
    parser.add_argument('--time', dest='time', type=int, default=75,
                        help='Time to wait after new directory is detected.')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    event_handler = Handbrake(args=args)
    observer = Observer()
    observer.schedule(event_handler, args.dir_to_monitor, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
