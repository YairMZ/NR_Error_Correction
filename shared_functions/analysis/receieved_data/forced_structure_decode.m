function [decoded_transmission_no_CRC,decoded_transmission_with_CRC,forcing_degree, fixed_bytes, corrected_binary] = forced_structure_decode(msg_buff,expected_structure, mavlink_parser, xml_path)
% forced_structure_decode  decdodes a transmission and forces the expected structure.
%
%   [decoded_transmission,forcing_degree] = forced_structure_decode(msg_buff,expected_structure, mavlink_parser, xml_path)
%       decodes the data encoded in msg_buff, using the parser object
%       mavlink_parser, while forcing the structure imposed by
%       expected_structure. Decoded data contained in decoded_transmission.
%
%       If transmission length does not match expected length, NaN is
%       returned.
%
%       forcing degree is measure of how much forcing was required for
%       decoding
%       
%   arguments:
%       -   msg_buff - a row vector of uint8
%       -   expected_structure - a struct obtined by calling the structure_init function
%       -   mavlink_parser - a parser obatined by calling the MAVLINK_parser function
%       -   xml_path - a path to an xml descriing a mavlink dialect
MESSAGES_PER_TRANSMISSION = expected_structure.num_of_msg;
MSG_LENGTH_SHIFT = 1;
SEQUENCE_SHIFT = 2;
SystemID_SHIFT = 3;
ComponentID_SHIFT = 4;
MsgID_SHIFT = 5;
PAYLOAD_SHIFT = 6;

original_buffer = msg_buff;
%% binray message buffer

binary_msg_buff = reshape( de2bi(msg_buff,8,'right-msb')',1,[]); % transform decimal uint8 to binary

%% degree of forcing
forcing_degree.num_of_struct_symbl = length(expected_structure.bytes_idx);
forcing_degree.bytes_stats = NaN([1, expected_structure.len]);
%1=good byte, 0=bad byte, NaN = not a structure byte
forcing_degree.bytes_stats(expected_structure.bytes_idx) = msg_buff(expected_structure.bytes_idx) == expected_structure.decimal_mask(expected_structure.bytes_idx);
forcing_degree.good_byte_ratio = sum(forcing_degree.bytes_stats,'omitnan')/forcing_degree.num_of_struct_symbl;

forcing_degree.num_of_struct_bits = length(expected_structure.bits_idx);
forcing_degree.bit_stats = NaN([1, expected_structure.len*8]);
forcing_degree.bit_stats(expected_structure.bits_idx) = binary_msg_buff(expected_structure.bits_idx) == expected_structure.binary_mask(expected_structure.bits_idx);
forcing_degree.good_bit_ratio = sum(forcing_degree.bit_stats,'omitnan')/forcing_degree.num_of_struct_bits;

%% force structure
if expected_structure.len == length(msg_buff)
    % force MASK
    msg_buff(expected_structure.bytes_idx) = expected_structure.decimal_mask(expected_structure.bytes_idx);

    %%%% FOR A GENERAL MASK %%%%%
    %decoded_transmission = deserializemsg(dialect,msg_buff);
    
    
    %%%% FOR AN EXTEREMELY SPCIFIC STRUCTURE %%%%%
    %the below code is based on the original implementation of
    %"deserializemsg" within the "mavlinkdialect" class.
    decoded_transmission_no_CRC = robotics.uav.internal.mavlink.Structures.createMsgExt(MESSAGES_PER_TRANSMISSION);
    
%     xml_path = '/Users/yairmazal/Google_Drive/repositories/mavlink/mavlink_scripts/common.xml';
%     msgdef = robotics.uav.internal.mavlink.parser.Import(xml_path);
%     Payload_Parser = robotics.uav.internal.mavlink.parser.PayloadParser(msgdef, double(1));
%     
    
    for idx = 1:MESSAGES_PER_TRANSMISSION
        decoded_transmission_no_CRC(idx).Seq = msg_buff(expected_structure.headers_idx(idx) + SEQUENCE_SHIFT);
        decoded_transmission_no_CRC(idx).SystemID = msg_buff(expected_structure.headers_idx(idx) + SystemID_SHIFT);
        decoded_transmission_no_CRC(idx).ComponentID = msg_buff(expected_structure.headers_idx(idx) + ComponentID_SHIFT);
        decoded_transmission_no_CRC(idx).MsgID = msg_buff(expected_structure.headers_idx(idx) + MsgID_SHIFT);
        decoded_transmission_no_CRC(idx).Payload = mavlink_parser.parse(decoded_transmission_no_CRC(idx).MsgID, ...
            msg_buff(expected_structure.headers_idx(idx) + PAYLOAD_SHIFT: ...
            expected_structure.headers_idx(idx) + PAYLOAD_SHIFT + expected_structure.msg_len(idx)-1)...
        );
    end
    
    decoded_transmission_with_CRC = deserializemsg(mav_dialect(xml_path),msg_buff);
    % fix seq if found any, 
    if ~isempty(decoded_transmission_with_CRC) && length(decoded_transmission_with_CRC) < MESSAGES_PER_TRANSMISSION
        decoded_ids = [decoded_transmission_with_CRC.MsgID];
        
        % first_decoded_id equals a number in the range of
        % 1:MESSAGES_PER_TRANSMISSION of the first correctly decoded
        % message ID.
        first_decoded_id = find(decoded_ids(1)==[expected_structure.msg_ID]);
        
        % if first decoded is is not the first message, force prior sequence ID's.
        if first_decoded_id > 1
            for idx = 1:first_decoded_id-1
                msg_buff(expected_structure.headers_idx(idx) + SEQUENCE_SHIFT) = decoded_transmission_with_CRC(1).Seq - ...
                    MESSAGES_PER_TRANSMISSION + idx + 1;
            end
        end
        % if first decoded is is not the last message, force latter sequence ID's.
        if first_decoded_id < MESSAGES_PER_TRANSMISSION
            for idx  = 1:MESSAGES_PER_TRANSMISSION - first_decoded_id
                if ~ismember(expected_structure.msg_ID(first_decoded_id + idx), decoded_ids) % does this part need fixing?
                    
                    msg_buff(expected_structure.headers_idx(first_decoded_id + idx) + SEQUENCE_SHIFT) = ...
                        decoded_transmission_with_CRC(1).Seq + idx;
                end
            end
        end
        
        % rerun decoding to see if it helped
        decoded_transmission_with_CRC = deserializemsg(mav_dialect(xml_path),msg_buff);
    end
    
    
    
    
else
    decoded_transmission_no_CRC = nan;
end

fixed_bytes = sum(original_buffer ~= msg_buff);
corrected_binary = reshape( de2bi(msg_buff,8,'right-msb')',1,[])'; % transform decimal uint8 to binary
end

