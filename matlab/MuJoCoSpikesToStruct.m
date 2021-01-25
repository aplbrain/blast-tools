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

function MuJoCoSpikesToStruct(data_dir,new_dir)
old=cd(data_dir);
contents=ls;

for i=1:size(contents,1)
    filename=contents(i,:);
    if contains(filename,'.mat')
        load(contents(i,:));
        
        % start new instance of data as struct, losing methods associated
        % with object but converting custom obj to standard matlab obj
        r_strs={};

        r_strs{1}=struct(r_sensor);

        for k=1:length(r_strs)
            r_str=r_strs{k};
            % first level
            r_str.affpop=struct(r_str.affpop);
            responses=r_str.responses;
            r_str.responses={};
            for j=1:length(responses)
                responses_struct=struct(responses(j));
                responses_struct.afferent=struct(responses_struct.afferent);
                r_str.responses{j}=responses_struct;
            end
            r_str.stimulus=struct(r_str.stimulus);

            % second level
            affpop_afferents=r_str.affpop.afferents;
            r_str.affpop.afferents={};
            for j=1:length(affpop_afferents)
                afferent_struct=struct(affpop_afferents(j));
                r_str.affpop.afferents{j}=afferent_struct;
            end
            r_strs{k}=r_str;
        end
        newfilename=fullfile(new_dir,filename);
        save(newfilename,'r_strs')
    end
end
cd(old)