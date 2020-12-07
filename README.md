# blast-tools
Repository for BLAST Simulation tools

This repository provides tools for simulating and processing tactile data. Tactile data can be loaded in from a physical robotic system or it can be simulated using the MuJoCo HAPTIX software (Kumar and Todorov, MuJoCo HAPTIX: A virtual reality system for hand manipulation, 2015, https://ieeexplore.ieee.org/document/7363441). 

The software in this repo leverages the TouchSim software (Saal et al, Simulating tactile signals from the whole hand with millisecond precision, 2017, https://www.pnas.org/content/114/28/E5693.short) to convert tactile signals into biologically relevant neural spikes by modelling mechanoreceptors in the skin.

The goal with these software tools is to easily convert analog sensor signals into spiking neuron responses and perform basic analysis, such as inter-spike interval distributions and KL divergence calculations.

There are two notebooks that give short demos of the tool functionality using some pre-processed spiking tactile data that was generated from the MuJoCo HAPTIX environment.

## Getting Started

This repo has dependencies for those leveraging this pipeline in a borad scope (i.e. performing data generation, preprocessing, and analysis).

### Software Dependencies:
* MATLAB installed - used for controlling MuJoCo HAPTIX and TouchSim computations.
    * Also install the MATLAB engine API for Python. This allows user to `import matlab.engine()` for scripting MATLAB instructions from Python
    * https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html
* MuJoCo HAPTIX - used for generating data points (IMPORTANT NOTE: At this time (Dec. 2020) MuJoCo HAPTIX is designed to ONLY run in Windows operating system)
    * MuJoCo HAPTIX Installation: https://www.roboti.us/index.html
    * MuJoCo HAPTIX Documentaiton (if needed): http://www.mujoco.org/book/haptix.html
    * For running the demo notebooks
          * Must be installed and running `MPL_key.xml` when the `haptix_sense()` function is called
          * Run MuJoCo HAPTIX from `mjhaptix150\mjhaptix150\program\mjhaptix.exe`
          * Open `MPL_key.xml` in HAPTIX from  `mjhaptix150\mjhaptix150\model\MPL\MPL_Key.xml`
* Python Libraries - for analysis and visualization
    * `pip install numpy`
    * `pip install scipy`
    * `pip install matplotlib`
    * The demos run in Jupyter Notebooks, requiring [anaconda](https://docs.anaconda.com/anaconda/install/). The code itself may run independently.
          
### Software Setup

To clone this repo and access its files: `git clone https://github.com/aplbrain/blast-tools.git`

it is recommended to resolve any dependencies you might have beforehand. To run the demo notebook, navigate to the `notebooks` directory in a terminal environment and open `mujoco_haptix_spike_train_analysis.ipynb` and follow the instructions contained within. The notebook preview should also be available for viewing on Github. MATLAB does NOT need to be running for the MMATLAB engine API to work in Python, but MuJoCo HAPTIX must be running for haptic sensing to take place. Please see the full video of the notebook for visual instructions. [VIDEO LINK NEEDED]

For analysis and visualization of data that is already preprocessed (i.e. probability of spikings or KL divergence comparison of trials), view the notebook `spike_train_tools_demo.ipynb` to view the avaialble analyses.

Please see notebooks, but here is a brief summary of the functions within this repo:

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
 
