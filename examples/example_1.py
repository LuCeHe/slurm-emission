import os

from slurm_emission import run_experiments

CDIR = os.path.dirname(os.path.abspath(__file__))
SHDIR = os.path.join(CDIR, 'sh')
os.makedirs(SHDIR, exist_ok=True)

script_path = 'path/to/your/script'
script_name = 'script.py'
n_gpus = 1
mem = '40G'
cpus_per_task = 4

id = 'transformers'
account = 'def-lherrtti'

experiments = []

datasets = ['cifar', 'mnist']
models = ['transformer', 'lstm']

experiment = {
    'seed': [s + 0 for s in range(4)],
    'epochs': [300], 'model': models, 'dataset': datasets
}
experiments.append(experiment)

env_location = f'conda activate ssms'
load_modules = 'module unload cudatookit; module load conda'
py_location = f'cd {script_path}'
bash_prelines = f'{load_modules}\n{env_location}\n{py_location}'

run_experiments(
    experiments,
    init_command=f'python {script_name} ',
    bash_prelines=bash_prelines,
    sh_save_dir=SHDIR,
    id=id,
    duration={'days': 0, 'hours': 23, 'minutes': 00},
    account=account,
    n_gpus=n_gpus,
    mem=mem,
    cpus_per_task=cpus_per_task,
    mock_send=True,
)
