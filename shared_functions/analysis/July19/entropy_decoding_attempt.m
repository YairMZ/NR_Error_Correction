%% transmitted data
clc
clear
A = load('/Users/yairmazal/Google_Drive/repositories/acoustic_tests/Transmitted_data/07_19/10_07_2019_12_20_44_stats.mat','transmitted_data');
transmitted_data = A.transmitted_data;
%discard first 7 transmissions, they occured prior to capture, last
%tranmission after capture end.

clear A

number_of_messages = length(transmitted_data.decoded_data);



[transmitted_structure.bits_idx,transmitted_structure.bits_val, transmitted_structure.entropy_est] ...
    = infer_structure(transmitted_data.binary_data',number_of_messages,10^-2);

%% received data
A = load('/Users/yairmazal/Google_Drive/repositories/acoustic_tests/Raw_captures/Eilat_July_19/10_07_2019/raw_capture_log_10_07_2019__12_21_36.mat','received_data');
received_data = A.received_data;
clear A

expected_structure = structure_init();

%% iteration
number_of_messages = length(received_data);


for msg_idx = 1:number_of_messages %iterate over messages
    
    [received_data(msg_idx).softStructureDecodeed, received_data(msg_idx).softStructureBinary, received_data(msg_idx).softStructureUint]...
        = soft_structure(received_data(msg_idx).whole_msg, received_data(msg_idx).entropy_est,...
        transmitted_structure.bits_idx, transmitted_structure.bits_val, expected_structure);
    if length(received_data(msg_idx).softStructureDecodeed) < expected_structure.num_of_msg && ...
            length(received_data(msg_idx).softStructureDecodeed) > 0
        [received_data(msg_idx).softStructureDecodeed, received_data(msg_idx).softStructureBinary, received_data(msg_idx).softStructureUint]...
            = fix_sequence(received_data(msg_idx).softStructureUint, expected_structure);
    end
end

%% gain

recovery_gain = [];
for trans = received_data
    recovery_gain = [recovery_gain; length(trans.softStructureDecodeed) - length(trans.standard_decode)];
end
sum(recovery_gain)