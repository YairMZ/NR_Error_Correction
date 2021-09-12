import mavlink_utils.clustering_dialect as mav
import numpy as np
import plotly.graph_objects as go  # type: ignore
# import plotly.io as pio

# pio.renderers.default = "svg"   #to render graphs in pycharm and not browser

rng = np.random.default_rng()     # initialize random seed
file = open("mission_log.mavlink", "wb")
mav_obj = mav.MAVLink(file, 1, 1)

# 1-st mission profile
# mission description:
#   - 50 messages until diving starts, run on surface
#   - 100 messages of dive stage
#   - 300 messages in cruise. Two turns along track, each after 100 messages.
#   - 50 messages, resurfacing after mission end.
#   - three legs, 90 degrees in first turn, and then straight back to ship.

number_of_messages = 500
diving_angle = 30*np.pi/180  # assume diving angle of 30 degrees
velocity = 1  # m/s
message_interval = 5  # sec

# pinger data
# range
range_noise_sig = 2  # range sigma, in meters.
initial_range = 50  # meters
# first leg is 200 messages long, 100 dive, and 100 straight
first_leg_final_range = initial_range + (velocity * message_interval * 199)
second_leg_final_range = np.sqrt(first_leg_final_range**2 + (velocity*message_interval*99)**2)
third_leg_final_range = second_leg_final_range - (velocity*message_interval*99)
range_noise = np.concatenate((np.zeros(50), rng.normal(scale=range_noise_sig, size=number_of_messages - 50)))
pinger_range = np.concatenate((np.zeros(50), np.linspace(initial_range, first_leg_final_range, 200),
                               np.linspace(first_leg_final_range, second_leg_final_range, 100),
                               np.linspace(second_leg_final_range, third_leg_final_range, 100),
                               third_leg_final_range * np.ones(50))) + range_noise

fig = go.Figure(data=go.Scatter(y=pinger_range))
fig.show()

# azimuth
azimuth_noise_sig = 3  # azimuth sigma, in degrees.
azimuth_noise = rng.normal(scale=azimuth_noise_sig, size=number_of_messages)
azimuth = np.concatenate((np.zeros(50), np.zeros(200), 90 * np.ones(100), 120 * np.ones(100), 120 * np.ones(50))) + \
          azimuth_noise


fig = go.Figure(data=go.Scatter(y=azimuth))
fig.show()
file.close()

# SYSTEM_STATUS_2
hc_mode = np.concatenate((np.zeros(50), 2*np.ones(100), 2*np.ones(300), 4*np.ones(50)))
hc_system_status = np.concatenate((np.zeros(50), np.ones(100), 2*np.ones(300), 4*np.ones(50)))
hc_err = np.concatenate((np.zeros(450), 8*np.ones(50)))

fig = go.Figure(data=go.Scatter(y=hc_system_status))
fig.show()
file.close()

# chamber status
chamber_pressure = 9.5*np.ones(500) + rng.normal(scale=0.05, size=number_of_messages)
camber_temperature = np.concatenate((np.linspace(39, 41, 50), np.linspace(41, 37, 300), 37*np.ones(115),
                                     np.linspace(37, 39, 35))) + rng.normal(scale=0.15, size=number_of_messages)

fig = go.Figure(data=go.Scatter(y=camber_temperature))
fig.show()
file.close()

# svs
depth_noise_sig = np.concatenate((0.25*np.ones(60), 0.15*np.ones(410), 0.25*np.ones(30)))
depth_noise = depth_noise_sig * rng.normal(scale=depth_noise_sig, size=number_of_messages)
depth = np.concatenate((np.zeros(50), np.linspace(0, 94*np.sin(diving_angle), 95),
                        np.linspace(95*np.sin(diving_angle), 104*np.sin(diving_angle), num=19),
                        104*np.sin(diving_angle)*np.ones(286),
                        np.linspace(104*np.sin(diving_angle), 0, 50)))

water_temp_noise = np.concatenate((0.4*np.ones(60), 0.15*np.ones(420), 0.3*np.ones(20))) * \
    rng.normal(size=number_of_messages)
water_temp = 5+25*np.exp(-depth/200) + water_temp_noise
depth = depth + depth_noise
pressure = 101.325+1025*9.81*depth/1000
# Speed_of_Sound = c_water(water_temp, pressure, 40);
# figure(3)
# plot(Speed_of_Sound)
