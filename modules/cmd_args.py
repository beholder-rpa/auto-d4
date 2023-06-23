import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--skip-python-version-check", action='store_true', help="launch.py argument: do not check python version")
parser.add_argument("--skip-torch-cuda-test", action='store_true', help="launch.py argument: do not check if CUDA is able to work properly")
parser.add_argument("--skip-prepare-environment", action='store_true', help="launch.py argument: skip all environment preparation")
parser.add_argument("--skip-install", action='store_true', help="launch.py argument: skip installation of packages")
parser.add_argument("--reinstall-torch", action='store_true', help="launch.py argument: install the appropriate version of torch even if you have some version already installed")

# app arguments
parser.add_argument("-f", "--target-fps", type=int, help="target fps", default=6)
parser.add_argument("-d", "--debug", action="store_true")
parser.add_argument('--cpu', default=True, action='store_false', dest='use_cuda',
                        help='run on cpu if not provided the program will run on gpu.')