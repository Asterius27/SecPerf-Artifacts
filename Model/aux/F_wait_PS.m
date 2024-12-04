function foo = F_wait_PS(l, mu, tau, s)
    rho = l/mu;
    r = (l+mu+s-sqrt((l+mu+s)^2-4*mu*l))/(2*l);
    num = (1-rho)*(1-rho*r^2)*exp(-l*(1-r)*tau);
    den = ((1-rho*r)^2 - (rho*(1-r)^2)*exp(-mu*tau*(1-rho*r^2)/r));
    foo = num/den;
end