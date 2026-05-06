import argparse
import os


def export_python_files(
    base_path: str, output="exported.md", extra_ignored: set[str] | None = None
):
    ignored_dirs = {".venv", "__pycache__", ".git", "tests", "scripts"}

    if extra_ignored:
        ignored_dirs |= extra_ignored

    with open(output, "w", encoding="utf-8") as f_out:
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]

            for file in files:
                if file.endswith(".py") and file != "export_scripts.py":
                    full_path = os.path.join(root, file)
                    script_path = os.path.relpath(full_path, ".")

                    try:
                        with open(full_path, encoding="utf-8") as f_in:
                            content = f_in.read()

                        f_out.write(f"{script_path}\n```python\n" + content + "\n```\n\n")
                        print(f"exported: {script_path}")
                    except Exception as e:  # noqa: BLE001
                        print(f"Failed to read {script_path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Export all python files into a markdown document."
    )

    parser.add_argument(
        "--base",
        "-b",
        default=".",
        help="Base directory to scan (default: current working directory)",
    )

    parser.add_argument(
        "--output",
        "-o",
        default="exported.md",
        help="Output markdown file (default: exported.md)",
    )

    parser.add_argument(
        "--ignore",
        "-i",
        nargs="*",
        default=[],
        help="Additional directories to ignore",
    )

    args = parser.parse_args()

    base_path = os.path.abspath(args.base)

    if not os.path.exists(base_path):
        print(f"Base path does not exist: {base_path}")
        return

    export_python_files(
        base_path=base_path,
        output=args.output,
        extra_ignored=set(args.ignore),
    )


if __name__ == "__main__":
    main()
