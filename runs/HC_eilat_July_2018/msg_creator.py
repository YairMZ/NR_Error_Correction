import scipy.io
import mavlink_utils.HC_dialect as dialect
import pickle
import numpy as np
from scipy.io import savemat

mat = scipy.io.loadmat("data/20_08_2018_13_12_11.mat")
mav = dialect.MAVLink(1, 1, 1)

# global_position_int
global_position_int = mat.get("global_position_int")[0, 1][0][0]
global_position_int_time = global_position_int[0].flatten()
global_position_int_lat = global_position_int[1].flatten()
global_position_int_lon = global_position_int[2].flatten()
global_position_int_alt = global_position_int[3].flatten()
global_position_int_relative_alt = global_position_int[4].flatten()
global_position_int_bottom_distance = global_position_int[5].flatten()
global_position_int_depth = global_position_int[6].flatten()
global_position_int_vx = global_position_int[7].flatten()
global_position_int_vy = global_position_int[8].flatten()
global_position_int_vz = global_position_int[9].flatten()
global_position_int_hdg = global_position_int[10].flatten()

# per plot of depth, actual mission only until data point number 16521
initial_time = global_position_int_time[0]
final_time = global_position_int_time[16521]
delays = [50000, 100000, 200000, 300000]
time_vecs = {}
for delay in delays:
    time_vecs[str(delay)] = np.arange(initial_time, final_time, delay)

# pinger_data
pinger_data = mat.get('pinger_data')[0][0][0][0]
pinger_time = pinger_data[0].flatten()
pinger_range = pinger_data[1].flatten()
pinger_azimuth = pinger_data[2].flatten()

# attitude
attitude = mat.get("attitude")[0, 1][0][0]
attitude_time = attitude[0].flatten()
attitude_roll = attitude[1].flatten()
attitude_pitch = attitude[2].flatten()
attitude_yaw = attitude[3].flatten()
attitude_roll_speed = attitude[4].flatten()
attitude_pitch_speed = attitude[5].flatten()
attitude_yaw_speed = attitude[6].flatten()

# svs_status
svs = mat.get('svs_status')[0][0][0][0]
svs_time = svs[0].flatten()
svs_speed = svs[1].flatten()
svs_depth = svs[2].flatten()
svs_reserved = svs[3].flatten()
svs_temp = svs[4].flatten()
svs_status = svs[5].flatten()

# chamber_status
chamber_status = mat.get('chamber_status')[0][0][0][0]
chamber_status_time = chamber_status[0].flatten()
chamber_status_temp = chamber_status[1].flatten()
chamber_status_hum = chamber_status[2].flatten()
chamber_status_num = chamber_status[3].flatten()
chamber_status_press = chamber_status[4].flatten()

all_msgs: dict = {}
for delay, time_vec in time_vecs.items():
    msgs = []
    # mav.seq = 0
    for t in time_vec:
        d = {"timestamp": t}
        buffer = b""
        idx = np.argmax(global_position_int_time >= t)
        pos = dialect.MAVLink_global_position_int_message(global_position_int_time[idx], global_position_int_lat[idx],
                                                             global_position_int_lon[idx], global_position_int_alt[idx],
                                                             global_position_int_relative_alt[idx],
                                                             global_position_int_bottom_distance[idx],
                                                             global_position_int_depth[idx], global_position_int_vx[idx],
                                                             global_position_int_vy[idx], global_position_int_vz[idx],
                                                             global_position_int_hdg[idx])
        d["position"] = pos
        buffer += pos.pack(mav)
        mav.seq = (mav.seq + 1) % 256

        idx = np.argmax(pinger_time >= t)
        ping = dialect.MAVLink_pinger_data_message(pinger_time[idx],pinger_range[idx], pinger_azimuth[idx])
        d["pinger_data"] = ping
        buffer += ping.pack(mav)
        mav.seq = (mav.seq + 1) % 256

        idx = np.argmax(attitude_time >= t)
        att = dialect.MAVLink_attitude_message(attitude_time[idx], attitude_roll[idx], attitude_pitch[idx],
                                               attitude_yaw[idx], attitude_roll_speed[idx], attitude_pitch_speed[idx],
                                               attitude_yaw_speed[idx])
        d["attitude"] = att
        buffer += att.pack(mav)
        mav.seq = (mav.seq + 1) % 256

        idx = np.argmax(svs_time >= t)
        sv = dialect.MAVLink_scaled_svs_message(svs_time[idx], svs_speed[idx], svs_depth[idx], svs_temp[idx],
                                                svs_status[idx], svs_reserved[idx])
        d["svs"] = sv
        buffer += sv.pack(mav)
        mav.seq = (mav.seq + 1) % 256

        idx = np.argmax(chamber_status_time >= t)
        chamber = dialect.MAVLink_chamber_status_message(chamber_status_time[idx], chamber_status_num[idx],
                                                         chamber_status_press[idx], chamber_status_temp[idx],
                                                         chamber_status_hum[idx])
        d["chamber_status"] = chamber
        buffer += chamber.pack(mav)
        mav.seq = (mav.seq + 1) % 256

        d["bin"] = buffer
        msgs.append(d)
    all_msgs[delay] = msgs

with open('data/hc_to_ship.pickle', 'wb') as file_b:
    pickle.dump(all_msgs, file_b)

five_sec_bin = [[int(b) for b in tx.get("bin")] for tx in all_msgs.get("50000")]
ten_sec_bin = [[int(b) for b in tx.get("bin")] for tx in all_msgs.get("100000")]
twenty_sec_bin = [[int(b) for b in tx.get("bin")] for tx in all_msgs.get("200000")]
thirty_sec_bin = [[int(b) for b in tx.get("bin")] for tx in all_msgs.get("300000")]
savemat("data/binary_buffers.mat", {"five_sec_delay_binary": five_sec_bin, "ten_sec_delay_binary": ten_sec_bin,
                               "twenty_sec_delay_binary": twenty_sec_bin, "thirty_sec_delay_binary": thirty_sec_bin})
