function [Pr_omit, Pr_include] = getProbs(omits, includes, rs_expl, rs_attack, th, nbins, rtt)

addpath('aux/');

[ps_omit, taus_omit] = bin_vector(omits, nbins);
[ps_include, taus_include] = bin_vector(includes, nbins);

[l, mu, pi0, mean_rs_expl] = get_params(rs_expl, taus_omit, ps_omit, nbins, 0.05);

k = 1;
while k <= numel(rs_attack)
    Pr_omit = 0;
    Pr_include = 0;
    norm = 0;
    % looping on taus_omits
    for i = 1:nbins   
        % looping on taus_include
        for j = 1:nbins
            % tic
            [p_omit, p_include] = getProbs_det(l, mu, taus_omit(i), taus_include(j), rs_attack(1:k), th, rtt);
            % toc
            if isnan(p_omit) && isnan(p_include)
                % Set both to 0 if they are NaN
                p_omit = 0;
                p_include = 0;
            else
                norm = norm + ps_omit(i)*ps_include(j);
            end
    
            Pr_omit = Pr_omit + ps_omit(i)*ps_include(j)*p_omit;
            Pr_include = Pr_include + ps_omit(i)*ps_include(j)*p_include;
    
        end
    end
    
    Pr_omit = Pr_omit/norm;
    Pr_include = Pr_include/norm;

    if isnan(Pr_omit) && isnan(Pr_include)
        % Remove the current element k from rs_attack
        disp(['Pr(Omit) = ', num2str(Pr_omit), '\nPr(Include) = ', num2str(Pr_include), '\nLambda = ', num2str(l), '\nMu = ', num2str(mu), '\nPi0_1 = ', num2str(pi0(1)), '\nPi0_2 = ', num2str(pi0(2)), '\nPi0_3 = ', num2str(pi0(3)), '\nPi0_4 = ', num2str(pi0(4))]);
        rs_attack(k) = [];
    else
        % Display results if not NaN
        disp(['Pr(Omit) = ', num2str(Pr_omit), '\nPr(Include) = ', num2str(Pr_include), '\nLambda = ', num2str(l), '\nMu = ', num2str(mu), '\nPi0_1 = ', num2str(pi0(1)), '\nPi0_2 = ', num2str(pi0(2)), '\nPi0_3 = ', num2str(pi0(3)), '\nPi0_4 = ', num2str(pi0(4))]);
        k = k + 1; % Increment index only if the current element is not removed
    end

end

end



