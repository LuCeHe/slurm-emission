import os, itertools, string, socket, random
from datetime import datetime, timedelta
import numpy as np


def run_experiments(
        experiments=None, subset=[0, None], init_command='python language_main.py ',
        run_string=None, is_argparse=True, sh_save_dir='', account='',
        duration={'days': 0, 'hours': 12, 'minutes': 0, 'prestop_training_hours': -1},
        n_gpus=0, id='', mem='8G', cpus_per_task=2, mock_send=False,
        bash_prelines='',
        shs_config_lines=None,
):
    """
    :param experiments: list of dictionaries, each dictionary contains the hyperparameters to be tested
    :param subset: list of two integers, the first is the start index and the second is the end index
    :param init_command: the command to be run for each experiment
    :param run_string: in case you want to run the experiment without sbatch for example
    :param is_argparse: if the init_command has argparse arguments, so -- has to be added
    :param sh_save_dir: the directory to save the .sh that will control the jobs
    :param account: the account to be used in the sbatch
    :param duration: the duration of the job
    :param n_gpus: the number of gpus to be used
    :param id: the id of the job
    :param mem: the memory to be used
    :param cpus_per_task: the number of cpus per task
    :param mock_send: if you want to print the commands instead of running them
    :param bash_prelines: the bash lines to be run before the experiment
    :param shs_config_lines: the sbatch lines to be run before the experiment, if you want to parameters that are not
    in our default configuration
    """
    delta = timedelta(days=duration['days'], hours=duration['hours'], minutes=duration['minutes'])

    hours, remainder = divmod(delta.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)
    sh_duration = "{}:{}:00".format(str(int(hours)).zfill(2), str(int(minutes)).zfill(2))

    if run_string is None:
        sh_name = create_sbatch_sh(sh_duration, sh_save_dir, account, n_gpus, id, mem=mem,
                                   cpus_per_task=cpus_per_task, bash_prelines=bash_prelines,
                                   shs_config_lines=shs_config_lines)
        run_string = 'sbatch ' + sh_name

    if not experiments is None:
        ds = dict2iter(experiments)

    else:
        ds = ['']

    if isinstance(subset, dict):
        servers = [k for k, v in subset.items()]
        probs = [v for k, v in subset.items()]
        cumprobs = np.cumsum(probs)

        amount = len(ds)
        server_found = False
        for i, server in enumerate(servers):
            if server in socket.gethostname():
                server_found = True
                if not probs[i] == 0:
                    cp = cumprobs[i]
                    cp_1 = cumprobs[i - 1] if i > 0 else 0
                    from_ = int(cp_1 * amount)
                    to_ = int(cp * amount)

                    if cp == 1:
                        to_ = None

                    if cp_1 == 1:
                        from_ = None
                    subset = [from_, to_]
                else:
                    subset = [0, 0]
                break

        if not server_found:
            subset = [0, 0]

    random.seed(0)
    random.shuffle(ds)

    ods = ds
    ds = ds[subset[0]:subset[1]]

    if len(ds) > 0:
        print(f'Number jobs: {len(ds)}/{len(ods)}')
        for i, d in enumerate(ds):
            if not experiments is None:
                a = '--' if is_argparse else ''
                config_update = ''.join([a + '{}={} '.format(k, v) for k, v in d.items()])
                command = init_command + config_update
            else:
                command = init_command

            command = "{} '{}'".format(run_string, command + stop_training)
            command = command.replace('  ', ' ')
            print('{}/{}'.format(i + 1, len(ds)), command)
            if not mock_send:
                os.system(command)
        print(f'Number jobs: {len(ds)}/{len(ods)}')

    print(subset)
    print(socket.gethostname())


def dict2iter(experiments, to_list=False):
    full_ds = []
    for experiment in experiments:
        c = list(itertools.product(*experiment.values()))
        ds = [{k: v if not to_list else [v] for k, v in zip(experiment.keys(), i)} for i in c]
        full_ds.extend(ds)
    return full_ds


def create_sbatch_sh(
        duration, sh_location, account, n_gpus, id, mem='32G', cpus_per_task=4,
        bash_prelines='', shs_config_lines=None):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    rand_5 = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

    sh_name = f'{id}--' + now + rand_5 + '.sh'
    sh_path = os.path.join(sh_location, sh_name)
    with open(sh_path, 'w') as f:
        sh_string = sh_base(
            duration, account, n_gpus, mem, cpus_per_task=cpus_per_task,
            bash_prelines=bash_prelines, shs_config_lines=shs_config_lines
        )
        f.write(sh_string)
    return sh_path


def sh_base(
        time, account, n_gpus, mem='32G', cpus_per_task=4,
        bash_prelines='module load gcc/9.3.0 arrow cuda/11.1 python/3.9 scipy-stack StdEnv/2020',
        shs_config_lines=None
):
    gpus_line = '' if n_gpus == 0 else f'#SBATCH --gres=gpu:{n_gpus}'
    if shs_config_lines is None:
        shs_config_lines = f"""
#SBATCH --time={time}
#SBATCH --account={account}
#SBATCH --mem {mem}
#SBATCH --cpus-per-task {cpus_per_task}
{gpus_line}
"""
    return f"#!/bin/bash{shs_config_lines}\n{bash_prelines}\n$1"
