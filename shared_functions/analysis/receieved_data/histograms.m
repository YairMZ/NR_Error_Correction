close all
clear

while true
    myDir = uigetdir; %gets directory
    if myDir == 0
        break
    end
    tmp = dir(fullfile(myDir, '/raw_capture_log*.mat'));
    if not(isempty(tmp))
        if not(exist('acoustic_log_files'))
            acoustic_log_files = tmp;
        else
            acoustic_log_files = [acoustic_log_files; tmp];
        end
    end     
end


%histogram of time delay (in seconds) between successive acoustic transmission
h_all = histogram((diff(global_position_int{2}.time_boot_ms*1e-4)),100,'Normalization','probability');
% Create ylabel
ylabel({'occurance [%]'});
% Create xlabel
xlabel({'Time between received transmissions [s]'});
title('histogram of all messages');
