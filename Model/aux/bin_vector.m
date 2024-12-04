function [props, centroids] = bin_vector(vector, n)
  
    % Create bin edges uniformly between min and max
    binEdges = linspace(min(vector), max(vector), n + 1);

    % Get the histogram counts for each bin
    [counts, ~, binIndices] = histcounts(vector, binEdges);

    tot = numel(vector);

    props = counts / tot;

    % Calculate the centroids of each bin
    centroids = zeros(1, n);

    for i = 1:n
        % Find the observations that fall into the i-th bin
        binObservations = vector(binIndices == i);
        
        % Compute the centroid as the mean of these observations, or leave it NaN if no observations fall in the bin
        if ~isempty(binObservations)
            centroids(i) = mean(binObservations);
        else
            centroids(i) = (binEdges(i) + binEdges(i + 1)) / 2;  % Or set to some default value if no observations in the bin
        end
    end


end

