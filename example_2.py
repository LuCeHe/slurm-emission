n_gpus = 1
time = '00:59:00'
account = 'def-lherrtti'
mem = '40G'

hashsbatch_prelines = f"""
#SBATCH -N 1
#SBATCH -C gpu
#SBATCH -G {n_gpus}
#SBATCH -q shared
#SBATCH --time={time}
#SBATCH --account={account}
#SBATCH --mem {mem}
"""

import os

from slurm_sender.submit_jobs import run_experiments

CDIR = os.path.dirname(os.path.abspath(__file__))
SHDIR = os.path.join(CDIR, 'sh')
os.makedirs(SHDIR, exist_ok=True)

script_path = 'path/to/your/script'
script_name = 'script.py'

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

id = 'transformers'

run_experiments(
    experiments,
    init_command=f'python {script_name} ',
    bash_prelines=bash_prelines,
    sh_save_dir=SHDIR,
    id=id,
    hashsbatch_prelines=hashsbatch_prelines,
    mock_send=True,
)
