function expected_structure = structure_init(stream_len, varargin)
% structure_init  initialize a stuct which contains expected format of received data.
%
%   expected_structure = structure_init(stream_len) returns a struct called expected_structure with the following fields:
%       -   len - length of data stream in bytes
%       -   num_of_msg - number of concatanated MAVLink messages
%       -   headers_idx - indexes of bytes at which messages are expected to begin, i.e. where 0xFE is expected
%       -   msg_len - expected length of MAVLink messages to be received.
%       -   msg_ID - expected IDs of MAVLink messages to be received.
%       -   decimal_mask - a vector of the length of expected transmission. Predetermined values contains values, while unknown values are NaN.
%       -   bytes_idx - a vector of indices where predetermined decimal values exist.
%       -   binary_mask - a vector of the length of expected transmission * 8. Predetermined values contains values in binary representation. undetermined values are 0.
%       -   bits_idx - boolean vector dictatates which bits hold structural data,
%       -   struct_payload_ratio - a ratio of the number of predetermined bytes to the whole transmission length.
%
%   Structural data includes:
%       -   stream length
%       -   SFX byte (0xFE)
%       -   message lengths
%       -   message IDs
%
%   Optional params:
%       -   NumMsg - number of messages in a stream
%       -   HdrIdx - indexes at which a magic marker is expected
%       -   MsgLen - lengths of each MavLink msg in the stream
%       -   MsgId - expected msg ID's



expected_structure.len = stream_len;

%defaults
expected_structure.num_of_msg = 4;
expected_structure.headers_idx = [1 28 46 98];
expected_structure.msg_len = [19 10 44 12];
expected_structure.msg_ID = [212 218 33 234];


%defualt override
for argidx = 1:2:(nargin - 1)
    switch varargin{argidx}
        case 'NumMsg'
            expected_structure.num_of_msg = varargin{argidx+1};
        case 'HdrIdx'
            expected_structure.headers_idx = varargin{argidx+1};
        case 'MsgLen'
            expected_structure.msg_len = varargin{argidx+1};
        case 'MsgId'
            expected_structure.msg_ID = varargin{argidx+1};
    end
end


expected_structure.decimal_mask = NaN([1, expected_structure.len]);
expected_structure.decimal_mask(expected_structure.headers_idx) = 254; % start of frame byte is considered structural
expected_structure.decimal_mask(expected_structure.headers_idx+1) = expected_structure.msg_len; % message length is considered structural
expected_structure.decimal_mask(expected_structure.headers_idx+5) = expected_structure.msg_ID; %  message ID is considered structural

expected_structure.bytes_idx = find(~isnan(expected_structure.decimal_mask));

tmp = expected_structure.decimal_mask;
tmp(isnan(tmp)) = 0;
expected_structure.binary_mask = reshape( de2bi(tmp,8,'right-msb')',1,[]);

expected_structure.bits_idx =  reshape(((expected_structure.bytes_idx' - 1)*8*ones(1,8) + repmat(1:8,length(expected_structure.bytes_idx),1))',1,[]);

expected_structure.struct_payload_ratio = length(expected_structure.bytes_idx)/ expected_structure.len;
end

