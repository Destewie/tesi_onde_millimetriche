function []=Example_MUSIC(arg1, arg2, arg3)

%%
close all

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
step_angle = 1;

% take the codebook
[cb_az, theta_az] = Grid_AoA(step_angle, N,d,lambda);
[cb_el, theta_el] = Grid_AoA(step_angle, N,d,lambda);

% Load the oscillator
load('oscillator_1.mat')


%% Set up the folders
measurement_folder_path = [pwd '\Example_data\2023-05-04_measurements\v1'];
csi_filename = [measurement_folder_path '\csi_measurements_fede.txt'];
ftm_filename = [measurement_folder_path '\ftm_measurements_fede.txt'];

%If Matlab gets called by a script with arguments, set the file names as
%those arguments
if nargin >= 3
    % execute this script with the passed arguments 
    csi_filename = arg1;
    ftm_filename = arg2;
    measurement_folder_path = arg3;
end

processed_data_folder = [measurement_folder_path '\processed_data\music'];
plots_folder = [measurement_folder_path '\plots'];

%% CSI
[magnitudes, phases, ~] = Parse_csi(csi_filename);

% Clean the data
pre_channel = zeros(num_samples,6);

% We go up to 30 instead of 32
% so that 31 and 32 are disabled
% since they return random data
for jj=[27,26,28,24,17,19]

    a = phases(1:num_samples, jj);
    a = a*2*pi/1024;
    
    % Move to complex domain
    a = exp(1i*a);

    
    converging_limit = 50;
    converging_retries = 0;
    converged = 0;
    
    % Sometimes it does not converge at first since the seed is random
    while converged == 0

        try
            [a, phase_offset_0, converged] = Sanitize(a);
        catch
            disp(['Converging error on file ' csi_filename])
        end

        if converging_retries == converging_limit

            break
        end

        converging_retries = converging_retries + 1;
    end

    if converging_retries == converging_limit
        disp(['Converging threshold reached, ignoring ' csi_filename])
        continue
    end

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

%% apply MUSIC
[ps_db, D] = MUSIC_alej_unknown(C, cb_aoa, 0);
theta_deg = rad2deg(theta);

% save these important variables for plotting
mkdir(processed_data_folder)

ps_db_save_path = strcat(processed_data_folder, "\ps_db.mat");
save(ps_db_save_path, 'ps_db');

angles_save_path = strcat(processed_data_folder, "\angles_deg.mat");
save(angles_save_path, 'theta_deg');


%% MUSIC plot
mkdir(plots_folder);

figure
plot(theta_deg, ps_db)
xlabel('Azimuth Angle (in deg)');
ylabel('???')
title('MUSIC plot')
saveas(gcf, fullfile(plots_folder, 'music_plot.pdf'), 'pdf');


% Get the angle
[~, index] = max(ps_db);
theta_deg(index);

% Encontrar ángulos falsos
[peaks, locs] = findpeaks(ps_db);

end