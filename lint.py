import os
import subprocess
import sys


def run_black(directories):
    for directory in directories:
        print(f"Running black for {directory}...")
        subprocess.run(["black", directory])


def run_flake8(directories):
    for directory in directories:
        print(f"Linting {directory}...")
        subprocess.run(["flake8", directory])


def run_autopep8(directories):
    for directory in directories:
        print(f"Formatting {directory}...")
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    result = subprocess.run(
                        [
                            "autopep8",
                            "--in-place",
                            "--aggressive",
                            "--aggressive",
                            "--max-line-length",
                            "88",
                            # "--diff",
                            file_path,
                        ],
                        capture_output=True,
                        text=True,
                    )
                    if result.stderr:
                        print(f"Error processing {file_path}: {result.stderr}")
                    elif result.stdout:
                        print(f"File {file_path} was modified.")


def main(*args):
    # Define default directories
    default_directories = ["app", "lib"]

    # Use provided arguments or default directories
    directories = args if args else default_directories

    run_autopep8(directories)
    run_black(directories)
    run_flake8(directories)


if __name__ == "__main__":
    # Capture arguments from the command line
    directories = sys.argv[1:]
    main(*directories)
