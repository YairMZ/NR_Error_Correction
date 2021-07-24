clear
close all
clc
load('hc_binary_tx.mat')
binary_matrix = [];

for ii = 1:length(hc_binary_tx)
    if length(hc_binary_tx{ii}) >= 117
        binary_matrix = [binary_matrix; double(hc_binary_tx{ii}(1:117))];
    end
end
binary_matrix(23,:) = []; % delete fucked up row

covariance_across_same_message_bytes =  cov(binary_matrix);
covariance_of_same_byte_across_messages = cov(binary_matrix');

[coeff,score,latent,tsquared,explained,mu] = pca(binary_matrix);

% Coefficient_of_Variance = std(binary_matrix)./mean(binary_matrix);
% figure(1)
% plot(Coefficient_of_Variance,'.')
figure(1)
plot(Entropy(binary_matrix),'.')

figure(2)
plot(std(binary_matrix),'.')

%% analyze features
variance_matrix = var(binary_matrix);
std_matrix = std(binary_matrix);
Coefficient_of_Variance = std(binary_matrix)./mean(binary_matrix);
enrtopy_matrix = Entropy(binary_matrix);
fft_matrix = fft(binary_matrix,[],1);

features = struct();
for ii = 1:117
    feat.variance = variance_matrix(ii);
    
end

%% fft test
t = [];
for ii = 1:117
    t = [t, (abs(fft_matrix(1,ii))^2) / sum(abs(fft_matrix(:,ii)).^2) ];
%     t = [t,  abs(mean(fft_matrix(:,ii))/fft_matrix(1,ii))];
end
plot(t,'.')