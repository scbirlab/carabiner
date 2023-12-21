# Usage

Import into python. For example:

```python
import carabiner as cbnr
from carabiner.pd import read_csv
from carabiner.tf import sparse_matmul
```

## Command line options

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
