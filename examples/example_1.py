import os

from slurm_emission import run_experiments

CDIR = os.path.dirname(os.path.abspath(__file__))
SHDIR = os.path.join(CDIR, 'sh')
os.makedirs(SHDIR, exist_ok=True)

script_path = 'path/to/your/script'
script_name = 'script.py'

sbatch_args = {
    'job-name': 'example_1',
    'partition': 'gpu',
    'gres': 'gpu:1',
    'cpus-per-task': 4,
    'mem': '40G',
    'account': '1230e98kal',
    'time': '23:00:00',
}

id = 'llms'

experiments = []

datasets = ['cifar', 'mnist']
models = ['transformer', 'lstm']

experiment = {
    'seed': list(range(4)),
    'epochs': [300], 'model': models, 'dataset': datasets
}
experiments.append(experiment)

env_location = f'conda activate llms'
load_modules = 'module unload cudatookit; module load conda'
py_location = f'cd {script_path}'
bash_prelines = f'{load_modules}\n{env_location}\n{py_location}'

run_experiments(
    experiments,
    init_command=f'python {script_name} ',
    sbatch_args=sbatch_args,
    bash_prelines=bash_prelines,
    sh_location=SHDIR,
    id=id,
)
