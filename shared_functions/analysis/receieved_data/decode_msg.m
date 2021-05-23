function decoded_msg = decode_msg(msg_buff,mavlink_parser)
%decode messages using by calling MAVLink decoder and other knowledge
% msg is an a vector of byted received

expected_length = 117; %currently we send only messages of 117 bytes

transmission_structure.valid_length = length(msg_buff) == expected_length;

if transmission_structure.valid_length == 1
    decoded_msg = MAVLink_decode(msg_buff,mavlink_parser);
end


