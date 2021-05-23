function dialect = mav_dialect(xml_path)

if nargin<1
  xml_path = '/Users/yairmazal/repos/mavlink/mavlink_scripts/common.xml';
end

dialect = mavlinkdialect(xml_path,1);

end

