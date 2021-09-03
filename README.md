# NR Error Correction
Natural redundancy based error correction

My algorithms for error correction based / aided by natural redundancy in data.
The package considers natural redundancy which exists in sensor data such as telemetry data.
The protocol used to transmit the data also gives rise to additional redundancy.
The code currently considers only the MAVLink protocol, commonly used for UAV's.

To run tests simply clone, cd into the cloned repo, and run:

```
python -m unittest discover -v -s tests
```
