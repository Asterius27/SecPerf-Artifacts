function [Pr_omit, Pr_include] = getProbs_ps(omits, includes, rs_expl, rs_attack, rtt, th)

addpath('aux/');
warning('off', 'all');

[l, mu, rho, g0, k0, g1, k1] = get_params_cont_ps(rs_expl, omits, includes);

k = 1;

while k <= numel(rs_attack)

    [Pr_omit, Pr_include] = get_probs_cont_ps(l, mu, k0, g0, k1, g1, rs_attack(1:k), rtt, th);
    disp(['Pr(Omit) = ', num2str(Pr_omit), '\nPr(Include) = ', num2str(Pr_include), '\nLambda = ', num2str(l), '\nMu = ', num2str(mu), '\nk0 = ', num2str(rho), '\nk1 = ', num2str(rs_attack(k))]);
    k = k + 1;

end

end
