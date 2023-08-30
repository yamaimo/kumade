# Example of Kumadefile.py

import subprocess
from pathlib import Path
from time import sleep

import kumade as ku


# demo -----------------------------------------------------

# default

ku.set_default("greet")

# simple task

@ku.task("greet")
@ku.help("Greet all.")
def greeting() -> None:
    print(
        "Hi, this is Kumade.\n"
        "A make-like build utility for Python.\n"
        "Enjoy!"
    )

# create task dynamically

for i in range(6):
    @ku.task(f"count{i}")
    @ku.depend(f"count{i+1}" if i < 5 else None)
    @ku.bind_args(i)
    def count(value: int) -> None:
        if value > 0:
            print(f"{value}...", end="", flush=True)
            sleep(1)
        else:
            print(f"{value}!")

@ku.task("countdown")
@ku.depend("count0")
@ku.help("Count down from 5 to 0.")
def countdown() -> None:
    pass

# file creation

project_dir = Path(__file__).parent
demo_dir = project_dir / "demo"
demo_file = demo_dir / "demo.txt"

@ku.task("build")
@ku.depend(demo_file)
@ku.help("Create demo file.")
def build() -> None:
    pass

@ku.file(demo_file)
@ku.depend(demo_dir)
def create_demo_file() -> None:
    demo_file.touch()

ku.directory(demo_dir)

# clean

ku.clean("clean", [demo_dir], help="Clean demo file.")


# format, lint, and test -----------------------------------

@ku.task("format")
@ku.help("Format code by pysen.")
def format() -> None:
    subprocess.run(["pysen", "run", "format"])

@ku.task("lint")
@ku.help("Lint code by pysen.")
def lint() -> None:
    subprocess.run(["pysen", "run", "lint"])

@ku.task("test")
@ku.help("Run unittest.")
def test() -> None:
    subprocess.run(["python", "-m", "unittest"])


# coverage -------------------------------------------------

coverage_path = project_dir / ".coverage"
kumade_dir = project_dir / "kumade"
tests_dir = project_dir / "tests"
python_sources = list(kumade_dir.glob("**/*.py")) + list(tests_dir.glob("**/*.py"))

@ku.task("coverage")
@ku.help("Measure code coverage.")
@ku.depend(coverage_path)
def coverage() -> None:
    pass

@ku.file(coverage_path)
@ku.depend(*python_sources)
def make_coverage() -> None:
    subprocess.run(["coverage", "run", "-m", "unittest"])
    coverage_path.touch()

@ku.task("report_coverage")
@ku.depend("coverage")
@ku.help("Report coverage result.")
def report_coverage() -> None:
    subprocess.run(["coverage", "report", "-m"])

ku.clean("clean_coverage", [coverage_path], help="Clean coverage files.")


# build and upload -----------------------------------------

dist_dir = project_dir / "dist"
wheel_path = dist_dir / f"kumade-{ku.__version__}-py3-none-any.whl"
tgz_path = dist_dir / f"kumade-{ku.__version__}.tar.gz"
built_timestamp_path = dist_dir / f"built_{ku.__version__}"

@ku.task("package.build")
@ku.depend(wheel_path, tgz_path)
@ku.help("Build kumade package.")
def build_package() -> None:
    pass

@ku.file(wheel_path)
@ku.depend(built_timestamp_path)
def create_wheel() -> None:
    pass

@ku.file(tgz_path)
@ku.depend(built_timestamp_path)
def create_tgz() -> None:
    pass

@ku.file(built_timestamp_path)
@ku.depend(*python_sources)
def execute_build() -> None:
    subprocess.run(["python", "-m", "build"], check=True)
    built_timestamp_path.touch()

@ku.task("package.upload")
@ku.depend("package.build")
@ku.help("Upload kumade package.")
def upload_package() -> None:
    subprocess.run(["twine", "upload", str(wheel_path), str(tgz_path)], check=True)
