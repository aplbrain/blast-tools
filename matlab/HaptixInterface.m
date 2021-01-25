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

classdef HaptixInterface
    %HAPTIXINTERFACE Summary of this class goes here
    %   Detailed explanation goes here
    
    properties
        jointAngles % struct from mj_get_control
        sensors
        robotInfo
        robotPose % 3d position, 4d quat
        sensorTypes
    end
    
    methods
        function obj = HaptixInterface(startPose)
            % connect to this robot
            mj_connect();
            obj.robotInfo = mj_info();
            
            % handle current position
            currpos = mj_get_mocap();
            if nargin < 1
                startPose = 'default';
            end
            
            % accommodate some starting positions by name
            if ischar(startPose)
                switch startPose
                    case 'key'
                        obj.robotPose = [0,-0.23,0.18   0.018,0.7306,-0.1055,0.674];
                    otherwise
                        obj.robotPose = [currpos.pos, currpos.quat];
                end
                
            % otherwise allow a custom start position
            elseif length(startPose) == 7
                obj.robotPose = startPose;
            else
                warning('Invalid starting position - must be 7 elem vector or string, using default');
                obj.robotPose = [currpos.pos, currpos.quat];
            end
            
            % set the current position and send it
            currpos.pos = obj.robotPose(1:3);
            currpos.quat = obj.robotPose(4:7);
            mj_set_mocap(currpos);
            
            % add some info
            obj.populateSensorTypes();
        end
        
        function [] = close(obj)
            mj_close();
        end
        
        function obj = refreshJointAngles(obj)
            obj.jointAngles = mj_get_control();
        end
        
        % actuator indices
        % 1. wrist rotation          -  A_wrist_PRO
        % 2. wrist deviation         -  A_wrist_UDEV
        % 3. wrist flexion/extension -  A_wrist_PRO
        % 4. thumb ab/ad             -  A_thumb_ABD
        % 5. thumb MCP               -  A_thumb_MCP
        % 6. thumb PIP               -  A_thumb_PIP
        % 7. thumb DIP               -  A_thumb_DIP
        % 8. index AB/AD             -  A_index_ABD
        % 9. index MCP               -  A_index_MCP
        % 10. middle MCP             -  A_middle_MCP
        % 11. ring MCP               -  A_ring_ABD
        % 12. pinky ab/ad            -  A_pinky_ABD
        % 13. pinky MCP              -  A_pinky_MCP
        function [] = sendJointAngles(obj,jointAngles)
            obj.jointAngles.nu = 13;
            obj.jointAngles.ctrl = jointAngles;
            mj_set_control(obj.jointAngles);
        end
        
        % send the position (3D) and orientation (in radians,
        % roll-pitch-yaw order) to the hand
        function [] = sendWristPose(obj, pose6D)
            currpos.nmocap = 1;
            currpos.time = 0;
            currpos.pos = pose6D(1:3);
            % reorder the eulers to roll-pitch-yaw
            pose6D(4:6) = [-(pose6D(6)+pi), pose6D(4), pose6D(5)];
            currpos.quat = eul2quat(pose6D(4:6), 'ZYX'); % haven't checked ZYX for the hand
            mj_set_mocap(currpos);
        end
        
        % contact force indices
        % 1     palm_thumb
        % 2     palm_pinky
        % 3     palm_side
        % 4     palm_back
        % 5     thumb_proximal
        % 6     thumb_medial
        % 7     thumb_distal	
        % 8     index_proximal
        % 9     index_medial
        % 10	index_distal	
        % 11	middle_proximal
        % 12	middle_medial
        % 13	middle_distal	
        % 14	ring_proximal
        % 15	ring_medial	
        % 16	ring_distal
        % 17	pinky_proximal
        % 18	pinky_medial	
        % 19	pinky_distal
        
        function obj = getSensorData(obj)
            sensorData = mj_get_sensor();
            sensorData = sensorData.sensordata;
            obj.sensors = struct();
            obj.sensors.jointPos = sensorData(1:22);
            obj.sensors.jointVel = sensorData(23:44);
            obj.sensors.actuatorPos = sensorData(45:57);
            obj.sensors.actuatorVel = sensorData(58:70);
            obj.sensors.actuatorForce = sensorData(71:83);
            obj.sensors.accelerometer = reshape(sensorData(84:98), [3 5])';
            obj.sensors.gyro = reshape(sensorData(99:113), [3 5])';
            obj.sensors.contactForce = sensorData(114:132);
        end
        
        function obj = populateSensorTypes(obj)
            obj.sensorTypes = cell(30, 1);
            
            % only populating sensor types from this model
            % and these are off-by-one relative to the enum
            obj.sensorTypes{1} = 'touch';
            obj.sensorTypes{2} = 'accelerometer';
            obj.sensorTypes{4} = 'gyro';
            obj.sensorTypes{9} = 'joint_position';
            obj.sensorTypes{10} = 'joint_velocity';
            obj.sensorTypes{13} = 'actuator_position';
            obj.sensorTypes{14} = 'actuator_velocity';
            obj.sensorTypes{15} = 'actuator_force';
        end
        
    end
end

