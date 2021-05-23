clear
clc
close all

%% Load transmitted data

myDir = uigetdir(pwd, 'Transmitted data directory'); %gets directory
if myDir == 0
    return
end

transmitted_data_files = dir(fullfile(myDir, '*_stats.mat'));

transmitted_data = {};

for file_idx = 1:length(transmitted_data_files)
    A = load(fullfile(transmitted_data_files(file_idx).folder, transmitted_data_files(file_idx).name),'acoustic_data');
    if not(isempty(fieldnames(A))) && size(A.acoustic_data.encoded_data,2) >= 10
        transmitted_data{end+1} = A.acoustic_data;
    end
end

%% Load received data

myDir = uigetdir(pwd, 'Received data directory'); %gets directory
if myDir == 0
    return
end

received_data_files = dir(fullfile(myDir, '*raw_capture_log*.mat'));

received_data = {};

for file_idx = 1:length(received_data_files)
    A = load(fullfile(received_data_files(file_idx).folder, received_data_files(file_idx).name),'msg');
    if not(isempty(fieldnames(A)))
        received_data{end+1} = A.msg;
    end
end
