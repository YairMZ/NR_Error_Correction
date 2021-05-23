set(0,'defaulttextinterpreter','latex')
%% reception to paylod ratio
expected_structure = structure_init();
number_of_structure_bytes = length(expected_structure.bytes_idx);
structural_redundancy_pct = number_of_structure_bytes*100/length(expected_structure.decimal_mask);


%% BER vs. SNR

close all

snr = [received_data.psnr];

gscatter(snr, BER/100, successfully_recovered_msg,[],[],25);

xlabel('SNR')
ylabel('BER')
set(gca,'FontSize',16,'FontName','mwa_cmr10')

box on
grid on


%saveas(gcf,'/Users/yairmazal/Google_Drive/University/PhD/Research_Proposal/V1/gfx/results/BER_vs_SNR.eps','epsc')

%% range
get_ranges;

%% mpd

mpd = mean([received_data.mpd]);
agc = mean([received_data.agc]);
psnr = mean([received_data.psnr]);
rel_v = mean(abs([received_data.rel_spd]));

%% infering structure
clear
clc
close all

A = load('/Users/yairmazal/Google_Drive/repositories/acoustic_tests/Transmitted_data/07_19/10_07_2019_12_20_44_stats.mat','transmitted_data');
transmitted_data = A.transmitted_data;

clear A first_capture last_capture



plot(transmitted_data.entropy_per_bit,'*');


%xlim([1,ceil(length(transmitted_data.entropy_per_bit)*1.05)]);
xlabel('Bit \# in transmission');
ylabel('$H_{tr}$ [bits]') 
set(gca,'FontSize',16,'FontName','mwa_cmr10')

box on
grid on

%saveas(gcf,'/Users/yairmazal/Google_Drive/University/PhD/Research_Proposal/research_proposal/gfx/results/entropy_per_bit.eps','epsc')

close all

histogram(transmitted_data.entropy_per_bit,40,'Normalization','probability')

xlabel('$H_{tr}$ [bits]');
ylabel('Probability') 
set(gca,'FontSize',16,'FontName','mwa_cmr10')

box on
grid on

%print('/Users/yairmazal/Google_Drive/University/PhD/Research_Proposal/research_proposal/gfx/results/entropy_per_bit_distribution.svg','-dsvg')
%saveas(gcf,'/Users/yairmazal/Google_Drive/University/PhD/Research_Proposal/research_proposal/gfx/results/entropy_per_bit_distribution.svg','svg')
% 