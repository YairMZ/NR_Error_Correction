function decoded_msg = MAVLink_decode(data,mavlink_parser)
%MAVLink decoding based on https://en.wikipedia.org/wiki/MAVLink

%% constants
MSG_HEADER_BYTE = 254;
MSG_LENGTH_SHIFT = 1;
SEQUENCE_SHIFT = 2;
SYSTEMID_SHIFT = 3;
COMPONENTID_SHIFT = 4;
MSGID_SHIFT = 5;
PAYLOAD_SHIFT = 6;

%% Find relevant headers - i.e. 0xFE
headers = find(data == MSG_HEADER_BYTE);
real_headers = zeros(size(headers));

if isempty(headers)
    headers = 1;
    real_headers = 1;
end

if headers(1) == 1 %First header must be first byte
    real_headers(1) = 1;
else % if first byte  isn't a header force it.
    headers = [1 headers];
    real_headers = [1 real_headers];
end


for k=1:length(headers)
    if real_headers(k) == 1
        tmp_length = data(headers(k)+ MSG_LENGTH_SHIFT);
        irrlevant_data = headers(k) + PAYLOAD_SHIFT + tmp_length +1; % all
        % msg_header_bytes with indices smaller than this aren't real headers.
        % They stem from payload data which accedentatlly has the byte.
        
        % find next legit start:
        % next index of legit start:
        if not(isempty(find(data(irrlevant_data +1:end) ==254, 1)))
            next_legit_idx = find(data(irrlevant_data +1:end) ==254, 1) + irrlevant_data;
            %set next legit index to real header
            real_headers(headers == next_legit_idx) = 1;
        end
    end
end

headers = headers(real_headers ==1);

%% decode each inferred message
decoded_msg = robotics.uav.internal.mavlink.Structures.createMsgExt(length(headers));

for k=1:length(headers)
    decoded_msg(k).HeaderIdx = headers(k);
    decoded_msg(k).MsgLen = data(headers(k)+ MSG_LENGTH_SHIFT);
    decoded_msg(k).Seq = data(headers(k) + SEQUENCE_SHIFT);
    decoded_msg(k).SystemID = data(headers(k) + SYSTEMID_SHIFT);
    decoded_msg(k).ComponentID = data(headers(k) + COMPONENTID_SHIFT);
    decoded_msg(k).MsgID = data(headers(k) + MSGID_SHIFT);
    %check length validity
    if length(data) >= headers(k)+decoded_msg(k).MsgLen + PAYLOAD_SHIFT &&...
            ~isempty(mavlink_parser.MessagePrototypes.find(decoded_msg(k).MsgID))
        try
            decoded_msg(k).Payload  = mavlink_parser.parse(decoded_msg(k).MsgID,...
                data(headers(k) + PAYLOAD_SHIFT:headers(k)+decoded_msg(k).MsgLen + PAYLOAD_SHIFT -1)); %first 6 byets are MAVLink overhead
        catch ME
            decoded_msg(k).Payload = "Parsing Exception";
        end
    else
        decoded_msg(k).Payload = "Incompatible Length";
    end
    %MAV.CRC{k} = data(headers(k) + PAYLOAD_SHIFT + MAV.msgs_length(k): headers(k) + PAYLOAD_SHIFT + MAV.msgs_length(k)+1); %two bytes of CRC
    
end

% for idx = 1:MESSAGES_PER_TRANSMISSION
%     decoded_transmission_no_CRC(idx).Seq = msg_buff(expected_structure.headers_idx(idx) + SEQUENCE_SHIFT);
%     decoded_transmission_no_CRC(idx).SystemID = msg_buff(expected_structure.headers_idx(idx) + SystemID_SHIFT);
%     decoded_transmission_no_CRC(idx).ComponentID = msg_buff(expected_structure.headers_idx(idx) + ComponentID_SHIFT);
%     decoded_transmission_no_CRC(idx).MsgID = msg_buff(expected_structure.headers_idx(idx) + MsgID_SHIFT);
%     decoded_transmission_no_CRC(idx).Payload = mavlink_parser.parse(decoded_transmission_no_CRC(idx).MsgID, ...
%         msg_buff(expected_structure.headers_idx(idx) + PAYLOAD_SHIFT: ...
%         expected_structure.headers_idx(idx) + PAYLOAD_SHIFT + expected_structure.msg_len(idx)-1)...
%         );
% end

% for k=1:length(headers)
%     msgs{k} = data(headers(k) + 6 :MAV.msgs_length(k) + headers(k) + 7 );
% end
% MAV.msgs = msgs;

end

