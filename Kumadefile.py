# Example of Kumadefile.py

import subprocess
from pathlib import Path
from time import sleep

import kumade as ku

# demo -----------------------------------------------------

@ku.task("greet")
@ku.help("Greet all.")
def greeting() -> None:
    print(
        "Hi, this is Kumade.\n"
        "A make-like build utility for Python.\n"
        "Enjoy!"
    )

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

project_dir = Path(__file__).parent
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

@ku.task("report_coverage")
@ku.depend("coverage")
@ku.help("Report coverage result.")
def report_coverage() -> None:
    subprocess.run(["coverage", "report", "-m"])

clean_coverage = ku.create_clean_task("clean_coverage", "Clean coverage files.")
clean_coverage.append(coverage_path)