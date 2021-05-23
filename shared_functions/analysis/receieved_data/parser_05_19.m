clear

myDir = uigetdir; %gets directory 
acoustic_channel_log_files = dir(fullfile(myDir, '/acoustic_channel_log*.txt'));
acoustic_log_files = dir(fullfile(myDir, '/acoustic_log*.txt'));

for k = 1:length(acoustic_channel_log_files)
    tmp_date = acoustic_channel_log_files(k).date(1:end-8);
    
    f = fopen(fullfile(acoustic_channel_log_files(k).folder, acoustic_channel_log_files(k).name));
    tmp1 = textscan(f, '%s %s %s %s %s %s %s %s %s %s %s %s %s');
    fclose(f);
    
    f = fopen(fullfile(acoustic_log_files(k).folder, acoustic_log_files(k).name));
    tmp2 = fread(f);
    fclose(f);
    
    msg_start_byte = strfind(tmp2','DATA');
    msg_end_byte = strfind(tmp2','<EOP>') + 4;
    clear msg;
    for l = 1:size(tmp1{1},1) %iterate over messages
        %{
            create a struct with follwing fields:
            - Aquisition_time - datetime
            - mpd - multipath delay in ms - double
            - psnr - multipath delay in ms - double - for details on psnr:
             https://dsp.stackexchange.com/questions/11326/difference-between-snr-and-psnr
            - AGC - Automatic gain control
            - rel_spd - ﻿relative speed in knots between the local and
            remote modems, where a negative number indicates the modems are
            moving farther apart - knots
            - ccerr - ﻿Corrected Channel Error—Metric 0–14
            - raw_modem_output- Whole modem outpput via serail port
            - msg_len as infered by modem it self (including whole (MAVLink
            headers and all)
            - whole_msg - message rreated by moedm as payload (including whole (MAVLink
            headers and all)
            -
        %}
        tmp_time = tmp1{1,3}(l);
        msg(l).Aquisition_time = datetime(strcat(tmp_date, {' '}, tmp_time));
        msg(l).mpd = str2double(tmp1{1,5}(l));
        msg(l).psnr = str2double(tmp1{1,7}(l));
        msg(l).agc = str2double(tmp1{1,9}(l));
        msg(l).rel_spd = str2double(tmp1{1,11}(l));
        msg(l).ccerr = str2double(tmp1{1,13}(l));
        raw_modem_output = tmp2(msg_start_byte(l):msg_end_byte(l))';
        msg_len = str2double(char(raw_modem_output(6:9)));     %indices 6:9 four digits of message length
        
        stats = raw_modem_output(14+msg_len:end);
        cursor = strfind(char(stats),'CRC') + 4;
        if isequal(stats(cursor:cursor+3) , 'Fail')
            msg(l).CRC = [0,0];
        else %CRC passed
            msg(l).CRC = [1,0];
        end
        parentheses_idx = strfind(char(stats),'{')+1;
        if not(isempty(parentheses_idx))
            msg(l).CRC(2) = str2double(char(stats(parentheses_idx:parentheses_idx+3)));
        end
        
        msg(l).raw_modem_output = raw_modem_output;
        msg(l).msg_len = msg_len;
        msg(l).whole_msg = msg(l).raw_modem_output(12:12+msg(l).msg_len-1);       %index 12 beginging of payload after ':'
        msg(l).decoded_msg = decode_msg(msg(l).whole_msg);
        
    end
    
    tmp = fullfile(acoustic_log_files(k).folder, acoustic_log_files(k).name);
    save([tmp(1:end-3) 'mat'],'msg');
    
end




