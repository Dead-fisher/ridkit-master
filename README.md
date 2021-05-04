# ridkit-master

## Introduction

ridkit is a python package for enhanced sampling via RiD(Reinforced Dynamics) method.

## Installation

#### install dependence
ridkit will need a specific software environment. We pack a easy-installed shell file located in env install.
~~~
cd env
sh rid.sh
~~~
Now you have all dependence of RiD (Gromacs, Tensorflow and a conda environment).
~~~
cd ritkit-master
python setup.py install
~~~
Open python, try `import ridkit`.

Install successfully if you get no error.

## Quick Start
We offer a simple but complete example in `ridkit/examples`

Try:
```
cd examples
python test.py
```

To begin with, you should offer a rid configeration file(rid.json), a CV file(phipsi_selected.json) and a dictory(mol/) containing initial conformation files in detail, and the number of conformation files should be equal to the number of walkers for parallel.

All these files are presented in `examples` dictory where the users can adjust the parameter as their will.



## Main procedure of RiD

RiD will run in iterations. Every iteration contains tasks below:

1. Biased MD;
2. Restrained MD;
3. Training neuro network.

#TODO

#### a. Biased MD

Just like Metadynamics, RiD will sample based on a bias potential given by NN models. A uncertainty indicator will direct the process of adding bias potential.

#### b. Restrained MD

This procedure will calculate mean force based on the sampling results, which can generate data set for training. 

#### c. Neuro network training

A fully connected NN will be trained via sampling data. This network will generate a map from selected CV to free energy.

A more detail description of RiD is published now, please see:

>  J. Chem. Phys. **148**, 124113 (2018); https://doi.org/10.1063/1.5019675



 # RiD settings



Two necessary json files are required to get start a RiD procedure.

1. rid.json for configuration of simulation.
2. cv.json for specifying CV.

### rid.json

| parameters | description | default |
| :----: | :----: | :----: |
| _comment | * | That's all |
| gmx_prep | * | gmx grompp -maxwarn 1 |
| gmx_run | * | gmx mdrun -ntmpi 1 |
| gmx_split_traj | * | echo 0 | gmx trjconv -sep -f traj.trr -o confs/conf.gro -vel |
| template_dir | * | ./template |
| init_graph | * | [] |
| numb_iter | * | 3 |
| bf_traj_stride | * | 500 |
| numb_walkers | * | 2 |
| bias_trust_lvl_1 | * | 2 |
| bias_trust_lvl_2 | * | 3 |
| bias_nsteps | * | 20000 |
| bias_frame_freq | * | 20 |
| sel_threshold | * | 2 |
| cluster_threshold | * | 1.5 |
| num_of_cluster_threshhold | * | 8 |
| max_sel | * | 30 |
| bias_dt | * | 0.002 |
| bias_temperature | * | 320 |
| res_nsteps | * | 25000 |
| res_frame_freq | * | 50 |
| res_dt | * | 0.002 |
| res_temperature | * | 320 |
| res_kappa | * | 500 |
| res_traj_stride | * | 500 |
| res_ang_stride | * | 5 |
| res_prt_file | * | plm.res.out |
| res_cmpf_error | * | False |
| init_numb_cluster_upper | * | 26 |
| init_numb_cluster_lower | * | 16 |
| conf_start | * | 0 |
| conf_every | * | 1 |
| numb_model | * | 4 |
| neurons | * | [256, 128, 64, 32] |
| resnet | * | True |
| batch_size | * | 128 |
| numb_epoches | * | 2000 |
| starter_lr | * | 0.0008 |
| decay_steps | * | 120 |
| decay_rate | * | 0.96 |
| res_iter | * | 13 |
| res_numb_epoches | * | 2000 |
| res_starter_lr | * | 0.0008 |
| res_olddata_ratio | * | 7 |
| res_decay_steps | * | 120 |
| res_decay_rate | * | 0.96 |
| machine_type | * | Slurm |
| queue_name | * | GPU_2080Ti |
| cleanup | * | True |
| enhc_thread | * | 8 |
| res_thread | * | 8 |
| train_thread | * | 8 |
| enhc_number_node | * | 1 |
| enhc_cpu_per_node | * | 8 |
| enhc_gpu_per_node | * | 1 |
| enhc_group_size | * | 1 |
| post_number_node | * | 1 |
| post_cpu_per_node | * | 4 |
| post_gpu_per_node | * | 0 |
| post_group_size | * | 1 |
| res_number_node | * | 1 |
| res_cpu_per_node | * | 8 |
| res_gpu_per_node | * | 1 |
| res_group_size | * | 10 |
| if_cuda_multi_devices | * | False |
| export_sources | * | ['PATH=/home/dongdong/gromacs-dp-rid/bin:$PATH'] |
