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

function MuJoCoSense(spikes_save_path, target_sampling_frequency, step_count, trial_count)

%     mj_close() % if "Already connected" error is being thrown.
    mj = HaptixInterface('key');

    wrist_angle_start = 0;
    wrist_angle_end = 0.47;

    sampling_frequency = double(step_count); % Hz
    time_step = wrist_angle_end / sampling_frequency;

    % Initialize an array to record sensor values and timestamps
    depths = zeros(sampling_frequency,2);
    depths_idx = 1;
    % INITIALIZE THE HAND MODEL ---------------------------------------------

    A_wrist_UDEV_init = 0.1425;

    A_wrist_PRO = 0;
    A_wrist_UDEV = A_wrist_UDEV_init; % Corresponds to initial contact with the key
    % A_wrist_PRO = 0; % Duplicate attribute (see HaptixInterface.m)
    A_thumb_ABD = 0;
    A_thumb_MCP = 0;
    A_thumb_PIP = 0;
    A_thumb_DIP = 0;
    A_index_ABD = .5;
    A_index_MCP = .25;
    A_middle_MCP = 0;
    A_ring_ABD = 0;
    A_pinky_ABD = 0;
    A_pinky_MCP = 0;

    jointAngles = [A_wrist_PRO A_wrist_UDEV A_wrist_PRO A_thumb_ABD... 
                   A_thumb_MCP A_thumb_PIP A_thumb_DIP A_index_ABD... 
                   A_index_MCP A_middle_MCP A_ring_ABD...
                   A_pinky_ABD A_pinky_MCP];

    mj.sendJointAngles(jointAngles);

    % END OF INITIALIZATION -------------------------------------------------

    % MAIN LOOP - This happens for each desired trial
    for trial = 1:trial_count
        A_wrist_UDEV = A_wrist_UDEV_init;
        
        jointAngles = [A_wrist_PRO A_wrist_UDEV A_wrist_PRO A_thumb_ABD... 
                   A_thumb_MCP A_thumb_PIP A_thumb_DIP A_index_ABD... 
                   A_index_MCP A_middle_MCP A_ring_ABD...
                   A_pinky_ABD A_pinky_MCP];

        mj.sendJointAngles(jointAngles);
        
        depths_idx = 1;
        angle=0;
        pause(1);%%%%%%%%%%%%%%%%%%%%%%%%%
        tic;
        
        
        
        
        
        % TIMER OBJECT - Controls the sensing of data on an interval
        t = timer;
        period = 1/target_sampling_frequency  
%         period = 1/1000 
        set(t, 'Period', period);
        set(t, 'ExecutionMode', 'fixedRate');
        set(t, 'TasksToExecute', step_count);
        set(t, 'TimerFcn',{@sense});
        set(t, 'UserData', {depths_idx, depths, mj});
        start(t)   
        
        
        % CONTROL LOOP - This controls the wrist movement
        for angle = wrist_angle_start:time_step:wrist_angle_end % This controls the MuJoCo wrist's full swipe motion
            A_wrist_UDEV = A_wrist_UDEV + time_step;

            jointAngles = [A_wrist_PRO A_wrist_UDEV A_wrist_PRO A_thumb_ABD... 
                       A_thumb_MCP A_thumb_PIP A_thumb_DIP A_index_ABD... 
                       A_index_MCP A_middle_MCP A_ring_ABD...
                       A_pinky_ABD A_pinky_MCP];

            mj.sendJointAngles(jointAngles);

            % This updates the recorded sensor values.
            vars = get(t, 'UserData');
            depths_idx = vars(1,1);
            depths_idx = depths_idx{1};
            depths = vars(1,2);
            depths = depths{1};
        end
        
        % Finish timer and prepare for next trial
        stop(t) 
        delete(t)

        % Get sampling frequency
        average_sample_time = mean(depths(:,3));
        sampling_freq = round(1 / average_sample_time)
        % Record indentation depth into array for saving

        save(strcat(spikes_save_path,'\object_key_sf_',num2str(sampling_freq), '_trial_',num2str(trial),'.mat'), 'depths')
    end


mj.close();

end

% SENSING FUNCTION - This performs data collection every
% [target_sampling_frequency] seconds
function sense(obj, ~)
    % Vars hols the object that the timer interacts with
    % Retreive them first to get their most up-to-date values
    vars = get(obj, 'UserData');
    depths_idx = vars{1,1};
    depths = vars{1,2};
    mj = vars{1,3};
    
    % Check if a texture has been sensed
    mj_sensor1 = mj.getSensorData();
    force = mj_sensor1.sensors.contactForce(10);

    % Convert force value from Newtons to millimeter indenation
    indentation_depth = 0.308 * (force / (0.02 * force + 0.027))^(2/3);

    % Write depth to array value
    depths(depths_idx,1) = force; % Force in Newetons
    depths(depths_idx,2) = indentation_depth; % Depth in mm
    depths(depths_idx,3) = toc; % Time since last data recording
    tic;
    depths(depths_idx,:);
    
    % Store the now-updated values so they are accessible by the all
    % functions
    depths_idx = depths_idx + 1; % Increment the index for the next sense()
    set(obj,'UserData',{depths_idx, depths, mj});
end

% end

