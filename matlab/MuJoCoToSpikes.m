% Christophe J. Brown
% August 2020
% 
% Copyright 2020 The Johns Hopkins University Applied Physics Laboratory
% 
% Licensed under the MIT License (the "License");
% you may not use this file except in compliance with the License.
% You may obtain a copy of the License at
% 
% https://opensource.org/licenses/MIT
% 
% Unless required by applicable law or agreed to in writing, software
% distributed under the License is distributed on an "AS IS" BASIS,
% WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
% See the License for the specific language governing permissions and
% limitations under the License.

function MuJoCoToSpikes(data_path, save_path)
fingers = {'D2d'}; % Tip of index finger

%set up the stimulus location properties 
pin_rad = 5.64;      % pin with 5.64 mm radius gives contact area ~100 mm^2)

%Note: within TouchSim, the segment ID for the distal finger pads are Thumb (1),
%Index (3), Middle (14), Ring (18), and Little (21)
stim_location = [65 -60; 
                  0 0;
                  -4 53;
                  20 85;
                  63 105]; % pin coordinate (D1; D2; D3; D4; D5 distal finger pads)

stim_location = stim_location(2,:); %downselect to only the fingers we want to analyze

%generate afferent population 
fprintf('Generating afferent population...\r\n');
for i = 1:length(fingers)
    a(i) = affpop_hand(fingers{i});    
end
fprintf('Done\r\n');

%find the data files
data_path = data_path
files = rdir(strcat(data_path,'\*.mat'));
fprintf('Found %d data files\r\n',length(files));

%location for saving the results
% save_path = strcat(data_path,'_spikes');
save_path = save_path;
save_flag = true;

%load in each data file and convert to neural activity 
for i = 1:length(files)
           
    load(files(i).name);
    fprintf('Converting file %d of %d to spikes\r\n',i,length(files));
    
    %grab the depths
    sensor_trace = depths(:,2); % This is the sensor data from mujoco (in mm)
    
    %calculate average sampling frequency
    average_sample_time = mean(depths(:,3)); %Indexing the times
    
    %generate stimulus signal
    sampling_freq = round(1 / average_sample_time) 
    sensor_stim = Stimulus(sensor_trace,stim_location,sampling_freq,pin_rad);   
    
    %generate afferent behavior based on the stimulus signal
%     tic
    clear r_sensor_tmp
    for j = 1:length(fingers)             
        s = sensor_stim;            
        r_sensor_tmp(j) = a(j).response(s);
    end
    
    r_sensor = r_sensor_tmp;
%     toc
    
    %save out variable for each trial
    if save_flag
        [~, save_name, ~] = fileparts(files(i).name); 
        save_filename = strcat(save_path,'\spikes_ftsn_',save_name,'.mat')
        save_filename
        save(save_filename,'r_sensor');
    end
    
end

% data_dir = 'C:\Users\browncj1\Box\personal_BLAST\mujoco\MuJoCo_spikes\'
% new_dir = 'C:\Users\browncj1\Box\personal_BLAST\mujoco\MuJoCo_spikes - touchsim2struct\'
% 
% MuJoCoSpikesToStruct(data_dir, new_dir)


end