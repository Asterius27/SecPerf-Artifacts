function [l, mu, pi0, mean_rs_expl] = get_params(rs_expl, taus_omit, ps_omit, nbins, delta)

    % Compute mean of response times collected during exploration
    mean_rs_expl = mean(rs_expl);
    % Compute rhos for all possible taus_omit (centroids computed from
    % service time of omit class observations)
    rho = 1 - (sum(taus_omit.*ps_omit) / mean_rs_expl);
    rho(rho <= 10^-6) = 0;  % Apply the threshold for rho
    
    if rho == 0
        
        l = 0;
        mu = 0;
        pi0 = [0, 0, 0, 0];
    
    else
    
        % Compute lower and upper bounds for all taus_omit (so to have the interval to compute pi0)
        lower_bounds = taus_omit * (1 - delta);
        upper_bounds = taus_omit * (1 + delta);
    
        % Initialize pi0
        pi0 = arrayfun(@(i) sum(rs_expl >= lower_bounds(i) & rs_expl <= upper_bounds(i)) / numel(rs_expl), 1:nbins);
        % Apply the threshold for pi0
        pi0(pi0 <= 0) = 0.001;  % Replace values less than or equal to 0 with 0.001
        % Calculate l
        l = -log(pi0 ./ (1 - rho)) .* (1 ./ taus_omit);
        l = sum(ps_omit.*l);
    
        l(l <= 0) = 0.001;  % Apply the threshold for l
        % Calculate mu
        mu = l ./ rho;
    end
end