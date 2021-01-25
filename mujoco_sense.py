"""
Christophe J. Brown
August 2020

Copyright 2020 The Johns Hopkins University Applied Physics Laboratory

Licensed under the MIT License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

https://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import errno
import matlab.engine

class MujoCoSense:

    def __init__(self, showpaths=False, showroot=False):
        print('MATLAB engine starting.')
        self.eng = matlab.engine.start_matlab()
        print('Engine started.')
        print('Importing paths. This may take a few minutes.')

        matlabroot = self.eng.matlabroot()
        matlabpath = self.eng.matlabpath().split(';')

        if showroot:
            print(f'MATLAB root: {matlabroot}')

        for path in matlabpath:
            if showpaths:
                print(f'Adding path: {path}')
            self.eng.addpath(path)

        print('Calling setup_path.')
        self.eng.setup_path(nargout=0)
        print('All paths imported.')

    def haptix_sense(self, spikes_save_path, target_sampling_frequency=1e3, step_count=1e3, trial_count=10):
        """

        Parameters
        ----------
        spikes_save_path - save location for sensor data. Columns: | Force (N) | Depth (mm) | Time deltas (sec)
        target_sampling_frequency - desired sampling frequency. Actual will vary depending on cpu speeds. use <= 1e3
        step_count - how many steps (wrist movement increments) to complete the trial in
        trial_count - how many trials (i.e. files) to generate

        Returns None
        -------

        """
        if not os.path.exists(spikes_save_path):
            os.makedirs(spikes_save_path)
        print(f'Calling MuJoCoSense for haptic sensing. Performing {trial_count} trial(s).')
        self.eng.MuJoCoSense(spikes_save_path, target_sampling_frequency, step_count, trial_count, nargout=0)
        print('Finished haptic sensing.')
        print(f'Saved to {spikes_save_path}')

    def MuJoCoToSpikes(self, data_path, save_path):
        """

        Parameters
        ----------
        data_path - directory to load data from
        save_path - directory to save data to for neural spike train analysis

        Returns None
        -------

        """
        if not os.path.exists(data_path):
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), data_path)
        mat_files = os.listdir(data_path)

        # Checking if the list is empty or not
        if len(mat_files) == 0:
            print(f"Directory is empty: {data_path}.")
            return

        if not os.path.exists(save_path):
            os.makedirs(save_path)

        print('Converting indentation depths to neural spikes.')
        self.eng.MuJoCoToSpikes(data_path, save_path, nargout=0)
        print('Finished converting forces.')
        print(f'Saved to {save_path}')

    def MuJoCoSpikesToStruct(self, data_dir, processed_dir):
        """

        Parameters
        ----------
        data_dir - directory to load data from
        processed_dir - directory to save preprocessed data for Python analysis

        Returns
        -------

        """
        if not os.path.exists(data_dir):
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), data_dir)
        mat_files = os.listdir(data_dir)

        # Checking if the list is empty or not
        if len(mat_files) == 0:
            print(f"Directory is empty: {data_dir}.")
            return

        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir)

        print('Beginning pre-processing for spike train analysis.')
        self.eng.MuJoCoSpikesToStruct(data_dir, processed_dir, nargout=0)
        print('Finished pre-processing.')
        print(f'Saved to {processed_dir}')



# TODO: Document somewhere that one must install the matlab API for python
# https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html

# Links that were helpful
# https://www.mathworks.com/matlabcentral/answers/166188-can-i-call-my-own-custom-matlab-functions-from-python-r2014b
# https://www.mathworks.com/matlabcentral/answers/202901-problem-of-call-user-script-from-python
# https://www.mathworks.com/matlabcentral/answers/93627-why-do-i-receive-license-manager-error-16






