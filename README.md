# airfoil-generator

Airfoil-generator is a tool generating airfoil flow field data for deep learning research.

This project is inspired by [Deep-Flow-Prediction](http://arxiv.org/abs/1810.08217)([code](https://github.com/thunil/Deep-Flow-Prediction))

## Requirements

0. **Linux**, Ubuntu 18.04 is recommended.

1. **OpenFOAM-5.x** and **gmsh**, this project use gmsh to generate unstructed mesh and use OpenFOAM-5.x(other version is not supported) as simulator.
   **NOTE**: There is two ways to install OpenFOAM, install from apt and build from source, install from apt in recommended.
   
   ```bash
    sudo sh -c "wget -O - https://dl.openfoam.org/gpg.key > /etc/apt/trusted.gpg.d/openfoam.asc"
    sudo add-apt-repository http://dl.openfoam.org/ubuntu
    sudo apt update
    sudo apt install openfoam5 gmsh
    source /opt/openfoam5/etc/bashrc  # activate openfoam5
    simpleFoam # check if installed successfully
   ```

2. airfoil-generator
   
   ```bash
   cd
   git clone https://github.com/yao-weijie/airfoil-generator.git && cd airfoil-generator/
   python3 -m pip install -U pip
   python3 setup.py install
   airfoil_generator --help # check if installed successfully
   ```

## Usage

It's better to generate data in a directory seperate from this project.


```bash
cd
mkdir airfoil-workspace
cp -r airfoil-generator/airfoil_database* airfoil-generator/config.yml airfoil-generator/case* -d airfoil-workspace
```

Airfoil_generator is a command-line tool, and can pass parameters from cli and a config file, and
cli parameters have higher priority.

```bash
airfoil-generator --n-samples=3 --config=/path/to/config.yaml
```

An example of config yaml file:

```yaml
#seed: 123456
case-dir: "caseSteadyState" # case-dir
airfoil-database: "airfoil_database" # airfoil database directory
fixed-airfoil: True # True to use only one airfoil "airfoil-name", False to randomly sample from "airfoil-database"
airfoil-name: "falcon"

freestream-angle: # inlet freestream angle, uniform randomly sample
  - 0
  - 20
freestream-length: # inlet freestream velocity, uniform randomly sample
  - 0
  - 50

# fluid parameters
rho: 1 # fluid density kg/m^3
nu: 1e-5 # fluid viscosity

# parallel parameters
parallel-enable: True
subdomains: 7 # subdomains if use parallel computing

# post process
res: 128 # resolution of output image
output-raw-mesh: True
output-airfoil-boundary: True

# outputs
n-samples: 2
output-dir: "outputs"
output-prefix: "sample"
```