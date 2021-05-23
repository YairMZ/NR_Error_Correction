%% setup
%clear
close
clc
set(0,'defaulttextinterpreter','latex')

% addpath(genpath('../shared_functions'))
% load('rafael_data.mat')

%% plots
disp('Rafael HC to ship:')
disp(['Rafael HC to ship success rate: ', num2str(sum([HC_to_Ship.rx_success] == 1)/length(HC_to_Ship))])
disp(['Rafael HC to ship BER: ', num2str(HC_to_Ship_BER)])
%correctable transmissions mean actual mavlink data was sent (tx_length>10), message type was
%correctly received by modem (rx_length == tx_length), and message wasn't succsessfully received (num_of_MAV_msgs_rx <4)
disp(['Rafael HC to ship correctable transimissions: ', num2str(sum([HC_to_Ship.tx_length] > 10 & [HC_to_Ship.rx_length] == [HC_to_Ship.tx_length] & ...
    [HC_to_Ship.rx_success] == 0))])

disp(' ')
disp('Rafael ship to HC:')
disp(['Rafael ship to HC  success rate: ', num2str(sum([ship_to_HC.rx_success] == 1)/length(ship_to_HC))])
disp(['Rafael ship to HC BER: ', num2str(ship_to_HC_BER)])
%correctable transmissions mean actual mavlink data was sent (tx_length>10), message type was
%correctly received by modem (rx_length == tx_length), and message wasn't succsessfully received (num_of_MAV_msgs_rx <4)
disp(['Rafael ship to HC correctable transimissions: ', num2str(sum([ship_to_HC.tx_length] > 10 & [ship_to_HC.rx_length] == [ship_to_HC.tx_length] & ...
    [ship_to_HC.rx_success] == 0 ))])


disp(' ')
mask = ~isnan([HC_to_Ship.HC_depth]);
hcDepth = [HC_to_Ship(mask).HC_depth];
errors_vec = [HC_to_Ship(mask).bit_errors];
tx_length_vec = double(8*[HC_to_Ship(mask).tx_length]);
berVec = errors_vec./tx_length_vec + eps;
groupingVec = [HC_to_Ship(mask).num_of_MAV_msgs_rx];

fig1 = figure(1);
gscatter(hcDepth,berVec, groupingVec,[],[],25);
format_figure(fig1, 'XLabel', 'Depth[m]', 'YLabel', 'BER', 'FontSize', 16, 'FontName', 'mwa_cmr10', 'grid', 'on', 'box', 'on')
%format_figure(fig1, 'XLabel', 'Depth[m]', 'YLabel', 'BER', 'FontSize', 16, 'FontName', 'mwa_cmr10', 'grid', 'on', 'box', 'on','yscale','log')
saveas(fig1,'BER_vs_depth.eps','epsc')
disp(['mean HC depth: ', num2str(nanmean(hcDepth))])
disp(['max HC depth: ', num2str(max(hcDepth))]) 


disp(' ')
mask = ~isnan([HC_to_Ship.range]);
rangeVec = [HC_to_Ship(mask).range];
errors_vec = [HC_to_Ship(mask).bit_errors];
tx_length_vec = double(8*[HC_to_Ship(mask).tx_length]);close all

berVec = errors_vec./tx_length_vec + eps;
groupingVec = [HC_to_Ship(mask).num_of_MAV_msgs_rx];

fig2 = figure(2);
gscatter(rangeVec,berVec, groupingVec,[],[],25);
format_figure(fig2, 'XLabel', 'Range[m]', 'YLabel', 'BER')
saveas(fig2,'BER_vs_range.eps','epsc')


disp(' ')
mask = ~isnan([HC_to_Ship.water_temp]);
xvec = [HC_to_Ship(mask).water_temp];
errors_vec = [HC_to_Ship(mask).bit_errors];
tx_length_vec = double(8*[HC_to_Ship(mask).tx_length]);close all

berVec = errors_vec./tx_length_vec + eps;
groupingVec = [HC_to_Ship(mask).num_of_MAV_msgs_rx];

fig3 = figure(3)
gscatter(xvec,berVec, groupingVec,[],[],25);
format_figure(fig3, 'XLabel', 'Water Temperature [C]', 'YLabel', 'BER')
saveas(fig3,'BER_vs_water_temperature.eps','epsc')


%% tx len


fig4 = figure(4);
nbins = 12;

mask = [HC_to_Ship.tx_length] == 10;
errors_vec = [HC_to_Ship(mask).bit_errors];
tx_length_vec = double(8*[HC_to_Ship(mask).tx_length]);
berVec = errors_vec./tx_length_vec;
subplot(1,3,1);
h1 = histogram(berVec,nbins,'Normalization','probability' );
format_figure(fig4, 'XLabel', 'BER','title', 'TX len = 10B');
ylim([0 0.8])


mask = [HC_to_Ship.tx_length] == 182;
errors_vec = [HC_to_Ship(mask).bit_errors];
tx_length_vec = double(8*[HC_to_Ship(mask).tx_length]);
berVec = errors_vec./tx_length_vec;
subplot(1,3,2);
h2 = histogram(berVec,nbins,'Normalization','probability' );
format_figure(fig4, 'XLabel', 'BER','title', 'TX len = 182B');
ylim([0 0.8])

mask = [HC_to_Ship.tx_length] == 2023;
errors_vec = [HC_to_Ship(mask).bit_errors];
tx_length_vec = double(8*[HC_to_Ship(mask).tx_length]);
berVec = errors_vec./tx_length_vec;
subplot(1,3,3);
h3 = histogram(berVec,nbins,'Normalization','probability' );
format_figure(fig4, 'XLabel', 'BER','title', 'TX len = 2023B');
ylim([0 0.8])

saveas(gcf,'BER_vs_tx_len.eps','epsc')




