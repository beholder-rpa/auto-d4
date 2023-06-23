# this scripts installs necessary requirements and launches main program in autod4.py
import subprocess
import os
import sys
import importlib.util
import platform
from functools import lru_cache

from modules import cmd_args
args, _ = cmd_args.parser.parse_known_args()

python = sys.executable
git = os.environ.get('GIT', "git")
index_url = os.environ.get('INDEX_URL', "")
dir_repos = "repositories"

# Whether to default to printing command output
default_command_live = (os.environ.get('WEBUI_LAUNCH_LIVE_OUTPUT') == "1")

def check_python_version():
    is_windows = platform.system() == "Windows"
    major = sys.version_info.major
    minor = sys.version_info.minor
    micro = sys.version_info.micro

    if is_windows:
        supported_minors = [10]
    else:
        supported_minors = [7, 8, 9, 10, 11]

    if not (major == 3 and minor in supported_minors):
        import modules.errors

        modules.errors.print_error_explanation(f"""
INCOMPATIBLE PYTHON VERSION

This program is tested with 3.10.6 Python, but you have {major}.{minor}.{micro}.
If you encounter an error with "RuntimeError: Couldn't install torch." message,
or any other error regarding unsuccessful package (library) installation,
please downgrade (or upgrade) to the latest version of 3.10 Python
and delete current Python and "venv" folder in auto-d4's directory.

You can download 3.10 Python from here: https://www.python.org/downloads/release/python-3106/

Use --skip-python-version-check to suppress this warning.
""")
 
@lru_cache()
def commit_hash():
    try:
        return subprocess.check_output([git, "rev-parse", "HEAD"], shell=False, encoding='utf8').strip()
    except Exception:
        return "<none>"

@lru_cache()
def git_tag():
    try:
        return subprocess.check_output([git, "describe", "--tags"], shell=False, encoding='utf8').strip()
    except Exception:
        return "<none>"

def run(command, desc=None, errdesc=None, custom_env=None, live: bool = default_command_live) -> str:
    if desc is not None:
        print(desc)

    run_kwargs = {
        "args": command,
        "shell": True,
        "env": os.environ if custom_env is None else custom_env,
        "encoding": 'utf8',
        "errors": 'ignore',
    }

    if not live:
        run_kwargs["stdout"] = run_kwargs["stderr"] = subprocess.PIPE

    result = subprocess.run(**run_kwargs)

    if result.returncode != 0:
        error_bits = [
            f"{errdesc or 'Error running command'}.",
            f"Command: {command}",
            f"Error code: {result.returncode}",
        ]
        if result.stdout:
            error_bits.append(f"stdout: {result.stdout}")
        if result.stderr:
            error_bits.append(f"stderr: {result.stderr}")
        raise RuntimeError("\n".join(error_bits))

    return (result.stdout or "")


def is_installed(package):
    try:
        spec = importlib.util.find_spec(package)
    except ModuleNotFoundError:
        return False

    return spec is not None

def run_pip(command, desc=None, live=default_command_live):
    if args.skip_install:
        return

    index_url_line = f' --index-url {index_url}' if index_url != '' else ''
    return run(f'"{python}" -m pip {command} --prefer-binary{index_url_line}', desc=f"Installing {desc}", errdesc=f"Couldn't install {desc}", live=live)


def check_run_python(code: str) -> bool:
    result = subprocess.run([python, "-c", code], capture_output=True, shell=False)
    return result.returncode == 0

def prepare_environment():
    torch_index_url = os.environ.get('TORCH_INDEX_URL', "https://download.pytorch.org/whl/cu118")
    torch_command = os.environ.get('TORCH_COMMAND', f"pip install torch torchvision torchaudio --extra-index-url {torch_index_url}")
    requirements_file = os.environ.get('REQS_FILE', "requirements.txt")

    if not args.skip_python_version_check:
        check_python_version()

    commit = commit_hash()
    tag = git_tag()

    print(f"Python {sys.version}")
    print(f"Version: {tag}")
    print(f"Commit hash: {commit}")

    if args.reinstall_torch or not is_installed("torch") or not is_installed("torchvision") or not is_installed("torchaudio"):
        run(f'"{python}" -m {torch_command}', "Installing torch", "Couldn't install torch", live=True)

    # if not args.skip_torch_cuda_test and not check_run_python("import torch; assert torch.cuda.is_available()"):
    #     raise RuntimeError(
    #         'Torch is not able to use GPU; '
    #         'add --skip-torch-cuda-test to COMMANDLINE_ARGS variable to disable this check'
    #     )

    run_pip(f"install -r \"{requirements_file}\"", "requirements")

    if "--exit" in sys.argv:
        print("Exiting because of --exit argument")
        exit(0)

def start():
    from autod4 import main
    main(args)