%% 6073B
h = dvbs2ldpc(3/4);
k = size(h, 2) - size(h, 1);
n = size(h, 2);
nB = k/8-2;

%% 4048B
h = dvbs2ldpc(1/2);
k = size(h, 2) - size(h, 1);
n = size(h, 2);
nB = k/8-2;

%% 2023B
h = dvbs2ldpc(1/4);
k = size(h, 2) - size(h, 1);
n = size(h, 2);
nB = k/8-2;