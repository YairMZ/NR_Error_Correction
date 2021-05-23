ranges = [];
range_idx = [];
for trans_idx = 1:34
    if ~isempty(received_data(trans_idx).standard_decode)
        for msg_idx = 1:size(received_data(trans_idx).standard_decode,2)
            if received_data(trans_idx).standard_decode(msg_idx).MsgID == uint32(234)
                ranges = [ranges received_data(trans_idx).standard_decode(msg_idx).Payload.range];
                range_idx = [range_idx trans_idx];
            end
        end
    end
end

figure(1);
gscatter(ranges, snr(range_idx), successfully_recovered_msg(range_idx),[],[],25);

xlabel('range[m]')
ylabel('SNR')
set(gca,'FontSize',16,'FontName','mwa_cmr10')

box on
grid on

figure(2);
gscatter(ranges, BER(range_idx)/100, successfully_recovered_msg(range_idx),[],[],25);

xlabel('range[m]')
ylabel('BER')
set(gca,'FontSize',16,'FontName','mwa_cmr10')

box on
grid on