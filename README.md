# kumade

A make-like build utility for Python.

Features:

- You can define tasks, such as executing commands, creating files,
  or invoking functions, in `Kumadefile.py`, with standard Python code.
- You can run tasks from shell with `kumade` command.
- Any task can have its dependencies and kumade considers the dependency graph
  to determin the task execution order.
- Kumade decides whether or not to perform a file creation task with considering
  the file existence and whether its timestamp is older than its dependencies.

*Kumade* means rake in Japanese, and it is regarded as a lucky charm
because it collects happiness.


## Getting started

### Install

To install kumade, use pip:

```console
pip install kumade
```

### Write `Kumadefile.py`

To define tasks, write `Kumadefile.py`.

For example,

```python
import kumade as ku

from pathlib import Path
import subprocess

ku.set_default("greet")

help_file = Path("help.txt")

@ku.task("greet")
@ku.depend(help_file)
def greeting() -> None:
    print("Hi, this is Kumade.")
    print(f"See {help_file}.")

@ku.file(help_file)
def create_help_file() -> None:
    with help_file.open("w") as outfile:
        subprocess.run(["kumade", "-h"], stdout=outfile)
```

This example defines two tasks and sets default task.

The task "greet" is defined by the decorator `@ku.task("greet")`
and it will output a greeting when executed.
This task depends on the file "help.txt" and
kumade will execute the file creation task if it does not exist.

The file creation task for "help.txt" is defined by the decorator
`@ku.file(help_file)` and it will create the file by capturing
the standard output of command execution.

You can see more examples of task definition in the file
[Kumadefile.py](https://github.com/yamaimo/kumade/blob/main/Kumadefile.py)
in the [kumade](https://github.com/yamaimo/kumade) repository.

### Run

To run tasks from shell, use `kumade` command:

```console
kumade
```

`kumade` command loads task definitions from `Kumadefile.py` and
runs the specified tasks (or the default task if no task is specified).

Run `kumade --help` to see available options.


## For development

### Install

You can install this package from GitHub directly:

```console
pip install git+ssh://git@github.com/yamaimo/kumade.git
```

Or, to develop, install from a cloned repository as follows:

```console
# clone repository
git clone git@github.com:yamaimo/kumade.git
cd kumade

# create venv and activate it
python3.11 -m venv venv
source venv/bin/activate

# install this package as editable with dependencies
pip install -e .[develop]
```

### Format and Lint

To format, execute `kumade format`.

To lint, execute `kumade lint`.

### Coverage

To measure coverage and report it, execute `kumade report_coverage`.
