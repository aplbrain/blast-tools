# blast-tools
Repository for BLAST Simulation tools

This repository provides tools for simulating and processing tactile data. Tactile data can be loaded in from a physical robotic system or it can be simulated using the MuJoCo HAPTIX software (Kumar and Todorov, MuJoCo HAPTIX: A virtual reality system for hand manipulation, 2015, https://ieeexplore.ieee.org/document/7363441). 

The software in this repo leverages the TouchSim software (Saal et al, Simulating tactile signals from the whole hand with millisecond precision, 2017, https://www.pnas.org/content/114/28/E5693.short) to convert tactile signals into biologically relevant neural spikes by modelling mechanoreceptors in the skin.

The goal with these software tools is to easily convert analog sensor signals into spiking neuron responses and perform basic analysis, such as inter-spike interval distributions and KL divergence calculations.

There are two notebooks that give short demos of the tool functionality using some pre-processed spiking tactile data that was generated from the MuJoCo HAPTIX environment.

More detail is provided in the notebooks, but here is a brief summary of the functions within this repo:

mujoco_sense.py - controls the MATLAB engine API for Python
matlab/HaptixInterface.mat - Interface between MATLAB and MuJoCo HAPTIX
matlab/MuJoCoSense.mat - Sensing & data collection in MuJoCo HAPTIX env
matlab/MuJoCoToSpikes.mat - Converting HAPTIX data to neural response
matlab/MuJoCoToStruct.mat - Preprocessing for spike train analysis
TouchSimMat2Python_Loader.py - Loads preprocessed responses to Python data types
spiketrainanalysis.py - Toolkit for spike train analysis
trialstats.py - Wrapper for simplified spike train analysis

There are specific Spike Train Analysis Tools within trialstats.py that users might find useful:
compare_neuron()   # Compares 2 different neurons across trials 
compare_afferent() # Compares 2 different afferent types (sa, ra, pc) across trials  
compare_response() # Compares 2 different experimental responses (e.g. object 1 vs object 2)  
compare_trial()    # Compares 2 different trials of the same experiement (e.g. trial 2 vs trial 4)  
compare_noise()    # Compares 2 different noise profiles of the same condition (e.g. 0 dB noise vs 9 dB noise) 
compare_location() # Compares 2 different stimulus points based on x-y coordinates


This repo was developed by Christophe J. Brown at the Johns Hopkins University Applied Physics Laboratory
 
