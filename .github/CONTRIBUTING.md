# Contributing to @axa-fr/axa-fr-splitter

First, ensure you have using Python 3.10.

To get started with the repository:

```sh
git clone https://github.com/AxaFrance/axa-fr-splitter.git
cd axa-fr-splitter
```

## Setup / Installation

First, create a virtual environment and install requirements:

``` bash
python -m venv .venv --prompt axa-fr-splitter
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements-dev.in
```

Then, you need to install the pacakge in **editable/development mode** (This allows you to modify your packages' source code and have the changes take effect without you having to rebuild and reinstall) by using the following command:

```bash
pip install -e .
```

You are now ready to contribute!

## Project Architecture

The source code is organized in two directories:

- **src**: the source code for the package(s) in the project
- **tests**: A set of unit tests for the project


## Running Tests
Run unit tests with:

``` bash
python -m pytest
```

## Pull Request

Please respect the following [PULL_REQUEST_TEMPLATE.md](./PULL_REQUEST_TEMPLATE.md)

## Issue

Please respect the following [ISSUE_TEMPLATE.md](./ISSUE_TEMPLATE.md)
