function [p,h] = binary_entropy_function(dp)
%binary_entropy_function returns the binary rntropy function computed for probabilities spaced at dp. 

p= dp:dp:1-dp;
h= -p.*log2(p) - (1-p).*log2(1-p);
h = [0,h,0];
p = [0,p,1];
end

