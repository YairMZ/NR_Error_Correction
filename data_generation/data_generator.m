close all
clear
clc
dialect = mavlinkdialect("clustering_dialect.xml", 2);

% empty messages
global_position = createmsg(dialect, 33);
svs = createmsg(dialect, 212);
chamber = createmsg(dialect, 218);
sys_status = createmsg(dialect, 225);
pinger = createmsg(dialect, 234);

%% 1-st mission profile
% mission description: 
%   - 50 messages until diving starts, run on surface
%   - 100 messages of dive stage
%   - 300 messages in cruise. Two turns along track, each after 100 messages.
%   - 50 messages, resufaceing after mission end.
%   - three legs, 90 degrees in first turn, and then straight back to ship.
number_of_messages = 500;

diving_angle = 30*pi/180; % assume diving angle of 30 degrees
velocity = 1; % m/s
message_interval = 5; %sec


%pinger data
% range
range_noise_sig = 2; % range sigma, in meters.
initial_range = 50;
first_leg_final_range = initial_range + velocity*message_interval*199; %first leg is 200 messages long, 100 dive, and 100 straight
second_leg_final_range = sqrt(first_leg_final_range^2 + (velocity*message_interval*99)^2);
third_leg_final_range = second_leg_final_range - (velocity*message_interval*99);
range_noise = [zeros(1,50), range_noise_sig * randn(1, number_of_messages - 50)];
range = [zeros(1,50), linspace(initial_range, first_leg_final_range,200), linspace(first_leg_final_range, second_leg_final_range),...
    linspace(second_leg_final_range, third_leg_final_range), third_leg_final_range * ones(1,50)] + range_noise;
fig = figure(1);
plot(range,'.');
format_figure(fig,'XLabel', 'Message number', 'YLabel','Range [m]','grid','on')

%azimuth
azimuth_noise_sig = 3;  % azimuth sigma, in degrees.
azimuth_noise = azimuth_noise_sig * randn(1, number_of_messages);
azimuth = [zeros(1,50), zeros(1,200), 90* ones(1,100), 120* ones(1,100), 120* ones(1,50)] + azimuth_noise;
fig = figure(2);
plot(azimuth,'.');
format_figure(fig,'XLabel', 'Message number', 'YLabel','Azimuth [deg]','grid','on')

%SYSTEM_STATUS_2
hc_mode = [zeros(1,50), 2*ones(1,100), 2*ones(1,300), 4*ones(1,50)];
hc_system_status = [zeros(1,50), ones(1,100), 2*ones(1,300), 4*ones(1,50)];
hc_err = [zeros(1,450), 8*ones(1,50)];

% chamber status
chamber_pressure = 9.5*ones(1,500) + 0.05*randn(1, number_of_messages);
camber_temperature = [linspace(39,41,50), linspace(41, 37,300), 37*ones(1,115), linspace(37,39,35)] + 0.15*randn(1, number_of_messages);


%svs
depth_noise_sig = [0.25*ones(1,60), 0.15*ones(1,410), 0.25*ones(1,30)];
depth_noise = depth_noise_sig.* randn(1, number_of_messages);
depth = [zeros(1,50), 0:sin(diving_angle):94*sin(diving_angle), 95*sin(diving_angle):sin(diving_angle)/2:104*sin(diving_angle), ...
    104*sin(diving_angle)*ones(1,286), linspace( 104*sin(diving_angle),0,50)];
water_temp_noise = [0.4*ones(1,60), 0.15*ones(1,420), 0.3*ones(1,20)].* randn(1, number_of_messages);
water_temp = 5+25*exp(-depth/200) + water_temp_noise;
depth = depth + depth_noise;
pressure = 101.325+1025*9.81*depth/1000;
Speed_of_Sound = c_water(water_temp, pressure, 40);
figure(3)
plot(Speed_of_Sound)


