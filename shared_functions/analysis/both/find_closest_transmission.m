function [min_dist, transmission_idx] = find_closest_transmission(received_data,list_of_transmissions)
%find_closest_transmission finds the closest transmission 
%
%   transmission_idx = find_closest_transmission(received_data,list_of_transmissions)
%   finds the closest transmission to received_data among
%   list_of_transmissions. The returned value transmission_idx is the index
%   of the closest transmission in the list.
%
%   received_data is a column vector, and list_of_transmissions is a matrix
%   whose row dimension is the same as received_data.
%
%   The metric used is Hamming distance.

expanded_rec = repmat(received_data, 1, size(list_of_transmissions,2));

Hamming_dist = sum(abs(expanded_rec - list_of_transmissions),1);

[min_dist, transmission_idx] = min(Hamming_dist);

end

