function [D,number_of_nan] = KLDiv(P,Q)
%
% Each column of matrices P and Q is a separate random valiable and thus
% they nust have must have the same amount of columns.
%
% For each column the alphabet of P is deduced and then the probability of
% each alphabet element is found both for P and Q.
%
% Then, the divergence is found per coulmn.


if size(P,2)~=size(Q,2)
    error('the number of columns in P and Q should be the same');
end

number_of_nan = 0;

% Establish size of data
[n, m] = size(P);
l = size(Q,1);

% Housekeeping
D = zeros(1,m);

for Column = 1:m
    % Assemble observed alphabet
    Alphabet = unique(P(:,Column));
	
    % Housekeeping
    P_Frequency = zeros(size(Alphabet));
	Q_Frequency = zeros(size(Alphabet));
    
    % Calculate sample frequencies
    for symbol = 1:length(Alphabet)
        P_Frequency(symbol) = sum(P(:,Column) == Alphabet(symbol));
        Q_Frequency(symbol) = sum(Q(:,Column) == Alphabet(symbol));
    end
	
    % Calculate sample class probabilities
    P_prob = P_Frequency / n;
    Q_prob = Q_Frequency / l;
	
    temp =  -P_prob.*log2(Q_prob./P_prob);
    temp(isnan(temp))=0; % resolving the case when Q(i)==0
    if  isinf(sum(temp))
        warning('KLDiv:ill_defined','Some alphabet elements do not appear in Q in column %d, divergence is ill-defined. inf is returned',Column)
        D(Column) = sum(temp);
        number_of_nan = number_of_nan + 1;
    else
        D(Column) = sum(temp);
    end
end


