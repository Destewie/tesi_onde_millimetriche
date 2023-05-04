function [ps_db, D] = MUSIC_alej_unknown(C,S,enableGPu)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
    % The number of samples
    
    if nargin < 3
        enableGPu = false;
        n_e = 1;
    end

    % Estimate eigen values and vectors by eigen decomposition
    % U contains the eigen vector and D contains the eigen value
    [U,D] = eig(C);
    % take the diagonal
%     D = diag(D);
    D = abs( diag(D) );
    % sort them by power
    [D,ind] = sort(D,'descend');
    U = U(:,ind);

    % Normalizaing Eigen values
    D_norm = D./max(D);
    
    % Number of dominant Eigenvalues provide an estimate of maximum number 
    % of sources
    Np = (find(D_norm<10e-3));
    if (length(Np)>=1)
        Un = U(:,Np);     % Noise subspace
    else
%         disp('Noise subspace is null for the given covariance matrix');
%         error('Error.\nMUSIC cannot be applied');
        Un = U(:,end);     % Noise subspace
    end

    % try to do it by GPU if not do it by CPU
    try
    canUseGPU = parallel.gpu.GPUDevice.isAvailable;
    catch ME
    canUseGPU = false;
    end
    if(canUseGPU && enableGPu)
        S_gpu = gpuArray(S);
        Un_gpu = gpuArray(Un);
        ps = sum(abs((S_gpu')*Un_gpu).^2,2);
        ps = ps.^-1;
        ps = gather(ps);
    else
        % Pseudo-spectrum
%         tic
        ps = sum(abs((S')*Un).^2,2);
%         ps = real(ps);
        ps = ps.^-1;
%         toc
    end

    % conver to log scale
    ps_db = 10*log10(ps);

end

