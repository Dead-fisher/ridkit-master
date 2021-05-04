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
