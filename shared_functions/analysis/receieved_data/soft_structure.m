function [decoded_transmission, binary_msg_buff, msg_buff] = soft_structure(msg_buff,inferred_entropy, structure_bits_idx, structure_bits_val, forced_structure, xml_path)
% soft_structure decdodes a transmission based on infered entropy.
%
%   [decoded_transmission,binary_msg_buff, msg_buff] = soft_structure(msg_buff,inferred_entropy, structure_bits_idx, structure_bits_val, forced_structure, xml_path)
%       decodes the data encoded in msg_buff, using the parser object
%       mavlink_parser, while using inferred structure. Decoded data contained in decoded_transmission.
%       
%   arguments:
%       -   msg_buff - a row vector of uint8
%       -   inferred_entropy - described entropy per bit
%       -   structure_bits_idx - infrrred structure bits index
%       -   structure_bits_val - infrrred structure bits value
%       -   forced_structure - a struct obtined by calling the structure_init function
%       -   xml_path - a path to an xml descriing a mavlink dialect


MESSAGES_PER_TRANSMISSION = forced_structure.num_of_msg;

decoded_transmission = deserializemsg(mav_dialect(xml_path),msg_buff);
binary_msg_buff = reshape( de2bi(msg_buff,8,'right-msb')',1,[])'; % transform decimal uint8 to binary

if  length(decoded_transmission) < MESSAGES_PER_TRANSMISSION % if all messages recvoered no need to do anything
    
    if ~isempty(decoded_transmission)  % if some messages are good... 
        decoded_ids = [decoded_transmission.MsgID];
        for idx = 1:MESSAGES_PER_TRANSMISSION
            if ~ismember(forced_structure.msg_ID(idx), decoded_ids) % does this part need fixing?
                begining = (forced_structure.headers_idx(idx) -1) * 8 +1;
                if idx < MESSAGES_PER_TRANSMISSION %if this isn't the last message
                    ending = (forced_structure.headers_idx(idx +1) -1) * 8;
                else
                    ending = length(binary_msg_buff);
                end
                mask = structure_bits_idx(structure_bits_idx >= begining & structure_bits_idx <= ending);
                binary_msg_buff(mask) = structure_bits_val(structure_bits_idx >= begining & structure_bits_idx <= ending);
            end
        end
    else % if all is bad replace all bits and try again
        if max(structure_bits_idx) > 0
            binary_msg_buff(structure_bits_idx) = structure_bits_val;
        end
    end
    msg_buff = bi2de(reshape(binary_msg_buff,8,[])','right-msb')';
    decoded_transmission = deserializemsg(mav_dialect(xml_path),msg_buff);
   
end

end

