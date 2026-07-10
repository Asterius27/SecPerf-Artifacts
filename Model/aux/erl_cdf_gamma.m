% function [val] = erl_cdf(x, k, l)

% acc = 0;
% for n = 0:k-1
%     acc = acc + (1/factorial(n)) * exp(-k*l*x) * (k*l*x)^n;
% end
% 
% val = 1 - acc;
% end
function [val] = erl_cdf_gamma(x, k, l)
% The Erlang CDF is equivalent to the regularized lower incomplete gamma function.
% Here, the rate lambda = k * l.
% The arguments for gammainc are ( integration_limit, shape_parameter ).

val = gammainc((k * l) * x, k);
end