%% load data
clear
clc
close all

A = load('/Users/yairmazal/Google_Drive/repositories/acoustic_tests/Transmitted_data/07_19/10_07_2019_12_20_44_stats.mat','transmitted_data');
transmitted_data = A.transmitted_data;
%discard first 7 transmissions, they occured prior to capture, last
%tranmission after capture end.

clear A first_capture last_capture

%% iterate over messages - estimate

number_of_messages = length(transmitted_data.decoded_data);
first_est_idx = 10;
window_length = 20;

for msg_idx = 1:number_of_messages %iterate over messages
    if msg_idx >= first_est_idx
        [inferred_structure(msg_idx).bits_idx,inferred_structure(msg_idx).bits_val, inferred_structure(msg_idx).entropy_est] ...
            = infer_structure(transmitted_data.binary_data(:,1:msg_idx)',number_of_messages,10^-2);
        [inferred_structure_windowed(msg_idx).bits_idx,inferred_structure_windowed(msg_idx).bits_val, ...
            inferred_structure_windowed(msg_idx).entropy_est] ...
            = infer_structure(transmitted_data.binary_data(:,1:msg_idx)', window_length);
    end
end

%% entropy estimate changes - non-windowed


number_of_structure_bits = [];
entropy_diff = [];
entropy_diff_from_final = [];
divergence_from_last = [];
divergence_from_prev = [];
final_data = (transmitted_data.binary_data)';

warning('off','KLDiv:ill_defined');
for msg_idx = 1:number_of_messages %iterate over messages
    if msg_idx >= first_est_idx
        number_of_structure_bits = [number_of_structure_bits length(inferred_structure(msg_idx).bits_idx)];
        entropy_diff_from_final = [entropy_diff_from_final abs(inferred_structure(msg_idx).entropy_est - inferred_structure(45).entropy_est)];
        divergence_from_last = [divergence_from_last; KLDiv(final_data,(transmitted_data.binary_data(:,1:msg_idx))')];
    end
    if msg_idx > first_est_idx
        entropy_diff = [entropy_diff abs(inferred_structure(msg_idx).entropy_est - inferred_structure(msg_idx-1).entropy_est)];
        divergence_from_prev = [divergence_from_prev; ...
            KLDiv((transmitted_data.binary_data(:,1:msg_idx))',(transmitted_data.binary_data(:,1:msg_idx-1))')];
    end
end

warning('on','KLDiv:ill_defined');

%% entropy estimate changes - windowed


number_of_structure_bits_windowed = [];
entropy_diff_windowed = [];
for msg_idx = 1:number_of_messages %iterate over messages
    if msg_idx >= first_est_idx
        number_of_structure_bits_windowed = [number_of_structure_bits_windowed length(inferred_structure_windowed(msg_idx).bits_idx)];
    end
    if msg_idx > first_est_idx
        entropy_diff_windowed = [entropy_diff_windowed abs(inferred_structure_windowed(msg_idx).entropy_est ...
            - inferred_structure_windowed(msg_idx-1).entropy_est)];
    end
end

%% Divergenace


msg_idx = 15;
temp_data = transmitted_data.binary_data(:,1:msg_idx);
warning('off','KLDiv:ill_defined');
[divergence, test] = KLDiv(final_data,temp_data');
warning('on','KLDiv:ill_defined');

%% plots - non-windowed
set(0,'defaulttextinterpreter','latex')



figure(1);
plot(first_est_idx:number_of_messages, number_of_structure_bits,'*')
xlabel('transmission \#');
ylabel('\# of  inferred structure bits')

set(gca,'FontSize',16,'FontName','mwa_cmr10')

box on
grid on


xlim([10 37])

saveas(gcf,'/Users/yairmazal/Google_Drive/University/PhD/Research_Proposal/research_proposal/gfx/results/number_of_structure_bits.eps','epsc')




figure(2);
plot(first_est_idx+1:number_of_messages, mean(entropy_diff,1),'*')
xlabel('transmission \#');
ylabel('$E\left[\left|\hat{H}_i^t-\hat{H}_{i-1}^t\right|\right]$ [bits]')
set(gca,'FontSize',16,'FontName','mwa_cmr10')
box on
grid on

xlim([10 37])

saveas(gcf,'/Users/yairmazal/Google_Drive/University/PhD/Research_Proposal/research_proposal/gfx/results/entropy_est_change.eps','epsc')
% 
% figure(3);
% plot(first_est_idx+1:number_of_messages, max(entropy_diff),'*')
% xlabel('transmission \#');
% ylabel('max$\left[\hat{H}_{i}-\hat{H}_{i-1}\right]$ [bits]')
% set(gca,'FontSize',16,'FontName','mwa_cmr10')
% box on
% grid on


% figure(4);
% plot(first_est_idx:number_of_messages, max(entropy_diff_from_final),'*')
% 
% %% plots - windowed
% figure(5);
% plot(first_est_idx:number_of_messages, number_of_structure_bits_windowed)
% xlabel('transmission \#');
% ylabel('\# of  inferred structure bits')
% 
% set(gca,'FontSize',16,'FontName','mwa_cmr10')
% 
% box on
% grid on
% 
% saveas(gcf,'/Users/yairmazal/Google_Drive/University/PhD/Research_Proposal/V1/gfx/results/number_of_structure_bits_windowed.eps','epsc')
% 
% figure(6);
% plot(first_est_idx+1:number_of_messages, mean(entropy_diff_windowed,1),'*')
% xlabel('transmission \#');
% ylabel('$E\left[\hat{H}_{i}-\hat{H}_{i-1}\right]$ [bits]')
% set(gca,'FontSize',16,'FontName','mwa_cmr10')
% box on
% grid on
% saveas(gcf,'/Users/yairmazal/Google_Drive/University/PhD/Research_Proposal/V1/gfx/results/entropy_est_change_windowed.eps','epsc')
% 
% figure(7);
% plot(first_est_idx+1:number_of_messages, max(entropy_diff_windowed),'*')
% xlabel('transmission \#');
% ylabel('max$\left[\hat{H}_{i}-\hat{H}_{i-1}\right]$ [bits]')
% set(gca,'FontSize',16,'FontName','mwa_cmr10')
% box on
% grid on
% saveas(gcf,'/Users/yairmazal/Google_Drive/University/PhD/Research_Proposal/V1/gfx/results/entropy_est_change_windowed.eps','epsc')
% 
% figure
% plot(10:45,mean(divergence_from_last,2,'omitnan'),'*')

