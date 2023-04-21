function []=Example(arg1, arg2, arg3)

%%
close all
%clear all

% Load the position of the MikroTik antennas
load('antennas_mikrotik.mat')

addpath("mD-Track/")

% Calibration
att = 1e-1;

% Number of samples gathered for CSI
num_samples = 250;

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


% Set up the folders manually
csi_filename = [pwd '/Example_data/csi_measurements.txt'];
ftm_filename = [pwd '/Example_data/ftm_measurements.txt'];
plot_path = [pwd '/Example_data'];

%If Matlab gets called by a script with arguments, set the file names as
%those arguments
if nargin >= 3
    % execute this script with the passed arguments 
    csi_filename = arg1;
    ftm_filename = arg2;
    plot_path = arg3;
end



%% CSI
[magnitudes, phases, ~] = Parse_csi(csi_filename);

% Clean the data
pre_channel = zeros(6, 6, num_samples);

% We go up to 30 instead of 32
% so that 31 and 32 are disabled
% since they return random data
for jj=1:30

    a = phases(:, jj);
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

    [row,col] = find(antenna_positions == jj);
    pre_channel(row, col, :) = a(1:num_samples, :);
end

csi_data = pre_channel;

% Average over the number of samples
csi_data = sum(csi_data,3)/num_samples;

% Apply mD-Track
[Az_estimated, El_estimated, att] = mD_track_2D(csi_data.', cb_az, cb_el);

% move argument to angles
Az_estimated = rad2deg(theta_az(Az_estimated));
El_estimated = rad2deg(theta_el(El_estimated));


% re-estimate azimuth. More info at this paper: Uniform Rectangular Antenna Array Design and Calibration Issues for 2-D ESPRIT Application
Az_estimated_2 = asind(sind(Az_estimated) ./ cosd(El_estimated));

% Power
power = abs(att).^2;

%% FTM
ftm_times = Parse_ftm(ftm_filename);

% Create a histogram
distances = zeros(size(ftm_times, 1), 1);

for i=1:size(ftm_times, 1)

    % Calculate the distance in meters
    T1 = ftm_times(i, 1);
    T2 = ftm_times(i, 2);
    T3 = ftm_times(i, 3);
    T4 = ftm_times(i, 4);

    dist = 3e8 * (((T4-T1)-(T3-T2))*1e-12)/2;

    distances(i, 1) = dist;
end

distance = median(distances) - antenna_ftm_offset;


%% Command window display
clc
disp(['Main path has an azimut of ' num2str(Az_estimated(1)) ' degrees, an elevation of ' num2str(El_estimated(1)) ' degrees and a power of ' num2str(power(1))])
disp(['The other router is at ' num2str(distance) ' meters'])

%% Stem display
stem(Az_estimated, power, LineWidth=2);
hold on; 
xlabel('Azimuth Angle (in deg)');
ylabel('Power (normalized)');
xlim([-90, 90]);
saveas(gcf, fullfile(plot_path, 'plot_image'), 'pdf');

%% 3D display
% r = -10:0.01:10;
% 
% fig3 = figure();
% grid on
% hold on
% for ii = 1 : 15 %length(El_estimated)
%     x = r*cosd(El_estimated(ii))*cosd(Az_estimated(ii));
%     y = r*cosd(El_estimated(ii))*sind(Az_estimated(ii));
%     z = r*sind(El_estimated(ii));
%     p = plot3(x, y, z);
%     p.LineWidth = power(ii)*15;
% end
% set(gca, 'XLim', [-1.5 1.5], 'YLim', [0 4.0], 'ZLim', [-1.0 2.0]); 
% view(60, 20); %imposta in 2 angoli della vista


%% debug
disp(strcat("csi filename= ", csi_filename))
disp(strcat("ftm filename= ", ftm_filename))
disp(strcat("plot path= ", plot_path))

end