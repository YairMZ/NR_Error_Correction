clear
clc
close all

myDir = uigetdir; %gets directory
if myDir == 0
    return
end

basic_log_files = dir(fullfile(myDir, '*.mat'));


dialect = mav_dialect();

start_byte = 1; %used to disregard first 27 bytes as they hold mostly empty SVS data

%% parse data
transmitted_data.time_boot_ms = [];
transmitted_data.file_name = {};
transmitted_data.binary_data = [];
transmitted_data.encoded_data = [];
transmitted_data.decoded_data = {};

for file_idx = 1:length(basic_log_files)
    A = load(fullfile(basic_log_files(file_idx).folder, basic_log_files(file_idx).name),'acoustic_transmission_log');
    
    if not(isempty(fieldnames(A)))
        count = A.acoustic_transmission_log{1,1}.count(1);
        
        %for my parser
        %acoustic_data.file_name{end+1} = fullfile(basic_log_files(file_idx).folder, basic_log_files(file_idx).name);
        transmitted_data.time_boot_ms = [ transmitted_data.time_boot_ms  A.acoustic_transmission_log{1,1}.time_boot_ms];
        transmitted_data.encoded_data = [transmitted_data.encoded_data A.acoustic_transmission_log{1,1}.data(start_byte:count,:)];
        
        %number of transmissions per file
        transmitted_data.transmissions_per_file(file_idx) = struct('filename', fullfile(basic_log_files(file_idx).folder, basic_log_files(file_idx).name),...
            'num_of_transmissions', size(A.acoustic_transmission_log{1,1}.data,2));
        
        %for alon's parser
        %     for msg_idx=1:length(A.acoustic_transmission_log{1,1}.data)
        %        data = [data; A.acoustic_transmission_log{1,1}.data{1,msg_idx}(1:count)];
        %     end
        %     data = data';
        
        %decode each msg
        for msg_idx = 1:size(A.acoustic_transmission_log{1,1}.data,2)
            tmp=de2bi(A.acoustic_transmission_log{1,1}.data(start_byte:count,msg_idx),8,'right-msb')';
            transmitted_data.binary_data = [transmitted_data.binary_data tmp(:)]; 
            transmitted_data.decoded_data{end+1} = deserializemsg(dialect,A.acoustic_transmission_log{1,1}.data(start_byte:count,msg_idx));
            transmitted_data.file_name{end+1} = fullfile(basic_log_files(file_idx).folder, basic_log_files(file_idx).name);
        end
        
        
    end
    
end

%decode each column
% for msg_idx = 1:size(acoustic_data.binary_data,2)
%     acoustic_data.decoded_data{msg_idx} = deserializemsg(dialect,acoustic_data.binary_data(:,msg_idx));
% end
transmitted_data.decoded_data = transmitted_data.decoded_data';
output = fullfile(basic_log_files(file_idx).folder, 'transmitted_data.mat');
save(output,'transmitted_data');


%% stats per file



for file_idx = 1:length(basic_log_files)
    A = load(fullfile(basic_log_files(file_idx).folder, basic_log_files(file_idx).name),'acoustic_transmission_log');
    if not(isempty(fieldnames(A))) && size(A.acoustic_transmission_log{1,1}.data,2) >= 10 % if less than 10 messages don't do statistics
        clear transmitted_data;
        transmitted_data.binary_data = [];
        transmitted_data.decoded_data = {};
        transmitted_data.encoded_data = A.acoustic_transmission_log{1,1}.data(start_byte:count,:);
        count = A.acoustic_transmission_log{1,1}.count(1);
        
        for msg_idx = 1:size(A.acoustic_transmission_log{1,1}.data,2)
            tmp=de2bi(A.acoustic_transmission_log{1,1}.data(start_byte:count,msg_idx),8,'right-msb')';
            transmitted_data.binary_data = [transmitted_data.binary_data tmp(:)];
            transmitted_data.decoded_data{end+1} = deserializemsg(dialect,A.acoustic_transmission_log{1,1}.data(start_byte:count,msg_idx));
        end
        
        transmitted_data.std_per_bit = std(double(transmitted_data.binary_data),0,2);
        transmitted_data.entropy_per_bit = Entropy(transmitted_data.binary_data')';
        transmitted_data.decoded_data = transmitted_data.decoded_data';
        
        output = fullfile(basic_log_files(file_idx).folder, [basic_log_files(file_idx).name(1:end-4), '_stats.mat']);
        save(output,'transmitted_data');
        figure(file_idx);
        plot(transmitted_data.entropy_per_bit,'*');
    end
end
