%% constants
clc
clear

MESSAGES_PER_TRANSMISSION = 4;

%% 12:20 - basic reception stats
% number of recpetions and acquisition failures for the 12:20 mission on
% July 10th.
disp('Mission from July 10, 2019, 12:20')

f = fopen('../../Raw_captures/Eilat_July_19/10_07_2019/raw_capture_log_10_07_2019__12_21_36.txt');
tmp = uint8(fread(f));
fclose(f);
receptions_idx = strfind(tmp','DATA');
num_of_receptions = length(receptions_idx);
Acquisition_failures_idx = strfind(tmp','Acquisition stats');
Acquisition_failures = length(Acquisition_failures_idx);
disp(['number of acquisition failures: ' num2str(Acquisition_failures)]);

for ii=1:length(Acquisition_failures_idx)
    Acquisition_failures_idx(ii) = sum(Acquisition_failures_idx(ii)>receptions_idx) +1;
end

clear f tmp ii

%% transmitted_data
A = load('../../Transmitted_data/07_19/10_07_2019_12_20_44_stats.mat','transmitted_data');
transmitted_data = A.transmitted_data;
%discard first 7 transmissions, they occured prior to capture, last
%tranmission after capture end.
first_capture = 8;
last_capture = 44;
transmitted_data.binary_data = transmitted_data.binary_data(:,first_capture:last_capture);
transmitted_data.decoded_data = transmitted_data.decoded_data(first_capture:last_capture);
transmitted_data.encoded_data = transmitted_data.encoded_data(:,first_capture:last_capture);

clear A first_capture last_capture

%% received data
A = load('../../Raw_captures/Eilat_July_19/10_07_2019/raw_capture_log_10_07_2019__12_21_36.mat','received_data');
received_data = A.received_data;
clear A 

%% BER
standard_errors = [];
forced_errors = [];
inferred_decode_errors = [];
transmission_based_decode_errors = [];
num_of_bits = [];
for trans_idx= 1:6
    num_of_bits = [num_of_bits; length(transmitted_data.binary_data(:,trans_idx))];
    standard_errors = [standard_errors; sum(abs(double(transmitted_data.binary_data(:,trans_idx))-double(received_data(trans_idx).binary_data)))];
    forced_errors = [forced_errors; sum(abs(double(transmitted_data.binary_data(:,trans_idx))-double(received_data(trans_idx).forced_binary)))];
    inferred_decode_errors = [inferred_decode_errors; sum(abs(double(transmitted_data.binary_data(:,trans_idx))-double(received_data(trans_idx).corrected_binary)))];
    transmission_based_decode_errors = [transmission_based_decode_errors; sum(abs(double(transmitted_data.binary_data(:,trans_idx))-double(received_data(trans_idx).softStructureBinary)))];
end
% errors
% errors/num_of_bits

for trans_idx= 9:36
    num_of_bits = [num_of_bits; length(transmitted_data.binary_data(:,trans_idx))];
    standard_errors = [standard_errors; sum(abs(double(transmitted_data.binary_data(:,trans_idx))-double(received_data(trans_idx-2).binary_data)))];
    forced_errors = [forced_errors; sum(abs(double(transmitted_data.binary_data(:,trans_idx))-double(received_data(trans_idx-2).forced_binary)))];
    inferred_decode_errors = [inferred_decode_errors; sum(abs(double(transmitted_data.binary_data(:,trans_idx))-double(received_data(trans_idx-2).corrected_binary)))];
    transmission_based_decode_errors = [transmission_based_decode_errors; sum(abs(double(transmitted_data.binary_data(:,trans_idx))-double(received_data(trans_idx-2).softStructureBinary)))];
end

disp(' ')
disp(['bit errors: ' num2str(sum(standard_errors))]);
BER = 100*standard_errors./num_of_bits;
disp(['BER: ' num2str(mean(BER)), '%'])

disp(['forced binary bit errors: ' num2str(sum(forced_errors))]);
forced_BER = 100*forced_errors./num_of_bits;
disp(['BER: ' num2str(mean(forced_BER)), '%'])

disp(['soft binary bit errors: ' num2str(sum(inferred_decode_errors))]);
soft_BER = 100*inferred_decode_errors./num_of_bits;
disp(['BER: ' num2str(mean(soft_BER)), '%'])

disp(['transmission based binary bit errors: ' num2str(sum(transmission_based_decode_errors))]);
trans_BER = 100*transmission_based_decode_errors./num_of_bits;
disp(['BER: ' num2str(mean(trans_BER)), '%'])
disp(' ')


%% recovered MAVLink messages - Standard decode
successfully_recovered_msg = [];
for msg = received_data
    successfully_recovered_msg = [successfully_recovered_msg;  length(msg.standard_decode)];
end

clear msg

faulty_recovery_msg = length(received_data) * MESSAGES_PER_TRANSMISSION - sum(successfully_recovered_msg);

completely_lost_msg = ( length(transmitted_data.decoded_data) - length(received_data) ) * MESSAGES_PER_TRANSMISSION;
disp(['completely_lost_msg: ' num2str(completely_lost_msg)]);

recovery_success_rate = sum(successfully_recovered_msg)/(length(transmitted_data.decoded_data) * MESSAGES_PER_TRANSMISSION);


disp(['standard decode MAVLink message success rate: ' num2str(recovery_success_rate)]);

disp(['packet loss: ' num2str(1-recovery_success_rate) ] );

disp(['number of lost packets: ' num2str(length(transmitted_data.decoded_data) * MESSAGES_PER_TRANSMISSION - sum(successfully_recovered_msg)) ] );

%% recovered MAVLink messages - no force no CRC
% drop_CRC_gain = [];
% 
% for trans = received_data
%     standard_decode = length(trans.standard_decode);
%     no_CRC_decode = 0;
%     for msg = trans.no_force_no_CRC
%         if isstruct(msg.Payload)
%             no_CRC_decode = no_CRC_decode +1;
%         end
%     end
%     drop_CRC_gain = [drop_CRC_gain; no_CRC_decode - standard_decode];    
% end
% 
% disp(['drop CRC gain: ' num2str(sum(drop_CRC_gain))])
% clear trans standard_decode no_CRC_decode msg

%% recovered MAVLink messages - Forcing with CRC
force_with_CRC_gain = [];

for trans = received_data
    force_with_CRC_gain = [force_with_CRC_gain; length(trans.forced_with_CRC) - length(trans.standard_decode)];    
end

clear trans
disp([ 'Force structure maintain CRC gain: ' num2str(sum(force_with_CRC_gain))])

%% recovered MAVLink messages - soft structure
soft_structure_gain = [];

for trans = received_data(10:end)
    soft_structure_gain = [soft_structure_gain; length(trans.entropy_decoded) - length(trans.standard_decode)];    
end

clear trans
disp([ 'Soft structure maintain CRC gain: ' num2str(sum(soft_structure_gain))])

%% recovered MAVLink messages - soft structure based on transmission
transmission_based_gain = [];

for trans = received_data
    transmission_based_gain = [transmission_based_gain; length(trans.softStructureDecodeed) - length(trans.standard_decode)];    
end

clear trans
disp([ 'transmission_based gain: ' num2str(sum(transmission_based_gain))])

%% Forcing Degree

structure_BER = [];
for trans = received_data
    structure_BER = [structure_BER; (1-trans.forcing_degree.good_bit_ratio)*100];    
end

clear trans
disp([ 'Structure bits BER: ' num2str(mean(structure_BER)) '%'])
