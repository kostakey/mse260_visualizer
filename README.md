# Atom Visualizer w/ LAMMPS for MSE260

## First Time Install

For ssh:

```git clone git@github.com:kostakey/mse260_visualizer.git```

For http:

```git clone https://github.com/kostakey/mse260_visualizer.git```

Once cloned, now change your directory:

```cd mse260_visualizer```

```cd src```

Run setup.sh:

```./setup.sh```

This will take some time because it is mirroring the LAMMPS physics library

This installs and builds all the project prerequisites in a Python virtual environment

You should only need to do this once per fresh install, so proceed to the next steps!

~~If things are failing, particularly with LAMMPS, run:~~

~~```rm -rf src/external/lammps```~~

~~Then:~~

~~```git submodule update --init --recursive --progress```~~

## Running Python Environment

Activate the Python virtual environment in the src/ folder:

```source .venv/bin/activate```

Then run the program!

```python3 main.py```

## Ending Python Environment

```deactivate```
