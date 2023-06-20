from modules import launch_utils

args = launch_utils.args
prepare_environment = launch_utils.prepare_environment
start = launch_utils.start

def main():
    if not args.skip_prepare_environment:
        prepare_environment()

    start()

if __name__ == "__main__":
    main()
