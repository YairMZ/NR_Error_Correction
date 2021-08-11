clear
clc
load('rafael_data.mat')
tx = [];
rx = [];
success = [];
for idx = 1:length(HC_to_Ship)
    if ~isnan(HC_to_Ship(idx).encoded_rx) & length(HC_to_Ship(idx).encoded_tx) >= 117 & ...
        length(HC_to_Ship(idx).encoded_tx) <= length(HC_to_Ship(idx).encoded_rx)
        tx = [tx; HC_to_Ship(idx).encoded_tx(1:117)];
        rx = [rx; HC_to_Ship(idx).encoded_rx(1:117)];
        success = [success; HC_to_Ship(idx).rx_success];
    end
end

writematrix(tx,"../data/June_20_Rafael/tx.csv");
writematrix(rx,"../data/June_20_Rafael/rx.csv");
writematrix(success',"../data/June_20_Rafael/rx_success.csv");