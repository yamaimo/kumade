# Example of Kumadefile.py

import subprocess
from pathlib import Path
from time import sleep

import kumade as ku
from example_for_import import SomeUsefulTask
from kumade.runner import TaskRunner

# demo -----------------------------------------------------

# default

ku.set_default("greet")

# simple task


@ku.task("greet")
@ku.help("Greet all.")
def greeting() -> None:
    print("Hi, this is Kumade.\n" "A make-like build utility for Python.\n" "Enjoy!")


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


# use imported class


@ku.task("import_example")
@ku.help("Execute example task which uses imported class.")
def execute_import_example() -> None:
    task = SomeUsefulTask("example task")
    task.execute()


# use config value

ku.add_str_config("name", "Name for greet_to_you task.", default_value="John")


@ku.task("greet_to_you")
@ku.help("Greet to specified name.")
def greet_to_you() -> None:
    config = ku.get_config()
    print(f"Hi, {config.name}!\n" "Enjoy kumae!!")


# define tasks using config and run it in task procedure

ku.add_int_config("count", "Number for countdown_with_config task.", default_value=10)


@ku.task("countdown_with_config")
@ku.help("Count down from specified number to 0.")
def define_countdown_tasks_and_run() -> None:
    config = ku.get_config()

    for i in range(config.count + 1):

        @ku.task(f"dynamic_count{i}")
        @ku.depend(f"dynamic_count{i+1}" if i < config.count else None)
        @ku.bind_args(i)
        def count(value: int) -> None:
            if value > 0:
                print(f"{value}...", end="", flush=True)
                sleep(1)
            else:
                print(f"{value}!")

    @ku.task("dynamic_countdown")
    @ku.depend("dynamic_count0")
    def countdown() -> None:
        pass

    runner = TaskRunner()
    runner.run(["dynamic_countdown"])


# format, lint, and test -----------------------------------


@ku.task("format")
@ku.help("Format code by pysen.")
def format() -> None:
    subprocess.run(["pysen", "run", "format"])


@ku.task("lint")
@ku.help("Lint code by pysen.")
def lint() -> None:
    subprocess.run(["pysen", "run", "lint"])


ku.add_bool_config(
    "test_each",
    "Set true if you want to run each test file.",
)

ku.add_bool_config(
    "test_verbose",
    "Run unit test with verbose output if true.",
)


@ku.task("test")
@ku.help("Run unittest.")
def test() -> None:
    config = ku.get_config()
    if config.test_verbose:
        subprocess.run(["python", "-m", "unittest", "-v"])
    else:
        subprocess.run(["python", "-m", "unittest"])


tests_dir = project_dir / "tests"
for test_path in tests_dir.glob("**/test_*.py"):
    execute_test_task = f"execute_{test_path}"

    @ku.file(test_path)
    @ku.depend(execute_test_task)
    def dummy() -> None:
        pass

    @ku.task(execute_test_task)
    @ku.bind_args(test_path)
    def execute_one_test(path: Path) -> None:
        config = ku.get_config()
        if config.test_each:
            print(f"execute {path.relative_to(project_dir)}")
            if config.test_verbose:
                subprocess.run(["python", "-m", "unittest", "-v", str(path)])
            else:
                subprocess.run(["python", "-m", "unittest", str(path)])


# coverage -------------------------------------------------

coverage_path = project_dir / ".coverage"
kumade_dir = project_dir / "kumade"
python_sources = list(kumade_dir.glob("**/*.py")) + list(tests_dir.glob("**/*.py"))


@ku.task("coverage")
@ku.depend(coverage_path)
@ku.help("Report coverage result.")
def report_coverage() -> None:
    subprocess.run(["coverage", "report", "-m"])


@ku.file(coverage_path)
@ku.depend(*python_sources)
def make_coverage() -> None:
    # NOTE: Exclude test Kumadefiles that are copied to temporary directory
    # and deleted at the end of test.
    subprocess.run(["coverage", "run", "--omit", "Kumadefile.py", "-m", "unittest"])
    coverage_path.touch()


ku.clean("coverage.clean", [coverage_path], help="Clean coverage files.")


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
