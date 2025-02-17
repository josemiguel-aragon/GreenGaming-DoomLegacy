# Green Gaming: Automated Energy Consumption Reduction for the Doom Engine

This repository contains the source code and data required to reproduce the research presented in the paper **"Green Gaming: Automated Energy Consumption Reduction for the Doom Engine."** using the Green Synchronous Software Energy consumption meter (GREESSE).

## Repository Structure

Inside the repository, there are two main directories:

- **`results`**:  
  This directory contains the experimental results presented in the paper, along with various Python 3 scripts for generating graphs and visualizations.

- **`DoomLegacy_EC_GA`**:  
  This directory includes the necessary scripts to reproduce the experiments.

## Experiment Reproduction

Within the **`DoomLegacy_EC_GA`** directory, there are two subdirectories:

- **`scriptsMediPi`**:  
  This should be placed on the energy measurement Raspberry Pi, the controller device in **GREESSE**.

- **`scriptsExperiPi`**:  
  This should be placed on the Raspberry Pi 4B device that is being measured.

### Running the Experiment

To execute the experiment:

1. **Set up the GREESSE energy measurement system** by ensuring the necessary scripts are placed in the correct Raspberry Pi devices.
2. **Run the optimization algorithm** by executing the script:  

   ```bash
   python3 main_llvm_intengerV3.py

