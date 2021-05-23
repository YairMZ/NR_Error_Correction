

clc

lost_packets = [];
for trans = received_data
    lost_packets = [lost_packets; 4-length(trans.standard_decode)];
end
sum(lost_packets)


%% forced

forced_lost_packets = [];
for trans = received_data
    forced_lost_packets = [forced_lost_packets; 4-length(trans.forced_with_CRC)];
end
sum(forced_lost_packets)

%% soft

soft_lost_packets = [];
for trans = received_data
    soft_lost_packets = [soft_lost_packets; 4-length(trans.softStructureDecodeed)];
end
sum(soft_lost_packets)