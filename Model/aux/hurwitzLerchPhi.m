function phi = hurwitzLerchPhi(z, s, a)
    
    N = 100;
    phi = 0;
    
    % vec = zeros(1, N);
    for n = 0:N-1
        % vec(n+1) = (z^n)*((a+n)^(-s));
        phi = phi + (z^n)*((a+n)^(-s));
    end

    % phi = sum(vec);
    


