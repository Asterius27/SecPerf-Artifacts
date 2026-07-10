function foo = lst_respTime_MErl1PS(l, u, s, k, gam)
    rho = l/u;
    y = (l + u + s - ((l + u + s)^2 - 4*u*l)^(1/2))/(2*l);
    a = l*(1 - y);
    b = (1 - rho*y)^2;
    g = rho*(1 - y)^2;
    h = u*(1 - rho*y^2)/y;
    coeff = (gam*k)^k * (1 - rho) * (1 - rho*y^2) * (1/(b*h^k));

    foo = coeff * (hurwitzLerchPhi(g/b, k, (a+s+k*gam)/h));
 