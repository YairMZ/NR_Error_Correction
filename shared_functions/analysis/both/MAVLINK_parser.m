function Payload_Parser = MAVLINK_parser(xml_path)
% MAVLINK_parser  instantiate PayloadParser object to parse MAVLink messages.
%
%   parser = MAVLINK_parser() creates a parser based on our standard XML file.
%
%   parser = MAVLINK_parser(xml_path) creates a parser based specified XML file.
%
%   See also mavlinkdialect, deserializemsg.

if nargin < 1
    this_file_path = fileparts(mfilename('fullpath'));
    xml_path = fullfile(this_file_path,'..','..','..','mavlink','mavlink_scripts','common.xml');
    %xml_path = '/Users/yairmazal/Google_Drive/repositories/mavlink/mavlink_scripts/common.xml';
end 

% robotics.uav.internal.loadresources();

%di= mavlinkdialect(xml_path,1);

msgdef = robotics.uav.internal.mavlink.parser.Import(xml_path, 1);

Payload_Parser = robotics.uav.internal.mavlink.parser.PayloadParser(msgdef, double(1));

end

