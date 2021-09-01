# NR Error Correction
Natural redundancy based error correction

My algorithms for error correction based / aided by natural reduandancy in data.
The package considers natrual redundancy which exists in sensor data such as telemetry data.
The protocol used to trasmit the data also gives rise to additional reduandancy.
The code currently consideres only the MAVLink protocol, commonly used for UAV's.

To run tests simply clone, cd into the the cloned repo, and run:

```
python -m unittest discover -v -s tests
```
