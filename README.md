# DigitalDriveShaft
[![Python package](https://github.com/Modular-Design/DigitalDriveShaft/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Modular-Design/DigitalDriveShaft/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/Modular-Design/DigitalDriveShaft/branch/main/graph/badge.svg?token=M2EM6L19BI)](https://codecov.io/gh/Modular-Design/DigitalDriveShaft)
[![supported Python version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
---
- Python Framework to evaluate, simulate and optimize composite reinforced driveshaft structures
- Python Version: 3.8 and newer

## Installation

0. setup venv `python -m venv .`
1. activate venv (Windows: `venv\Scripts\activate`, Linux)
2. install requrements with `pip install -e .`
3. starting ansys find more information here [here](https://mapdl.docs.pyansys.com/version/stable/getting_started/running_mapdl.html)

```
sudo /opt/ansys_inc/v222/ansys/bin/ansys222 -grpc
```


## Features
- Analytic Evaluation
  - [X] Strength
  - [X] Buckling
  - [X] Eigenfrequency
- Simulation Evaluation
  - [X] Strength
  - [ ] Buckling
  - [ ] Eigenfrequency
- Optimization
  - [X] Multi-goal optimization

## Testing

run `pytest` in venv
