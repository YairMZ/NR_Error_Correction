function [cumulative_dist, transmission_idx, legit_mapping] = match_tranmissions_2_receptions(received_data,list_of_transmissions)
%match_tranmissions_2_receptions finds the closest match
%
%   transmission_idx = match_tranmissions_2_receptions(received_data,list_of_transmissions)
%   finds the closest match between transmissions and receptions.
%   Chronological order is imposed a constraint. The metric used the sum of
%   Hamming distance between mathches.
%
%   The returned value transmission_idx is a vector of indexes
%   of the closest transmissions in the list.
%
%   received_data is matrix whose columns are distinct receptions.
%   list_of_transmissions is a matrix with the same row dimension
%   whose columns are distinct transmissions.
%


number_of_receptions = size(received_data,2);
number_of_transmissions = size(list_of_transmissions,2);

if number_of_transmissions < number_of_receptions %illegitimate mapping
    cumulative_dist = 0;
    transmission_idx = 0;
    legit_mapping = 0;
    return
end

if number_of_receptions == 1 %recursion exit clause
    [cumulative_dist, transmission_idx] = find_closest_transmission(received_data,list_of_transmissions);
    legit_mapping = 1;
    return
end

if number_of_transmissions == number_of_receptions %trivial soultion
    cumulative_dist = sum(abs(received_data - list_of_transmissions),'all');
    transmission_idx = 1:number_of_transmissions;
    legit_mapping = 1;
    return
end


%% number_of_transmissions > number_of_receptions
%initialize mapping - default to first transmissions
[cumulative_dist, transmission_idx, legit_mapping] = ...
    match_tranmissions_2_receptions(received_data,list_of_transmissions(:,1:number_of_receptions));
first_run = true;
min_dist_first = 0;

%iterate recuresively to find best match
for disect_idx = 1:number_of_transmissions - number_of_receptions+1 % disect_idx disects trnasmissions into two groups;
    % where the first recpetion is limited to transmissions up to
    % disect_idx, and the remaining receptions are limited to transmissions
    % above the disection.
    % The disection index cannot go above:
    % number_of_transmissions - number_of_receptions + 1
    % to prevent useless iterations which would yield illegitimate
    % mappings.
    
    min_dist_first_previous = min_dist_first;
    [min_dist_first, transmission_idx_first] = find_closest_transmission(...
        received_data(:,1),list_of_transmissions(:,1:disect_idx));
    
    if disect_idx == 1 || min_dist_first < min_dist_first_previous
        %in the first run (disect_idx == 1) must enter recursion to escape
        %default initialization just in case the best match for the first
        %reception is the first transmission.
        %Otherwise enter recursion only if first recpetion benefits from
        %addittional matching option as the remainder of columns cannot
        %improve from the lost mathcing option.
        
        [min_dist_rest, transmission_idx_rest, legit_mapping] = match_tranmissions_2_receptions(...
            received_data(:,2:end),list_of_transmissions(:,disect_idx+1:end));
        
        if legit_mapping == 1 && min_dist_first + min_dist_rest < cumulative_dist %better match was found
            cumulative_dist = min_dist_first + min_dist_rest;
            transmission_idx = [transmission_idx_first, disect_idx  + transmission_idx_rest];
        end
    end
    
end

