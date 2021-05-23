clear
clc
close all

myDir = uigetdir; %gets directory
if myDir == 0
    return
end

stat_files = dir(fullfile(myDir, '*_stats.mat'));

data = {};

for file_idx = 1:length(stat_files)
    A = load(fullfile(stat_files(file_idx).folder, stat_files(file_idx).name),'transmitted_data');
    if not(isempty(fieldnames(A)))
        data{file_idx} = A.transmitted_data;
    end
end

%remove empty cells if exist
data = data(~cellfun('isempty',data));

%% plot entropy vs bits
fig = figure('Name','1','units','normalized','outerposition',[0 0 1 1]);
hold on
for datum = data
    plot(datum{1}.entropy_per_bit,'*');
end

legend('1st - mission', '2nd - mission', '3rd - mission', '4th - mission','Location', 'Best');
xlim([1,ceil(length(datum{1}.entropy_per_bit)*1.05)]);
xlabel('Bit # in transmission');
ylabel('Entropy [bits]')

for child = length(fig.Children)
    fig.Children(child).FontSize = 20;
end

box on
grid on

%saveas(fig,fullfile(stat_files(file_idx).folder, 'transmitted_data_entroy'),'epsc')

%% histogram of entropy - one file example
nBins = 100;
fig = figure('Name','2','units','normalized','outerposition',[0 0 1 1]);
h = histogram(data{1,3}.entropy_per_bit,nBins,'Normalization','probability');

average_entropy_per_bit = h.Values*linspace(0,1,nBins)';
