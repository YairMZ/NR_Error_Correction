---
title: choice of probability
last_modified_date: 2022-01-17
last_edit_by: yairmazal
---

If we assume a BSC channel with LLR defined by:
```
L_p(c_i) = log(Pr(c_i=0| y_i) / Pr(c_i=1| y_i)) = (-1)^y log((1-p)/p)
```

we can ask how much does the LLR change if we assume a "bad" (higher) bit flip probability which 
is a multiple of a "better" (smaller) one.

Assume two bit flip probabilities such that `p0 = k* p1`, and let us see how does the LLR of zero changes
while assuming small p1, and reasonably small k such that also p0 << 1:

```
L_p1(0) - L_p0(0) ~ log(k) + log(1+p1(k-1)) ~ log(k) + p1(k-1)
```
