# Installation

## The easy way

Install the pre-compiled version from GitHub:

```bash
$ pip install carabiner
```

If you want to use the `tensorflow`, `pandas`, or `matplotlib` utilities, these must be installed separately
or together:

```bash
$ pip install carabiner[deep]
# or
$ pip install carabiner[pd]
# or
$ pip install carabiner[mpl]
# or
$ pip install carabiner[all]
```

## From source

Clone the repository, then `cd` into it. Then run:

```bash
pip install -e .
```