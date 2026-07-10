function [lam, mu, rho, g0, k0, g1, k1] = get_params_cont_ps(rs_expl, omits, includes)

[phat, pci] = gamfit(omits);
k0 = phat(1);
theta_hat0 = phat(2);
g0 = 1/(k0*theta_hat0);

[phat, pci] = gamfit(includes);
k1 = phat(1);
theta_hat1 = phat(2);
g1 = 1/(k1*theta_hat1);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Compute mean of response times collected during exploration
mean_rs_expl = mean(rs_expl);
v2 = var(rs_expl);

% Compute rho estimate
rho = 1 - (1/(g0*mean_rs_expl));

rho(rho <= 10^-6) = 0;  % Apply the threshold for rho

if rho == 0
    lam = 0;
    mu = 1;
    comps = [];

else

    k0_bot = k0;
    k0_top = k0;
    flag = true;

    solution = false;
    while solution == false

        syms l
        eqn = (( (l/rho) * ((l/rho) * ( (l/rho - l)^2 ) + 2*g0*k0*l*(l/rho - l) + 2*g0^2*k0*l * ( (k0*g0) / (l/rho - l + k0*g0) )^k0 - 2*g0^2*k0*l )) /( g0^2 * k0 * (l/rho - l)^4)) - v2;
        sol_sym = vpasolve(eqn == 0, l);
        sol_double = double(sol_sym);
    
        real_mask = abs(imag(sol_double)) < 1e-12;
        pos_mask = real(sol_double) > 1e-10;
    
        lam = sol_double(real_mask & pos_mask);
    
        if isempty(lam)
            if flag
                k0 = k0_bot * 0.9;
                k0_bot = k0;
                flag = false;
            else
                k0 = k0_top * 1.1;
                k0_top = k0;
                flag = true;
            end
            if k0 < 0.001
                error("Infinite loop...")
            end
        else
            solution = true;
        end
    end

    mu = lam ./ rho;  % Calculate mu)

end

end