[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Build Status - GitHub](https://github.com/YairMZ/NR_Error_Correction/actions/workflows/python-app.yml/badge.svg)](https://github.com/YairMZ/NR_Error_Correction/actions/workflows/python-app.yml/badge.svg)
[![codecov](https://codecov.io/gh/YairMZ/NR_Error_Correction/branch/main/graph/badge.svg?token=EBIWO80ERF)](https://codecov.io/gh/YairMZ/NR_Error_Correction)
[![Sourcery](https://img.shields.io/badge/Sourcery-enabled-brightgreen)](https://sourcery.ai)


# NR Error Correction
Natural redundancy based error correction

My algorithms for error correction based / aided by natural redundancy in data.
The package considers natural redundancy which exists in sensor data such as telemetry data.
The protocol used to transmit the data also gives rise to additional redundancy.
The code currently considers only the MAVLink protocol, commonly used for UAV's.

To run tests simply clone, cd into the cloned repo, and run:
```
python -m pytest
```
or
```
python -m pytest --cov-report=html
```
to run also coverage tests.