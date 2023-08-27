# kumade

A make-like build utility for Python.

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
