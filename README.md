# DAVIS Data Capture System

[![DOI](https://zenodo.org/badge/741917894.svg)](https://zenodo.org/doi/10.5281/zenodo.10569637)

Event-based data are a lightweight data format for conveying visual information and well-suited for real-time analysis of human motion.  
However, reliable and easy to use methods for creating event-based datasets are not readily available.

This repository features custom-built Python code to aid researchers in capturing DAVIS240C samples for an event-based dataset.

The code was used to record and process the DAVIS Dataset of Manufacturing Assembly Tasks, which is available <a href="https://zenodo.org/records/10562563">here</a>

The repository requires the use <a href="http://jaerproject.org">jAER</a> open-source software, designed to display and record event data. The Python code interfaces with the jAER software by sending it commands through a UDP connection to start and stop logging data. It also makes use of an Arduino connected through a serial connection to trigger these commands to start and end the recordings.

All data are captured in raw form (.aedat) and can processed into numpy arrays for ease of use (.npy). 

## Cite our paper:
If you've found this work useful for your research, please cite our paper as follows:

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

## Quick Guide:

https://github.com/Robotics-and-AI/DAVIS-data-capture-system/assets/51830421/bc4b0a39-a13c-43cc-83f2-29406e9562aa




