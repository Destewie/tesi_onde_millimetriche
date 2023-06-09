%%
close all
clear all

% Load the position of the MikroTik antennas
load('antennas_mikrotik.mat')

addpath("mD-Track/")

% Calibration
att = 1e-1;

% Number of samples gathered for CSI
num_samples = 300;

% number of antennas
N = 6;

% frequency
freq = 60.48e9;

% speed of light
c = 3e8;

% the wavelength
lambda = c/freq;

% distance between antennas
d = lambda*0.58;

% step for the angle
step_angle =1;

% take the codebook
[cb_az, theta_az] = Grid_AoA(step_angle, N,d,lambda);
[cb_el, theta_el] = Grid_AoA(step_angle, N,d,lambda);

% Load the oscillator
load('Example_data/oscillator.mat')


% Set up the folders
csiFiles = ["csi_24_11_22_test_6_1","csi_24_11_22_test_6_2","csi_24_11_22_test_6_3"];%,"csi_24_11_22_test_6_4","csi_24_11_22_test_6_5","csi_24_11_22_test_6_6"];
    ftmFiles = ["tof_24_11_22_test_6_1","tof_24_11_22_test_6_2","tof_24_11_22_test_6_3"];%,"tof_24_11_22_test_6_4","tof_24_11_22_test_6_5","tof_24_11_22_test_6_6"];
    ext = '.txt';
for k = 1:length(csiFiles)
    currentFolder = pwd;
    csi_filename =append(pwd,'/Example_data/24_11_22/',csiFiles(k), ext);
            ftm_filename = append(pwd ,'/Example_data/24_11_22/' ,ftmFiles(k), ext);
    %% CSI
    [magnitudes, phases, ~] = Parse_csi(csi_filename);
    
    % Clean the data
    pre_channel = zeros(300,6);
    
    % We go up to 30 instead of 32
    % so that 31 and 32 are disabled
    % since they return random data
    for jj=[27,26,28,24,17,19]
    
        a = phases(:, jj);
        a = a*2*pi/1024;
        
        % Move to complex domain
        a = exp(1i*a);
    
        
%         converging_limit = 50;
%         converging_retries = 0;
%         converged = 0;
%         
%         % Sometimes it does not converge at first since the seed is random
%         while converged == 0
%     
%             try
%                 [a, phase_offset_0, converged] = Sanitize(a);
%             catch
%                 disp(['Converging error on file ' csi_filename])
%             end
%     
%             if converging_retries == converging_limit
%     
%                 break
%             end
%     
%             converging_retries = converging_retries + 1;
%         end
%     
%         if converging_retries == converging_limit
%             disp(['Converging threshold reached, ignoring ' csi_filename])
%             continue
%         end
    
        % Remove oscilator
        a = a/exp(1i*antenna_oscilator_phases(antenna_positions == jj));
        
        pre_channel(:, jj==[27,26,28,24,17,19]) = a;
    end
    
    channel = pre_channel.';
    % channel = squeeze(channel(:,4,:));
    % create the codebook
    [cb_aoa, theta] = Grid_AoA(step_angle, N,d,lambda);
    
    % create the correlation matrix
    C = channel * channel';
    
    % apply MUSIC
    [ps_db, D] = MUSIC_alej_unknown(C, cb_aoa, 0);
    
    figure, plot(rad2deg(theta),ps_db)
    
    % Get the angle
    [~, index] = max(ps_db);
    rad2deg(theta(index));
    
    % Encontrar ángulos falsos
    [peaks, locs] = findpeaks(ps_db);
end