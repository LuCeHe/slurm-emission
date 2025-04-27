# SLURM emission

For those of you who use heavily High Performance Computing (HPC) clusters that depend on SLURM, 
you might have noticed that submitting jobs to the cluster can be a bit of a hassle. 
This is especially true when you have to submit multiple jobs with similar 
scripts but different parameters. Fortunately, `slurm_emission` comes for the rescue. In fact,

- it automates the creation of the sh file
- and it simplifies the submission of jobs to the cluster when the scripts to reuse are similar, 
and only the parameters change

I use it constantly so I thought it might be useful for you as well.

## Example

Here we go in detail through what you can find in the `example_1` script. Let's
import first the necessary modules, and create a folder where the code will save the 
sh file.


```python
import os
from slurm_emission import run_experiments

CDIR = os.path.dirname(os.path.abspath(__file__))
SHDIR = os.path.join(CDIR, 'sh')
os.makedirs(SHDIR, exist_ok=True)
```

Then, we define the parameters of the jobs, the number of gpus, cpus and memory we'll need. 
Also, we want to repeat the experiments for several settings, in this case, we have two datasets, 
two models, and four seeds.
We define also the script location and the name of the script to run. 

```python

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
```


Finally, we define the bash lines that will go in the sh, which are the lines that will be executed before the script, and
then we submit the jobs.


```python

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
```


The output of this script will be a .sh file with the following inside

```commandline
#!/bin/bash
#SBATCH --job-name=example_1
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=40G
#SBATCH --account=1230e98kal
#SBATCH --time=23:00:00

module unload cudatookit; module load conda
conda activate llms
cd path/to/your/script
$1
```

that will be used by all the jobs that will be submitted:

```commandline
Number jobs: 16/16
1/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=2 --epochs=300 --model=lstm --dataset=cifar '
2/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=3 --epochs=300 --model=lstm --dataset=cifar '
3/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=1 --epochs=300 --model=transformer --dataset=mnist '
4/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=0 --epochs=300 --model=transformer --dataset=mnist '
5/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=2 --epochs=300 --model=transformer --dataset=mnist '
6/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=0 --epochs=300 --model=lstm --dataset=cifar '
7/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=0 --epochs=300 --model=lstm --dataset=mnist '
8/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=2 --epochs=300 --model=lstm --dataset=mnist '
9/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=3 --epochs=300 --model=transformer --dataset=mnist '
10/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=1 --epochs=300 --model=lstm --dataset=mnist '
11/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=2 --epochs=300 --model=transformer --dataset=cifar '
12/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=1 --epochs=300 --model=transformer --dataset=cifar '
13/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=0 --epochs=300 --model=transformer --dataset=cifar '
14/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=1 --epochs=300 --model=lstm --dataset=cifar '
15/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=3 --epochs=300 --model=lstm --dataset=mnist '
16/16 sbatch cdir\sh\llms--2024-06-07_11-49-47OukHy.sh 'python script.py --seed=3 --epochs=300 --model=transformer --dataset=cifar '
Number jobs: 16/16
```

Hope it helps!