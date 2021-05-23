clear
clc

myDir = uigetdir; %gets directory 
if myDir == 0
    return
end
acoustic_channel_log_files = dir(fullfile(myDir, '/acoustic_channel_log*.txt'));
acoustic_raw_capture_files = dir(fullfile(myDir, '/raw_capture*.txt'));

mav_parse = MAVLINK_parser();
expected_structure = structure_init();
concat_struct = [];

for file_idx = 1:length(acoustic_raw_capture_files)
    %tmp_date = acoustic_raw_capture_files(file_idx).date(1:end-8);
    
    %parse raw capture - get data
    f = fopen(fullfile(acoustic_raw_capture_files(file_idx).folder, acoustic_raw_capture_files(file_idx).name));
    tmp = uint8(fread(f));
    fclose(f);
    disp(acoustic_raw_capture_files(file_idx).name);
    msg_start_byte = strfind(tmp','DATA');
    msg_end_byte = strfind(tmp','<EOP>') + 4;
    number_of_messages = length(msg_start_byte);
    clear received_data;
    received_data(number_of_messages) = struct(); 
    for msg_idx = 1:number_of_messages %iterate over messages
        %{
            create a struct with follwing fields:
            - mpd - multipath delay in ms - double
            - psnr - double - for details on psnr:
             https://dsp.stackexchange.com/questions/11326/difference-between-snr-and-psnr
            - AGC - Automatic gain control
            - rel_spd - ﻿relative speed in knots between the local and
            remote modems, where a negative number indicates the modems are
            moving farther apart - knots
            - ccerr - ﻿Corrected Channel Error—Metric 0–14
            - raw_modem_output- Whole modem outpput via serial port
            - msg_len as infered by modem it self (including whole (MAVLink
            headers and all)
            - whole_msg - message rreated by moedm as payload (including whole (MAVLink
            headers and all)
            - Source
            - Destination
        %}
        
        received_data(msg_idx).raw_modem_output = tmp(msg_start_byte(msg_idx):msg_end_byte(msg_idx))';
        received_data(msg_idx).msg_len = str2double(char(received_data(msg_idx).raw_modem_output(6:9)));     %indices 6:9 four digits of message length
        received_data(msg_idx).whole_msg = received_data(msg_idx).raw_modem_output(12:12+received_data(msg_idx).msg_len-1);       %index 12 beginging of payload after ':'
        
        stats = received_data(msg_idx).raw_modem_output(14+received_data(msg_idx).msg_len:end);
        %source
        cursor = 1 + length('Source:');
        received_data(msg_idx).source = str2double(char(stats(cursor: cursor + 3)));
        %dest
        cursor = cursor + length('xxx  Destination:');
        received_data(msg_idx).destination = str2double(char(stats(cursor: cursor + 3)));
        %CRC
        cursor = strfind(char(stats),'CRC') + 4;
        if isequal(stats(cursor:cursor+3) , 'Fail')
            received_data(msg_idx).Modem_CRC = 0;
            %received_data(msg_idx).Modem_CRC = [0,0];
        else %CRC passed
            %received_data(msg_idx).Modem_CRC = [1,0];
            received_data(msg_idx).Modem_CRC = 1;
        end
%         tmp2 = strfind(char(stats),'{')+1;
%         if not(isempty(tmp2))
%             received_data(msg_idx).Modem_CRC(2) = str2double(char(stats(tmp2:tmp2+3)));
%         end
        %MPD
        cursor = strfind(char(stats),'MPD') + 4;
        received_data(msg_idx).mpd = str2double(char(stats(cursor:cursor+3)));
        %pSNR
        cursor = strfind(char(stats),'PSNR') + 5;
        received_data(msg_idx).psnr = str2double(char(stats(cursor:cursor+3)));
        %AGC
        cursor = strfind(char(stats),'AGC') + 4;
        received_data(msg_idx).agc = str2double(char(stats(cursor:cursor+1)));
        %rel_spd
        cursor = strfind(char(stats),'SPD') + 4;
        received_data(msg_idx).rel_spd = str2double(char(stats(cursor:cursor+4)));
        %ccerr
        cursor = strfind(char(stats),'CCERR') + 6;
        received_data(msg_idx).ccerr = str2double(char(stats(cursor:cursor+2)));
        %standard_decode
        received_data(msg_idx).standard_decode = deserializemsg(mav_dialect(),received_data(msg_idx).whole_msg);
        %no_force_no_CRC
        received_data(msg_idx).no_force_no_CRC = decode_msg(received_data(msg_idx).whole_msg,mav_parse);
        %force structure
        [received_data(msg_idx).forced_no_CRC, received_data(msg_idx).forced_with_CRC,...
            received_data(msg_idx).forcing_degree, received_data(msg_idx).fixed_bytes, received_data(msg_idx).forced_binary] = ...
            forced_structure_decode(received_data(msg_idx).whole_msg, expected_structure, mav_parse);
        
%          tmp2 = de2bi(received_data(msg_idx).whole_msg,8,'right-msb')';
%          received_data(msg_idx).binary_data = tmp2(:);
        received_data(msg_idx).binary_data = reshape( de2bi(received_data(msg_idx).whole_msg,8,'right-msb')',1,[])';
        
        if msg_idx >= 10
            [received_data(msg_idx).structure_bits_idx, received_data(msg_idx).structure_bits_val, ...
                received_data(msg_idx).entropy_est] ...
                = infer_structure([received_data.corrected_binary received_data(msg_idx).binary_data]');
            
            [received_data(msg_idx).entropy_decoded, received_data(msg_idx).corrected_binary, received_data(msg_idx).softStructureUint]...
                = soft_structure(received_data(msg_idx).whole_msg, received_data(msg_idx).entropy_est,...
                received_data(msg_idx-1).structure_bits_idx, received_data(msg_idx-1).structure_bits_val, expected_structure);
        else
            received_data(msg_idx).corrected_binary = received_data(msg_idx).binary_data;
            
        end
    end
    
    output = fullfile(acoustic_raw_capture_files(file_idx).folder, [acoustic_raw_capture_files(file_idx).name(1:end-3), 'mat']);
    save(output,'received_data');
    concat_struct = [concat_struct, received_data];
    
%     f = fopen(fullfile(acoustic_channel_log_files(file_idx).folder, acoustic_channel_log_files(file_idx).name));
%     tmp1 = textscan(f, '%s %s %s %s %s %s %s %s %s %s %s %s %s');
%     fclose(f);
%     
    %tmp_time = tmp1{1,3}(msg_idx);
     %   msg(msg_idx).Aquisition_time = datetime(strcat(tmp_date, {' '}, tmp_time));
end

output = fullfile(acoustic_raw_capture_files(file_idx).folder, 'concat_struct.mat');
save(output,'concat_struct');

clear cursor dialect f file_idx msg_end_byte msg_start_byte myDir number_of_messages stats tmp tmp2 tmp_date msg_idx ans expected_structure

%% entropy decoding using transmitted structure
entropy_decoding_attempt;
save('/Users/yairmazal/Google_Drive/repositories/acoustic_tests/Raw_captures/Eilat_July_19/10_07_2019/raw_capture_log_10_07_2019__12_21_36.mat','received_data');