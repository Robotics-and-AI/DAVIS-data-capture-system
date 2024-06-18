# DAVIS Data Capture System

[![DOI](https://zenodo.org/badge/741917894.svg)](https://zenodo.org/doi/10.5281/zenodo.10569637)
[![Paper](https://img.shields.io/badge/Paper-10.1016/j.dib.2024.110340-blue)](https://doi.org/10.1016/j.dib.2024.110340)

## Introduction

Event-based sensors encode visual information asynchronously with low latency and high temporal resolution.  
Event-based datasets are scarce, so user-friendly methods for creating said datasets are required.

This repository contributes with code to record a dataset with a DAVIS240C event camera.  
The code was used to record and process the <a href="https://zenodo.org/records/10562563">Event-based Dataset of Assembly Tasks (EDAT24)</a>.

All data are captured in raw form (.aedat) and can be processed into numpy arrays (.npy) for ease of use.

## Requirements

- A <a href="https://docs.inivation.com/_static/hardware_guides/davis240.pdf">DAVIS240C event camera</a> - to obtain the data
- The <a href="http://jaerproject.org">jAER open-source software</a> - to display and record the data
- An <a href="https://www.arduino.cc">Arduino board</a> - to trigger the commands to start and end the recordings

A detailed explanation on how to utilize the code is provided below

https://github.com/Robotics-and-AI/DAVIS-data-capture-system/assets/51830421/bc4b0a39-a13c-43cc-83f2-29406e9562aa

## Cite our paper
If you've found this work useful for your research, please cite our paper as follows

```
@article{Duarte2024,
         title = {Event-based dataset for the detection and classification of manufacturing assembly tasks},
         author = {Laura Duarte and Pedro Neto},
         journal = {Data in Brief},
         volume = {54},
         year = {2024},
         doi = {https://doi.org/10.1016/j.dib.2024.110340}
}
```




