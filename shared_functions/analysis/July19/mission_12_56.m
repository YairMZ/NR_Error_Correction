%% constants
clc
clear

MESSAGES_PER_TRANSMISSION = 4;

%% 12:56 - basic reception stats
% number of recpetions and acquisition failures for the 12:56 mission on
% July 10th.
disp('Mission from July 10, 2019, 12:56')

f = fopen('/Users/yairmazal/Google_Drive/repositories/acoustic_tests/Raw_captures/Eilat_July_19/10_07_2019/raw_capture_log_10_07_2019__12_56_54.txt');
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

clear f tmp ii receptions_idx

%% received data
A = load('/Users/yairmazal/Google_Drive/repositories/acoustic_tests/Raw_captures/Eilat_July_19/10_07_2019/raw_capture_log_10_07_2019__12_56_54.mat','received_data');
received_data = A.received_data;
clear A 


%% transmitted_data
A = load('/Users/yairmazal/Google_Drive/repositories/acoustic_tests/Transmitted_data/07_19/10_07_2019_13_01_13_stats.mat','transmitted_data');
transmitted_data = A.transmitted_data;

clear A

%% match transmissions and receptions
%first good match is the 6-th reception which is matched to the 21st
%transmission, verified by timestamp and sequence ID. match prevoius ones:
binary_reception = [];
for ii = 1:5
    binary_reception = [binary_reception received_data(ii).binary_data];
end
[~, transmission_idx] = match_tranmissions_2_receptions(binary_reception, transmitted_data.binary_data(:,1:20));

%trasnmissions 21-24 are attributed to receptions 6-9

%match  last three receptions:
binary_reception = [];
for ii = 10:12
    binary_reception = [binary_reception received_data(ii).binary_data];
end
[~, transmission_idx_last] = match_tranmissions_2_receptions(binary_reception, transmitted_data.binary_data(:,25:end));
transmission_idx_last = transmission_idx_last + 25 - 1;

mask = [transmission_idx, 21:24, transmission_idx_last];

% binary_reception = [];
% for ii = 1:12
%     binary_reception = [binary_reception received_data(ii).binary_data];
% end
% [~, transmission_idx_all] = match_tranmissions_2_receptions(binary_reception, transmitted_data.binary_data);

transmitted_data.binary_data = transmitted_data.binary_data(:,mask);
transmitted_data.decoded_data = transmitted_data.decoded_data(mask);
transmitted_data.encoded_data = transmitted_data.encoded_data(:,mask);

number_of_transmissions = mask(end) - mask(1) + 1;

clear binary_reception ii transmission_idx transmission_idx_last



%% BER
errors = [];
num_of_bits = [];
for trans_idx= 1:12
    num_of_bits = [num_of_bits; length(transmitted_data.binary_data(:,trans_idx))];
    errors = [errors; sum(abs(double(transmitted_data.binary_data(:,trans_idx))-double(received_data(trans_idx).binary_data)))];
end
% errors
% errors/num_of_bits

disp(['bit errors: ' num2str(sum(errors))]);
BER = 100*errors./num_of_bits;
disp(['BER: ' num2str(mean(BER)), '%'])


%% recovered MAVLink messages - Standard decode
successfully_recovered_msg = [];
for msg = received_data
    successfully_recovered_msg = [successfully_recovered_msg;  length(msg.standard_decode)];
end

clear msg

faulty_recovery_msg = length(received_data) * MESSAGES_PER_TRANSMISSION - sum(successfully_recovered_msg);
%Since unclear if matching is correct, I assume (not realistic) that all lost transmissions are aquisition failures,
%i.e. no messages went without nitice by the modem.  
completely_lost_msg = Acquisition_failures * MESSAGES_PER_TRANSMISSION;
%completely_lost_msg = ( number_of_transmissions - num_of_receptions ) * MESSAGES_PER_TRANSMISSION;

recovery_success_rate = sum(successfully_recovered_msg)/((num_of_receptions + Acquisition_failures) * MESSAGES_PER_TRANSMISSION);

disp(['standard decode MAVLink message success rate: ' num2str(recovery_success_rate)]);

%% recovered MAVLink messages - no force no CRC
drop_CRC_gain = [];

for trans = received_data
    standard_decode = length(trans.standard_decode);
    no_CRC_decode = 0;
    for msg = trans.no_force_no_CRC
        if isstruct(msg.Payload)
            no_CRC_decode = no_CRC_decode +1;
        end
    end
    drop_CRC_gain = [drop_CRC_gain; no_CRC_decode - standard_decode];    
end

disp(['drop CRC gain: ' num2str(sum(drop_CRC_gain))])
clear trans standard_decode no_CRC_decode msg

%% recovered MAVLink messages - Forcing force with CRC
force_with_CRC_gain = [];

for trans = received_data
    force_with_CRC_gain = [force_with_CRC_gain; length(trans.forced_with_CRC) - length(trans.standard_decode)];    
end

clear trans
disp([ 'Force structure maintain CRC gain: ' num2str(sum(force_with_CRC_gain))])

%% Forcing Degree

structure_BER = [];
for trans = received_data
    structure_BER = [structure_BER; (1-trans.forcing_degree.good_bit_ratio)*100];    
end

clear trans
disp([ 'Structure bits BER: ' num2str(mean(structure_BER)) '%'])
