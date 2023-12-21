# 🪨 carabiner

![GitHub Workflow Status (with branch)](https://img.shields.io/github/actions/workflow/status/scbirlab/carabiner/python-publish.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/carabiner)
![PyPI](https://img.shields.io/pypi/v/carabiner)

Useful utilities.

## Installation

### The easy way

Install the pre-compiled version from GitHub:

```bash
pip install git+https://github.com/scbirlab/carabiner.git
```

If you want to use the `tensorflow` utilities, these must be installed separately:

```bash
pip install tensorflow
```

### From source

Clone the repository, then `cd` into it. Then run:

```bash
pip install -e .
```

## Usage

Import into python. For example:

```python
import carabiner as cbnr
from carabiner.pd import read_csv
from carabiner.tf import sparse_matmul
```

### Command line options

```bash
usage: cbnr [-h] [--format {TSV,CSV,tsv,csv}] [--output OUTPUT] [inputs [inputs ...]]

positional arguments:
  inputs

optional arguments:
  -h, --help            show this help message and exit
  --format {TSV,CSV,tsv,csv}, -f {TSV,CSV,tsv,csv}
                        Format of files. Default: TSV
  --output OUTPUT, -o OUTPUT
                        Output file. Default: STDOUT

```

## Issues, problems, suggestions

Add to the [issue tracker](https://www.github.com/carabiner/envs/issues).

## Documentation

Available at [ReadTheDocs](https://ogilo.readthedocs.org).