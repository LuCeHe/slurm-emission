<div align="center">

<h1>📤 Slurm Emission</h1>

<p><strong>One shared SBATCH wrapper for every parameter combination, straight from Python.</strong></p>

<p>
  <a href="https://www.python.org/downloads/">Python 3.9+</a>
  &nbsp;·&nbsp;
  <a href="https://slurm.schedmd.com/">Slurm</a>
  &nbsp;·&nbsp;
  <a href="LICENSE">License: MIT</a>
</p>

<br/>

</div>

Slurm Emission is a small utility for [Slurm](https://slurm.schedmd.com/) clusters. It writes a single driver script with your directives and environment setup, expands experiment grids into CLI flags, and submits each run—ideal when many jobs differ only by arguments.

## Features
- Builds a single `.sh` driver with `#SBATCH` options and optional preamble (modules, `conda activate`, `cd`, etc.).
- Expands experiment definitions into a Cartesian product of parameter lists and calls `sbatch` for each combination.
- Optional deduplication, shuffling, subsetting, and “dry run” style workflows via `mock_send`.

## Requirements

- Python 3.9 or newer
- A Slurm cluster with `sbatch` available on your `PATH`
- A worker script that accepts the generated arguments (e.g. `argparse` flags like `--seed=0`)

## Installation

```bash
pip install slurm-emission
```

## Usage

Import `run_experiments` and pass:

1. A list of experiment dicts whose values are lists (or scalars); keys become argument names.
2. `sbatch_args`: mapping of Slurm option names (without `#SBATCH`) to values, e.g. `job-name`, `partition`, `gres`.
3. `bash_prelines`: shell commands run before the per-job command (modules, environment, working directory).
4. `init_command`: prefix for each job’s command (typically `python your_script.py`).

Generated batch scripts are written under **`~/.cache/slurm-emission/shs/`** by default (configurable with `sh_location`).

### Example

```python
from slurm_emission import run_experiments

script_path = "path/to/your/script"
script_name = "script.py"

sbatch_args = {
    "job-name": "example_1",
    "partition": "gpu",
    "gres": "gpu:1",
    "cpus-per-task": 4,
    "mem": "40G",
    "account": "your-account",
    "time": "23:00:00",
}

datasets = ["cifar", "mnist"]
models = ["transformer", "lstm"]

experiments = [
    {
        "seed": list(range(4)),
        "epochs": [300],
        "model": models,
        "dataset": datasets,
    }
]

load_modules = "module load conda"
activate_env = "conda activate llms"
py_location = f"cd {script_path}"
bash_prelines = f"{load_modules}\n{activate_env}\n{py_location}"

run_experiments(
    experiments,
    init_command=f"python {script_name}",
    sbatch_args=sbatch_args,
    bash_prelines=bash_prelines,
    id="llms",
)
```

Ensure `script.py` parses the emitted flags (by default `--key=value` style for `argparse`).

The generated driver looks like this (paths and timestamps will differ on your machine):

```bash
#!/bin/bash
#SBATCH --job-name=example_1
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=40G
#SBATCH --account=your-account
#SBATCH --time=23:00:00

module load conda
conda activate llms
cd path/to/your/script
$1
```

Slurm is invoked once per combination, passing the full command as the script’s first argument, for example:

```text
Number jobs: 16/16
1/16 sbatch ~/.cache/slurm-emission/shs/llms--2024-06-07--11-49-47--OukHy.sh 'python script.py --seed=0 --epochs=300 --model=transformer --dataset=cifar '
...
16/16 sbatch ~/.cache/slurm-emission/shs/llms--2024-06-07--11-49-47--OukHy.sh 'python script.py --seed=3 --epochs=300 --model=transformer --dataset=cifar '
Number jobs: 16/16
```

### Boolean flags (`##true##` / `##false##`)

When `clean_store_true_false=True` (the default), emitted commands are post-processed so you can sweep “on/off” flags that map to `argparse` `action="store_true"` / `store_false`-style CLIs without emitting awkward `=True` / `=False` pairs:

- **`=##true## `** → the `=##true## ` fragment is removed and replaced with a space, so `--use_amp=##true## ` becomes **`--use_amp `** (flag present, no value).
- **`--flag=##false## `** → the whole **`--flag=##false## `** token is stripped so the flag is omitted from the command.

Use **letters, digits, and underscores only** in the parameter name (the implementation matches `--\w+=##false##`).

```python
experiments = [
    {
        "epochs": [3],
        "use_amp": ["##true##", "##false##"],
        "log_every": [100],
    }
]

run_experiments(
    experiments,
    init_command="python train.py",
    sbatch_args=sbatch_args,
    bash_prelines=bash_prelines,
    id="bool-sweep",
)
```

Roughly equivalent printed commands (after cleanup and whitespace normalization):

```text
… 'python train.py --epochs=3 --use_amp --log_every=100 '
… 'python train.py --epochs=3 --log_every=100 '
```

Set `clean_store_true_false=False` if you want the raw `--use_amp=##true##` strings left unchanged.

See `run_experiments` in `slurm_emission.submit_jobs` for additional options (`mock_send`, `subset`, `prevent`, `remove_duplicates`, etc.).

## License

This project is released under the [MIT License](LICENSE).

## Links

- [Repository](https://github.com/lucehe/slurm-emission)
- [Issue tracker](https://github.com/lucehe/slurm-emission/issues)
