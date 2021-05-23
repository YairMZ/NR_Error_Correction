function [strurcture_bit_idx , strurcture_bit_value, inf_entropy] = infer_structure(receptions, window_length ,threshold_ent)
% infer_structure   learns the structure of the reception from the
% previously received bitstream.
%
% binary_receptions is a matrix whose rows are the previous receptions, with
% column dimension equal to the length of the bit stream.
%
% default entropy threshold is 10^-1

[n, m] = size(receptions);
strurcture_bit_idx = zeros(m,1);
strurcture_bit_value = zeros(m,1);
inf_entropy = [];
if n < 10 % a minimal of 10 receptions is required to start learning
    return
end

default_entropy = 10^-1;

if nargin < 2
    window_length = size(receptions,1);
else
    min_p = 1/window_length;
    default_entropy = min((-min_p* log2(min_p) - (1-min_p)*log2(1-min_p))*0.95, default_entropy);
end

if nargin < 3
    threshold_ent = default_entropy;
end

if window_length < size(receptions,1)
    inf_entropy = Entropy(receptions(end-window_length+1:end,:))';
else
    inf_entropy = Entropy(receptions)';
end

strurcture_bit_idx = find(inf_entropy < threshold_ent);
strurcture_bit_value = round(mean(receptions(:,strurcture_bit_idx),1));

end

