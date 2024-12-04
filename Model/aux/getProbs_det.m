function [Pr_omit, Pr_include] = getProbs_det(l, mu, tau_omit, tau_include, rs, th, rtt)
    
    %%%%%%%%%%%%%%%%%%%%%%% Params %%%%%%%%%%%%%%%%%%%%%%%%%
    addpath('aux/')
    
    funEvals = 150;
    
    met = 'cme';
    
    syms s;
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    w_omit_up = ((rs + th) - rtt) - tau_omit;
    w_omit_lw = ((rs - th) - rtt) - tau_omit;
    
    w_include_up = ((rs + th) - rtt) - tau_include;
    w_include_lw = ((rs - th) - rtt) - tau_include;
    
    % Load is zero
    if l == 0 && mu == 0 
    
        % Initialize f_omit and f_include
        f_omit = (w_omit_lw <= 0 & w_omit_up >= 0);
        f_include = (w_include_lw <= 0 & w_include_up >= 0);
        
    else
        
        F_s = @(s, l, mu, tau) F_wait_PS(l, mu, tau, s)/s;
        
        F = [F_s(s, l, mu, tau_omit), F_s(s, l, mu, tau_include)];
        
        % Initialize f_omit and f_include
        f_omit = zeros(1, numel(rs));
        f_include = zeros(1, numel(rs));
        
        % Compute f_omit_up and f_omit_lw where conditions are satisfied
        valid_w_omit_up = w_omit_up > 0;
        valid_w_omit_lw = w_omit_lw > 0;
        
        f_omit_up = zeros(1, numel(rs));
        f_omit_lw = zeros(1, numel(rs));
        
        f_omit_up(valid_w_omit_up) = matlab_ilt(matlabFunction(F(1)), w_omit_up(valid_w_omit_up), funEvals, met);
        f_omit_lw(valid_w_omit_lw) = matlab_ilt(matlabFunction(F(1)), w_omit_lw(valid_w_omit_lw), funEvals, met);
        
        f_omit = max(f_omit_up - f_omit_lw, 0) .* (abs(f_omit_up - f_omit_lw) >= 10^-4);
        
        % Compute f_include_up and f_include_lw where conditions are satisfied
        valid_w_include_up = w_include_up > 0;
        valid_w_include_lw = w_include_lw > 0;
        
        f_include_up = zeros(1, numel(rs));
        f_include_lw = zeros(1, numel(rs));
        
        f_include_up(valid_w_include_up) = matlab_ilt(matlabFunction(F(2)), w_include_up(valid_w_include_up), funEvals, met);
        f_include_lw(valid_w_include_lw) = matlab_ilt(matlabFunction(F(2)), w_include_lw(valid_w_include_lw), funEvals, met);
        
        f_include = max(f_include_up - f_include_lw, 0) .* (abs(f_include_up - f_include_lw) >= 10^-4);

    end

    % Compute the products
    fprod_omit = prod(f_omit);
    fprod_include = prod(f_include);
    
    % Prior probabilities (assumed to be 0.5 each i.e. no prior knowledge)
    prior_omit = 0.5;
    prior_include = 0.5;
    
    % Compute the posterior probabilities (Pr. of A | B given we observed rs)
    
    denominator = (prior_omit * fprod_omit + prior_include * fprod_include);
    
    Pr_omit = (prior_omit * fprod_omit) / denominator;
    Pr_include = (prior_include * fprod_include) / denominator;
    
    %toc

end



