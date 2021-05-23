function [decoded_transmission, binary_msg_buff, msg_buff] = fix_sequence(msg_buff,expected_structure)

SEQUENCE_SHIFT = 2;
MESSAGES_PER_TRANSMISSION = expected_structure.num_of_msg;
decoded_transmission = deserializemsg(mav_dialect(),msg_buff);

if ~isempty(decoded_transmission) && length(decoded_transmission) < MESSAGES_PER_TRANSMISSION  % there are bad messages as well as good ones
    decoded_ids = [decoded_transmission.MsgID];
    
    % first_decoded_id equals a number in the range of
    % 1:MESSAGES_PER_TRANSMISSION of the first correctly decoded
    % message ID.
    first_decoded_id = find(decoded_ids(1)==[expected_structure.msg_ID]);
    
    % if first decoded is is not the first message, force prior
    % sequence ID's.
    if first_decoded_id > 1
        for idx = 1:first_decoded_id-1
            msg_buff(expected_structure.headers_idx(idx) + SEQUENCE_SHIFT) = decoded_transmission(1).Seq - ...
                MESSAGES_PER_TRANSMISSION + idx + 1;
        end
    end
    % if first decoded is not the last message, force later
    % sequence ID's.
    if first_decoded_id < MESSAGES_PER_TRANSMISSION
        for idx  = 1:MESSAGES_PER_TRANSMISSION - first_decoded_id
            if ~ismember(expected_structure.msg_ID(first_decoded_id + idx), decoded_ids) % does this part need fixing?
                
                msg_buff(expected_structure.headers_idx(first_decoded_id + idx) + SEQUENCE_SHIFT) = ...
                    decoded_transmission(1).Seq + idx;
            end
        end
    end
    
    % rerun decoding to see if it helped
    decoded_transmission = deserializemsg(mav_dialect(),msg_buff);
end

binary_msg_buff = reshape( de2bi(msg_buff,8,'right-msb')',1,[])'; % transform decimal uint8 to binary

end

