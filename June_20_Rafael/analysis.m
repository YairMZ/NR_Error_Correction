clear
clc
load('rafael_data.mat'); %load data

%% find seperate missions
[~, ~, tx_file_idx]  = unique({HC_to_Ship.tx_file_name});
num_of_missions = tx_file_idx(end);
for ii = 1:length(HC_to_Ship)
    HC_to_Ship(ii).tx_file_idx = tx_file_idx(ii);
end

[num_of_tx_per_mission, mision_idx] = groupcounts(tx_file_idx);

disp('missions with more the 20 transmissions:')
disp(mision_idx(num_of_tx_per_mission>20))

clear ii tx_file_idx

%% possible msg lengths
lengths = num2cell(unique([HC_to_Ship.tx_length]));

%% basic stats
LPI_messages = find([HC_to_Ship.rx_length]==10);
short_messages = find([HC_to_Ship.rx_length]==182);
medium_messages = find([HC_to_Ship.rx_length]==2023);
long_messages = find([HC_to_Ship.rx_length]==4048);

%no failed LPI messages
failed_short =  short_messages(find([HC_to_Ship(short_messages).rx_success]==0));
failed_medium =  medium_messages(find([HC_to_Ship(medium_messages).rx_success]==0));
failed_long =  long_messages(find([HC_to_Ship(long_messages).rx_success]==0));

LPI_lost = LPI_messages([HC_to_Ship(LPI_messages).rx_length]<10);
short_lost = short_messages([HC_to_Ship(short_messages).rx_length]<10);
medium_lost = medium_messages([HC_to_Ship(medium_messages).rx_length]<10);
long_lost =  long_messages([HC_to_Ship(long_messages).rx_length]<10);
%no failed LPI messages
failed_short =  short_messages(find([HC_to_Ship(short_messages).rx_success]==0));
failed_medium =  medium_messages(find([HC_to_Ship(medium_messages).rx_success]==0));
failed_long =  long_messages(find([HC_to_Ship(long_messages).rx_success]==0));

success_short =  short_messages(find([HC_to_Ship(short_messages).rx_success]==0));
success_medium =  medium_messages(find([HC_to_Ship(medium_messages).rx_success]==0));
success_long =  long_messages(find([HC_to_Ship(long_messages).rx_success]==0));


%% 
HC_to_Ship(133).bit_errors = 80;
HC_to_Ship(139).bit_errors = 1456;
%% iterate over every tx. try reovery based on overall tx, and per mission recovery
mission_idx = 1;
xml_path = fullfile(pwd, 'dialect.xml');
mav_parse = MAVLINK_parser(xml_path);
expected_structure = containers.Map(lengths,{structure_init(10, 'NumMsg', 0, 'HdrIdx', [1], 'MsgLen', [19], 'MsgId', [212]),  %only a partial MavLink msg squeezes in 10B tx
                                              structure_init(117),
                                              structure_init(182),
                                              structure_init(2023),
                                              structure_init(4048)
                                             });

accumulated_binary  = containers.Map({10, 182, 2023, 4048},{[],[],[],[]});
accumulated_bytes  = containers.Map({10, 182, 2023, 4048},{[],[],[],[]});
window_length = 20;
[possible_probabilities,possible_entropies] = binary_entropy_function(1/window_length);
min_entropy = possible_entropies(2);
for tx_idx = 1:length(HC_to_Ship)
    
    if isKey(expected_structure, length(HC_to_Ship(tx_idx).encoded_rx)) % does the received stream of reasonable length
        
        if HC_to_Ship(tx_idx).rx_success == 1
            accumulated_binary(length(HC_to_Ship(tx_idx).encoded_rx)) = [accumulated_binary(length(HC_to_Ship(tx_idx).encoded_rx)), HC_to_Ship(tx_idx).binary_rx];
            accumulated_bytes(length(HC_to_Ship(tx_idx).encoded_rx)) = [accumulated_bytes(length(HC_to_Ship(tx_idx).encoded_rx)), HC_to_Ship(tx_idx).encoded_rx.'];
            HC_to_Ship(tx_idx).errors_after_correction = 0;
            
        end
        
        [HC_to_Ship(tx_idx).structure_bits_idx, HC_to_Ship(tx_idx).structure_bits_val, ...
            HC_to_Ship(tx_idx).entropy_est] ...
            = infer_structure(accumulated_binary(length(HC_to_Ship(tx_idx).encoded_rx)).',window_length);
        
        [HC_to_Ship(tx_idx).structure_bytes_idx, HC_to_Ship(tx_idx).structure_bytes_val, ...
            HC_to_Ship(tx_idx).byte_entropy_est] ...
            = infer_structure(accumulated_bytes(length(HC_to_Ship(tx_idx).encoded_rx)).',window_length);
        
        if min(HC_to_Ship(tx_idx).entropy_est(HC_to_Ship(tx_idx).entropy_est>0))+ eps < min_entropy
            disp(min(HC_to_Ship(tx_idx).entropy_est(HC_to_Ship(tx_idx).entropy_est>0)))
        end
            
        if HC_to_Ship(tx_idx).bit_errors > 0  % Are there any bad bits?
            %forcing
            [HC_to_Ship(tx_idx).forced_no_CRC, HC_to_Ship(tx_idx).forced_with_CRC,...
                HC_to_Ship(tx_idx).forcing_degree, HC_to_Ship(tx_idx).fixed_bytes, HC_to_Ship(tx_idx).forced_binary] = ...
                forced_structure_decode(uint8(HC_to_Ship(tx_idx).encoded_rx), expected_structure(length(HC_to_Ship(tx_idx).encoded_rx)), mav_parse, xml_path);
            HC_to_Ship(tx_idx).forcing_gain = length(HC_to_Ship(tx_idx).forced_with_CRC) - max(0,HC_to_Ship(tx_idx).num_of_MAV_msgs_rx);
            
            
            %soft
            [HC_to_Ship(tx_idx).entropy_decoded, HC_to_Ship(tx_idx).corrected_binary, HC_to_Ship(tx_idx).softStructureUint]...
                = soft_structure(uint8(HC_to_Ship(tx_idx).encoded_rx), HC_to_Ship(tx_idx).entropy_est, HC_to_Ship(tx_idx).structure_bits_idx,...
                HC_to_Ship(tx_idx).structure_bits_val, expected_structure(length(HC_to_Ship(tx_idx).encoded_rx)), xml_path);
            
            HC_to_Ship(tx_idx).soft_gain = length(HC_to_Ship(tx_idx).entropy_decoded) - max(0,HC_to_Ship(tx_idx).num_of_MAV_msgs_rx);
            
            if length(HC_to_Ship(tx_idx).binary_tx) == length(HC_to_Ship(tx_idx).binary_rx)
                HC_to_Ship(tx_idx).errors_after_correction = sum(HC_to_Ship(tx_idx).binary_tx ~= HC_to_Ship(tx_idx).corrected_binary);
            elseif HC_to_Ship(tx_idx).tx_length == 117 &&  HC_to_Ship(tx_idx).rx_length == 182
                HC_to_Ship(tx_idx).errors_after_correction = sum(HC_to_Ship(tx_idx).binary_tx ~= HC_to_Ship(tx_idx).corrected_binary(1:117*8));
            else
                HC_to_Ship(tx_idx).errors_after_correction = 0;%length(HC_to_Ship(tx_idx).binary_tx);
                HC_to_Ship(tx_idx).bit_errors = 0;%length(HC_to_Ship(tx_idx).binary_tx);
            end
        else
            HC_to_Ship(tx_idx).corrected_binary = HC_to_Ship(tx_idx).binary_rx;
        end
    else
        HC_to_Ship(tx_idx).errors_after_correction = 0;%length(HC_to_Ship(tx_idx).binary_tx);
        HC_to_Ship(tx_idx).bit_errors = 0;%length(HC_to_Ship(tx_idx).binary_tx);        
    end
    
end

%% Performance analysis
overall_tx.original_BER = 0;
overall_tx.rx_bits = 0;
overall_tx.corrected_BER = 0;

LPI.original_BER = 0;
LPI.rx_bits = 0;
LPI.corrected_BER = 0;

short_tx.original_BER = 0;
short_tx.rx_bits = 0;
short_tx.corrected_BER = 0;

medium_tx.original_BER = 0;
medium_tx.rx_bits = 0;
medium_tx.corrected_BER = 0;

long_tx.original_BER = 0;
long_tx.rx_bits = 0;
long_tx.corrected_BER = 0;

for tx_idx = 1:length(HC_to_Ship)
    if isKey(expected_structure, length(HC_to_Ship(tx_idx).encoded_rx))  % does the received stream of reasonable length
        if length(HC_to_Ship(tx_idx).binary_tx) == length(HC_to_Ship(tx_idx).binary_rx) && length(HC_to_Ship(tx_idx).binary_rx) > 80
            overall_tx.rx_bits =  overall_tx.rx_bits + 117*8;
            overall_tx.corrected_BER = overall_tx.corrected_BER + sum(HC_to_Ship(tx_idx).binary_tx(1:117*8) ~= HC_to_Ship(tx_idx).corrected_binary(1:117*8));
            overall_tx.original_BER = overall_tx.original_BER + sum(HC_to_Ship(tx_idx).binary_tx(1:117*8) ~= HC_to_Ship(tx_idx).binary_rx(1:117*8));
        elseif HC_to_Ship(tx_idx).tx_length == 117 &&  HC_to_Ship(tx_idx).rx_length == 182
            overall_tx.rx_bits = overall_tx.rx_bits + 117*8;
            overall_tx.corrected_BER = overall_tx.corrected_BER + sum(HC_to_Ship(tx_idx).binary_tx(1:117*8) ~= HC_to_Ship(tx_idx).corrected_binary(1:117*8));
            overall_tx.original_BER = overall_tx.original_BER + sum(HC_to_Ship(tx_idx).binary_tx(1:117*8) ~= HC_to_Ship(tx_idx).binary_rx(1:117*8));
        end
    end
%     overall_tx.rx_bits = overall_tx.rx_bits + length(HC_to_Ship(tx_idx).binary_rx);
%     overall_tx.original_BER = overall_tx.original_BER + HC_to_Ship(tx_idx).bit_errors;
%     overall_tx.corrected_BER = overall_tx.corrected_BER + HC_to_Ship(tx_idx).errors_after_correction;
    switch HC_to_Ship(tx_idx).rx_length
        case 10
            LPI.rx_bits = LPI.rx_bits + length(HC_to_Ship(tx_idx).binary_rx);
            LPI.original_BER = LPI.original_BER + HC_to_Ship(tx_idx).bit_errors;
            LPI.corrected_BER = LPI.corrected_BER + HC_to_Ship(tx_idx).errors_after_correction;
        case 182
            short_tx.rx_bits = short_tx.rx_bits + 117*8;%length(HC_to_Ship(tx_idx).binary_rx);
            short_tx.original_BER = short_tx.original_BER + HC_to_Ship(tx_idx).bit_errors;
            short_tx.corrected_BER = short_tx.corrected_BER + HC_to_Ship(tx_idx).errors_after_correction;
        case 2023
            medium_tx.rx_bits = medium_tx.rx_bits + length(HC_to_Ship(tx_idx).binary_rx);
            medium_tx.original_BER = medium_tx.original_BER + HC_to_Ship(tx_idx).bit_errors;
            medium_tx.corrected_BER = medium_tx.corrected_BER + HC_to_Ship(tx_idx).errors_after_correction;
        case 4048
            long_tx.rx_bits = long_tx.rx_bits + length(HC_to_Ship(tx_idx).binary_rx);
            long_tx.original_BER = long_tx.original_BER + HC_to_Ship(tx_idx).bit_errors;
            long_tx.corrected_BER = long_tx.corrected_BER + HC_to_Ship(tx_idx).errors_after_correction;
    end 
end

LPI.original_BER = LPI.original_BER / LPI.rx_bits;
LPI.corrected_BER = LPI.corrected_BER / LPI.rx_bits;

short_tx.original_BER = short_tx.original_BER / short_tx.rx_bits;
short_tx.corrected_BER = short_tx.corrected_BER / short_tx.rx_bits;

medium_tx.original_BER = medium_tx.original_BER / medium_tx.rx_bits;
medium_tx.corrected_BER = medium_tx.corrected_BER / medium_tx.rx_bits;

long_tx.original_BER = long_tx.original_BER / long_tx.rx_bits;
long_tx.corrected_BER = long_tx.corrected_BER / long_tx.rx_bits;


overall_tx.original_BER = overall_tx.original_BER / overall_tx.rx_bits;
overall_tx.corrected_BER = overall_tx.corrected_BER / overall_tx.rx_bits;

%% histogram
%tx 242 is last 182B tx

set(0,'defaulttextinterpreter','latex')
error_idx = [];
corrected_error_idx = [];
for tx_idx = 1:length(HC_to_Ship)
     if length(HC_to_Ship(tx_idx).encoded_rx) == 182  % does the received stream of reasonable length
         error_idx = [error_idx; find(HC_to_Ship(tx_idx).binary_tx(1:117*8) ~= HC_to_Ship(tx_idx).binary_rx(1:117*8))];
         corrected_error_idx = [corrected_error_idx; find(HC_to_Ship(tx_idx).binary_tx(1:117*8) ~= HC_to_Ship(tx_idx).corrected_binary(1:117*8))];
     end
      
end

ent_per_byte = mean(reshape(HC_to_Ship(242).entropy_est(1:936),[8,117]));

% figure(1)
% histogram((error_idx/8),0:117)
% xticks(0.5:1:117);
% xticklabels(1:117);
% xtickangle(90);
% xlim([-3 120])
% 
% 
% figure(2)
% histogram((corrected_error_idx/8),0:117)
% xticks(0.5:1:117);
% xticklabels(1:117);
% xtickangle(90);
% xlim([-3 120])

fig = figure(1);
histogram((error_idx/8),1:117)
xlim([-3 120])
grid on
%legend('original','Interpreter','latex','Location', 'southoutside' )
format_figure(fig, 'XLabel', 'Byte \#', 'YLabel', 'Errors Count')
saveas(fig,'errors_per_byte_original.svg','svg')

fig = figure(2)
histogram((corrected_error_idx/8),0:117)
% xticks(0.5:1:117);
% xticklabels(1:117);
% xtickangle(90);
xlim([-3 120])
colororder('k')
yyaxis right
plot(0.5:117,ent_per_byte,'b*')
ylabel('Average Entropy [bits]')
ylim([-0.05, 1.05])
grid on
hold off;
yyaxis left
%legend('corrected', '$H$','Interpreter','latex','Location', 'southoutside' )
format_figure(fig, 'XLabel', 'Byte \#', 'YLabel', 'Errors Count')
saveas(fig,'errors_per_byte_corrected.svg','svg')

%[B,BG] = groupcounts(error_idx);
%[C,CG] = groupcounts(corrected_error_idx);
%test = find(B(CG)<C);
%% byte entropy
fig = figure(3);
plot(HC_to_Ship(255).byte_entropy_est,'*')
title('entropy per byte 10B messages')
format_figure(fig)

fig = figure(3);
plot(HC_to_Ship(242).byte_entropy_est,'*')
title('entropy per byte 182B messages')
xlim([0 117])
format_figure(fig)

%%
bit_matrix = [];
byte_matrix = [];
for tx_idx = 1:length(HC_to_Ship)
    if length(HC_to_Ship(tx_idx).encoded_rx) == 182 && HC_to_Ship(tx_idx).rx_success ==1 && tx_idx >=148 && tx_idx <=185 % does the received stream of reasonable length
        byte_matrix = [byte_matrix; HC_to_Ship(tx_idx).encoded_rx(1:117)];
        bit_matrix = [bit_matrix; HC_to_Ship(tx_idx).binary_rx(1:117*8).'];
    end
end

fourier_byte = fft(double(byte_matrix));
fourier_bit = fft(double(bit_matrix));
%%
fig1 = figure(1);
stem(abs(fourier_byte(:,56)));
figure(3);
plot(byte_matrix(:,56:59),'*');
figure(4);
histogram(byte_matrix(:,56), 100)
figure(5);
histogram(byte_matrix(:,57), 100)
figure(6);
histogram(byte_matrix(:,58), 100)
figure(7);
histogram(byte_matrix(:,59), 100)
lat = zeros(1,8);
for ii = 1: 8
    lat(ii) =  typecast( uint8(byte_matrix(ii,56:59)) , 'single');
end
figure(8)
plot(lat,'*')
%fig1 =  figure(2);
%stem(abs(fourier_bit(:,17:24)));
%% entropy of byte 66
% ent_57 = [];
% selected_byte = 74;
% original_errors = [];
% post_errors = [];
% for tx_idx = 1:length(HC_to_Ship)
%     if length(HC_to_Ship(tx_idx).encoded_rx) == 182  % does the received stream of reasonable length
%         if HC_to_Ship(tx_idx).bit_errors < HC_to_Ship(tx_idx).errors_after_correction
%             disp(tx_idx)
%         end
%         if length(HC_to_Ship(tx_idx).encoded_rx) == 182  % does the received stream of reasonable length
%             original_errors = [original_errors; sum(HC_to_Ship(tx_idx).binary_tx(selected_byte*8:(selected_byte+1)*8-1) ~= HC_to_Ship(tx_idx).binary_rx(selected_byte*8:(selected_byte+1)*8-1))];
%             post_errors = [post_errors; sum(HC_to_Ship(tx_idx).binary_tx(selected_byte*8:(selected_byte+1)*8-1) ~= HC_to_Ship(tx_idx).corrected_binary(selected_byte*8:(selected_byte+1)*8-1))];
%         end
%         if length(HC_to_Ship(tx_idx).entropy_est) > 0
%             ent_57 = [ent_57, HC_to_Ship(tx_idx).entropy_est(selected_byte*8:(selected_byte+1)*8-1)];
%         end
%     end
% end

% for ii=1:8
%     figure(ii+1)
%     plot(ent_57(ii,:),'*')
% end


