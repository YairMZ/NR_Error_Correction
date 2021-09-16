import array
import struct
from typing import Any, Tuple, List, BinaryIO, Callable, Sequence
from collections.abc import MutableSequence

WIRE_PROTOCOL_VERSION: str
DIALECT: str
PROTOCOL_MARKER_V1: int
PROTOCOL_MARKER_V2: int
HEADER_LEN_V1: int
HEADER_LEN_V2: int
MAVLINK_SIGNATURE_BLOCK_LEN: int
MAVLINK_IFLAG_SIGNED: int
native_supported: bool
native_force: bool
native_testing: bool
MAVLINK_IGNORE_CRC: int
MAVLINK_TYPE_CHAR: int
MAVLINK_TYPE_UINT8_T: int
MAVLINK_TYPE_INT8_T: int
MAVLINK_TYPE_UINT16_T: int
MAVLINK_TYPE_INT16_T: int
MAVLINK_TYPE_UINT32_T: int
MAVLINK_TYPE_INT32_T: int
MAVLINK_TYPE_UINT64_T: int
MAVLINK_TYPE_INT64_T: int
MAVLINK_TYPE_FLOAT: int
MAVLINK_TYPE_DOUBLE: int

def to_string(s: Any): ...

class MAVLink_header:
    mlen: int
    seq: int
    srcSystem: int
    srcComponent: int
    msgId: int
    incompat_flags: Any
    compat_flags: Any
    def __init__(self, msgId: int, incompat_flags: int = ..., compat_flags: int = ..., mlen: int = ...,
                 seq: int = ..., srcSystem: int = ..., srcComponent: int = ...) -> None: ...
    def pack(self, force_mavlink1: bool = ...) -> bytes: ...

class MAVLink_message:
    def __init__(self, msgId: int, name: str) -> None: ...
    def format_attr(self, field: Any) -> Any: ...
    def get_msgbuf(self) -> bytearray: ...
    def get_header(self) -> MAVLink_header: ...
    def get_payload(self) -> MutableSequence[int]: ...
    def get_crc(self) -> Tuple[bytes]: ...
    def get_fieldnames(self) -> List[str]: ...
    def get_type(self) -> int: ...
    def get_msgId(self) -> int: ...
    def get_srcSystem(self) -> int: ...
    def get_srcComponent(self) -> int: ...
    def get_seq(self) -> int: ...
    def get_signed(self) -> bool: ...
    def get_link_id(self) -> int: ...
    def __ne__(self, other) -> bool: ...
    def __eq__(self, other) -> bool: ...
    def to_dict(self) -> dict[Any]: ...
    def to_json(self)-> str: ...
    def sign_packet(self, mav: MAVLink) -> None: ...
    def pack(self, mav: MAVLink, crc_extra: int, payload: MutableSequence[int], force_mavlink1: bool = ...
             ) -> MutableSequence[int]: ...
    def __getitem__(self, key: Any) -> Any: ...

class EnumEntry:
    name: str
    description: str
    param: dict
    def __init__(self, name, description) -> None: ...

enums: dict[str, dict[int, EnumEntry]]
MAV_AUTOPILOT_GENERIC: int
MAV_AUTOPILOT_RESERVED: int
MAV_AUTOPILOT_SLUGS: int
MAV_AUTOPILOT_ARDUPILOTMEGA: int
MAV_AUTOPILOT_OPENPILOT: int
MAV_AUTOPILOT_GENERIC_WAYPOINTS_ONLY: int
MAV_AUTOPILOT_GENERIC_WAYPOINTS_AND_SIMPLE_NAVIGATION_ONLY: int
MAV_AUTOPILOT_GENERIC_MISSION_FULL: int
MAV_AUTOPILOT_INVALID: int
MAV_AUTOPILOT_PPZ: int
MAV_AUTOPILOT_UDB: int
MAV_AUTOPILOT_FP: int
MAV_AUTOPILOT_PX4: int
MAV_AUTOPILOT_SMACCMPILOT: int
MAV_AUTOPILOT_AUTOQUAD: int
MAV_AUTOPILOT_ARMAZILA: int
MAV_AUTOPILOT_AEROB: int
MAV_AUTOPILOT_ASLUAV: int
MAV_AUTOPILOT_ENUM_END: int
MAV_TYPE_GENERIC: int
MAV_TYPE_FIXED_WING: int
MAV_TYPE_QUADROTOR: int
MAV_TYPE_COAXIAL: int
MAV_TYPE_HELICOPTER: int
MAV_TYPE_ANTENNA_TRACKER: int
MAV_TYPE_GCS: int
MAV_TYPE_AIRSHIP: int
MAV_TYPE_FREE_BALLOON: int
MAV_TYPE_ROCKET: int
MAV_TYPE_GROUND_ROVER: int
MAV_TYPE_SURFACE_BOAT: int
MAV_TYPE_SUBMARINE: int
MAV_TYPE_HEXAROTOR: int
MAV_TYPE_OCTOROTOR: int
MAV_TYPE_TRICOPTER: int
MAV_TYPE_FLAPPING_WING: int
MAV_TYPE_KITE: int
MAV_TYPE_ONBOARD_CONTROLLER: int
MAV_TYPE_VTOL_DUOROTOR: int
MAV_TYPE_VTOL_QUADROTOR: int
MAV_TYPE_VTOL_TILTROTOR: int
MAV_TYPE_VTOL_RESERVED2: int
MAV_TYPE_VTOL_RESERVED3: int
MAV_TYPE_VTOL_RESERVED4: int
MAV_TYPE_VTOL_RESERVED5: int
MAV_TYPE_GIMBAL: int
MAV_TYPE_ADSB: int
MAV_TYPE_ENUM_END: int
FIRMWARE_VERSION_TYPE_DEV: int
FIRMWARE_VERSION_TYPE_ALPHA: int
FIRMWARE_VERSION_TYPE_BETA: int
FIRMWARE_VERSION_TYPE_RC: int
FIRMWARE_VERSION_TYPE_OFFICIAL: int
FIRMWARE_VERSION_TYPE_ENUM_END: int
MAV_MODE_FLAG_CUSTOM_MODE_ENABLED: int
MAV_MODE_FLAG_TEST_ENABLED: int
MAV_MODE_FLAG_AUTO_ENABLED: int
MAV_MODE_FLAG_GUIDED_ENABLED: int
MAV_MODE_FLAG_STABILIZE_ENABLED: int
MAV_MODE_FLAG_HIL_ENABLED: int
MAV_MODE_FLAG_MANUAL_INPUT_ENABLED: int
MAV_MODE_FLAG_SAFETY_ARMED: int
MAV_MODE_FLAG_ENUM_END: int
MAV_MODE_FLAG_DECODE_POSITION_CUSTOM_MODE: int
MAV_MODE_FLAG_DECODE_POSITION_TEST: int
MAV_MODE_FLAG_DECODE_POSITION_AUTO: int
MAV_MODE_FLAG_DECODE_POSITION_GUIDED: int
MAV_MODE_FLAG_DECODE_POSITION_STABILIZE: int
MAV_MODE_FLAG_DECODE_POSITION_HIL: int
MAV_MODE_FLAG_DECODE_POSITION_MANUAL: int
MAV_MODE_FLAG_DECODE_POSITION_SAFETY: int
MAV_MODE_FLAG_DECODE_POSITION_ENUM_END: int
MAV_GOTO_DO_HOLD: int
MAV_GOTO_DO_CONTINUE: int
MAV_GOTO_HOLD_AT_CURRENT_POSITION: int
MAV_GOTO_HOLD_AT_SPECIFIED_POSITION: int
MAV_GOTO_ENUM_END: int
MAV_MODE_PREFLIGHT: int
MAV_MODE_STOP: int
MAV_MODE_MANUAL_DISARMED: int
MAV_MODE_TEST_DISARMED: int
MAV_MODE_STABILIZE_DISARMED: int
MAV_MODE_GUIDED_DISARMED: int
MAV_MODE_AUTO_DISARMED: int
MAV_MODE_MANUAL_ARMED: int
MAV_MODE_TEST_ARMED: int
MAV_MODE_STABILIZE_ARMED: int
MAV_MODE_GUIDED_ARMED: int
MAV_MODE_AUTO_ARMED: int
MAV_MODE_ENUM_END: int
MAV_STATE_UNINIT: int
MAV_STATE_BOOT: int
MAV_STATE_CALIBRATING: int
MAV_STATE_STANDBY: int
MAV_STATE_ACTIVE: int
MAV_STATE_CRITICAL: int
MAV_STATE_EMERGENCY: int
MAV_STATE_POWEROFF: int
MAV_STATE_ENUM_END: int
MAV_COMP_ID_ALL: int
MAV_COMP_ID_CAMERA: int
MAV_COMP_ID_SERVO1: int
MAV_COMP_ID_SERVO2: int
MAV_COMP_ID_SERVO3: int
MAV_COMP_ID_SERVO4: int
MAV_COMP_ID_SERVO5: int
MAV_COMP_ID_SERVO6: int
MAV_COMP_ID_SERVO7: int
MAV_COMP_ID_SERVO8: int
MAV_COMP_ID_SERVO9: int
MAV_COMP_ID_SERVO10: int
MAV_COMP_ID_SERVO11: int
MAV_COMP_ID_SERVO12: int
MAV_COMP_ID_SERVO13: int
MAV_COMP_ID_SERVO14: int
MAV_COMP_ID_GIMBAL: int
MAV_COMP_ID_LOG: int
MAV_COMP_ID_ADSB: int
MAV_COMP_ID_MAPPER: int
MAV_COMP_ID_MISSIONPLANNER: int
MAV_COMP_ID_PATHPLANNER: int
MAV_COMP_ID_IMU: int
MAV_COMP_ID_IMU_2: int
MAV_COMP_ID_IMU_3: int
MAV_COMP_ID_GPS: int
MAV_COMP_ID_UDP_BRIDGE: int
MAV_COMP_ID_UART_BRIDGE: int
MAV_COMP_ID_SYSTEM_CONTROL: int
MAV_COMPONENT_ENUM_END: int
MAV_SYS_STATUS_SENSOR_3D_GYRO: int
MAV_SYS_STATUS_SENSOR_3D_ACCEL: int
MAV_SYS_STATUS_SENSOR_3D_MAG: int
MAV_SYS_STATUS_SENSOR_ABSOLUTE_PRESSURE: int
MAV_SYS_STATUS_SENSOR_DIFFERENTIAL_PRESSURE: int
MAV_SYS_STATUS_SENSOR_GPS: int
MAV_SYS_STATUS_SENSOR_OPTICAL_FLOW: int
MAV_SYS_STATUS_SENSOR_VISION_POSITION: int
MAV_SYS_STATUS_SENSOR_LASER_POSITION: int
MAV_SYS_STATUS_SENSOR_EXTERNAL_GROUND_TRUTH: int
MAV_SYS_STATUS_SENSOR_ANGULAR_RATE_CONTROL: int
MAV_SYS_STATUS_SENSOR_ATTITUDE_STABILIZATION: int
MAV_SYS_STATUS_SENSOR_YAW_POSITION: int
MAV_SYS_STATUS_SENSOR_Z_ALTITUDE_CONTROL: int
MAV_SYS_STATUS_SENSOR_XY_POSITION_CONTROL: int
MAV_SYS_STATUS_SENSOR_MOTOR_OUTPUTS: int
MAV_SYS_STATUS_SENSOR_RC_RECEIVER: int
MAV_SYS_STATUS_SENSOR_3D_GYRO2: int
MAV_SYS_STATUS_SENSOR_3D_ACCEL2: int
MAV_SYS_STATUS_SENSOR_3D_MAG2: int
MAV_SYS_STATUS_GEOFENCE: int
MAV_SYS_STATUS_AHRS: int
MAV_SYS_STATUS_TERRAIN: int
MAV_SYS_STATUS_SENSOR_ENUM_END: int
MAV_FRAME_GLOBAL: int
MAV_FRAME_LOCAL_NED: int
MAV_FRAME_MISSION: int
MAV_FRAME_GLOBAL_RELATIVE_ALT: int
MAV_FRAME_LOCAL_ENU: int
MAV_FRAME_GLOBAL_INT: int
MAV_FRAME_GLOBAL_RELATIVE_ALT_INT: int
MAV_FRAME_LOCAL_OFFSET_NED: int
MAV_FRAME_BODY_NED: int
MAV_FRAME_BODY_OFFSET_NED: int
MAV_FRAME_GLOBAL_TERRAIN_ALT: int
MAV_FRAME_GLOBAL_TERRAIN_ALT_INT: int
MAV_FRAME_HCMISSION: int
MAV_FRAME_ENUM_END: int
MAVLINK_DATA_STREAM_IMG_JPEG: int
MAVLINK_DATA_STREAM_IMG_BMP: int
MAVLINK_DATA_STREAM_IMG_RAW8U: int
MAVLINK_DATA_STREAM_IMG_RAW32U: int
MAVLINK_DATA_STREAM_IMG_PGM: int
MAVLINK_DATA_STREAM_IMG_PNG: int
MAVLINK_DATA_STREAM_TYPE_ENUM_END: int
FENCE_ACTION_NONE: int
FENCE_ACTION_GUIDED: int
FENCE_ACTION_REPORT: int
FENCE_ACTION_GUIDED_THR_PASS: int
FENCE_ACTION_ENUM_END: int
FENCE_BREACH_NONE: int
FENCE_BREACH_MINALT: int
FENCE_BREACH_MAXALT: int
FENCE_BREACH_BOUNDARY: int
FENCE_BREACH_ENUM_END: int
MAV_MOUNT_MODE_RETRACT: int
MAV_MOUNT_MODE_NEUTRAL: int
MAV_MOUNT_MODE_MAVLINK_TARGETING: int
MAV_MOUNT_MODE_RC_TARGETING: int
MAV_MOUNT_MODE_GPS_POINT: int
MAV_MOUNT_MODE_ENUM_END: int
MAV_CMD_NAV_WAYPOINT: int
MAV_CMD_NAV_LOITER_UNLIM: int
MAV_CMD_NAV_LOITER_TURNS: int
MAV_CMD_NAV_LOITER_TIME: int
MAV_CMD_NAV_RETURN_TO_LAUNCH: int
MAV_CMD_NAV_LAND: int
MAV_CMD_NAV_SAFETY_REGION: int
MAV_CMD_NAV_LAND_LOCAL: int
MAV_CMD_NAV_TAKEOFF_LOCAL: int
MAV_CMD_NAV_FOLLOW: int
MAV_CMD_NAV_CONTINUE_AND_CHANGE_ALT: int
MAV_CMD_NAV_LOITER_TO_ALT: int
MAV_CMD_NAV_ROI: int
MAV_CMD_NAV_PATHPLANNING: int
MAV_CMD_NAV_SPLINE_WAYPOINT: int
MAV_CMD_NAV_VTOL_TAKEOFF: int
MAV_CMD_NAV_VTOL_LAND: int
MAV_CMD_NAV_GUIDED_ENABLE: int
MAV_CMD_NAV_LAST: int
MAV_CMD_CONDITION_DELAY: int
MAV_CMD_CONDITION_CHANGE_ALT: int
MAV_CMD_CONDITION_DISTANCE: int
MAV_CMD_CONDITION_YAW: int
MAV_CMD_CONDITION_LAST: int
MAV_CMD_DO_SET_MODE: int
MAV_CMD_DO_JUMP: int
MAV_CMD_DO_CHANGE_SPEED: int
MAV_CMD_DO_SET_HOME: int
MAV_CMD_DO_SET_PARAMETER: int
MAV_CMD_DO_SET_RELAY: int
MAV_CMD_DO_REPEAT_RELAY: int
MAV_CMD_DO_SET_SERVO: int
MAV_CMD_DO_REPEAT_SERVO: int
MAV_CMD_DO_FLIGHTTERMINATION: int
MAV_CMD_DO_LAND_START: int
MAV_CMD_DO_RALLY_LAND: int
MAV_CMD_DO_GO_AROUND: int
MAV_CMD_DO_CONTROL_VIDEO: int
MAV_CMD_DO_SET_ROI: int
MAV_CMD_DO_DIGICAM_CONFIGURE: int
MAV_CMD_DO_DIGICAM_CONTROL: int
MAV_CMD_DO_MOUNT_CONFIGURE: int
MAV_CMD_DO_MOUNT_CONTROL: int
MAV_CMD_DO_SET_CAM_TRIGG_DIST: int
MAV_CMD_DO_FENCE_ENABLE: int
MAV_CMD_DO_PARACHUTE: int
MAV_CMD_DO_INVERTED_FLIGHT: int
MAV_CMD_DO_MOUNT_CONTROL_QUAT: int
MAV_CMD_DO_GUIDED_MASTER: int
MAV_CMD_DO_GUIDED_LIMITS: int
MAV_CMD_DO_LAST: int
MAV_CMD_PREFLIGHT_CALIBRATION: int
MAV_CMD_PREFLIGHT_SET_SENSOR_OFFSETS: int
MAV_CMD_PREFLIGHT_UAVCAN: int
MAV_CMD_PREFLIGHT_STORAGE: int
MAV_CMD_PREFLIGHT_REBOOT_SHUTDOWN: int
MAV_CMD_OVERRIDE_GOTO: int
MAV_CMD_MISSION_START: int
MAV_CMD_COMPONENT_ARM_DISARM: int
MAV_CMD_GET_HOME_POSITION: int
MAV_CMD_START_RX_PAIR: int
MAV_CMD_GET_MESSAGE_INTERVAL: int
MAV_CMD_SET_MESSAGE_INTERVAL: int
MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES: int
MAV_CMD_IMAGE_START_CAPTURE: int
MAV_CMD_IMAGE_STOP_CAPTURE: int
MAV_CMD_DO_TRIGGER_CONTROL: int
MAV_CMD_VIDEO_START_CAPTURE: int
MAV_CMD_VIDEO_STOP_CAPTURE: int
MAV_CMD_PANORAMA_CREATE: int
MAV_CMD_DO_VTOL_TRANSITION: int
MAV_CMD_PAYLOAD_PREPARE_DEPLOY: int
MAV_CMD_PAYLOAD_CONTROL_DEPLOY: int
MAV_CMD_ENUM_END: int
MAV_DATA_STREAM_ALL: int
MAV_DATA_STREAM_RAW_SENSORS: int
MAV_DATA_STREAM_EXTENDED_STATUS: int
MAV_DATA_STREAM_RC_CHANNELS: int
MAV_DATA_STREAM_RAW_CONTROLLER: int
MAV_DATA_STREAM_POSITION: int
MAV_DATA_STREAM_EXTRA1: int
MAV_DATA_STREAM_EXTRA2: int
MAV_DATA_STREAM_EXTRA3: int
MAV_DATA_STREAM_ENUM_END: int
MAV_ROI_NONE: int
MAV_ROI_WPNEXT: int
MAV_ROI_WPINDEX: int
MAV_ROI_LOCATION: int
MAV_ROI_TARGET: int
MAV_ROI_ENUM_END: int
MAV_CMD_ACK_OK: int
MAV_CMD_ACK_ERR_FAIL: int
MAV_CMD_ACK_ERR_ACCESS_DENIED: int
MAV_CMD_ACK_ERR_NOT_SUPPORTED: int
MAV_CMD_ACK_ERR_COORDINATE_FRAME_NOT_SUPPORTED: int
MAV_CMD_ACK_ERR_COORDINATES_OUT_OF_RANGE: int
MAV_CMD_ACK_ERR_X_LAT_OUT_OF_RANGE: int
MAV_CMD_ACK_ERR_Y_LON_OUT_OF_RANGE: int
MAV_CMD_ACK_ERR_Z_ALT_OUT_OF_RANGE: int
MAV_CMD_ACK_ENUM_END: int
MAV_PARAM_TYPE_UINT8: int
MAV_PARAM_TYPE_INT8: int
MAV_PARAM_TYPE_UINT16: int
MAV_PARAM_TYPE_INT16: int
MAV_PARAM_TYPE_UINT32: int
MAV_PARAM_TYPE_INT32: int
MAV_PARAM_TYPE_UINT64: int
MAV_PARAM_TYPE_INT64: int
MAV_PARAM_TYPE_REAL32: int
MAV_PARAM_TYPE_REAL64: int
MAV_PARAM_TYPE_ENUM_END: int
MAV_RESULT_ACCEPTED: int
MAV_RESULT_TEMPORARILY_REJECTED: int
MAV_RESULT_DENIED: int
MAV_RESULT_UNSUPPORTED: int
MAV_RESULT_FAILED: int
MAV_RESULT_ENUM_END: int
MAV_MISSION_ACCEPTED: int
MAV_MISSION_ERROR: int
MAV_MISSION_UNSUPPORTED_FRAME: int
MAV_MISSION_UNSUPPORTED: int
MAV_MISSION_NO_SPACE: int
MAV_MISSION_INVALID: int
MAV_MISSION_INVALID_PARAM1: int
MAV_MISSION_INVALID_PARAM2: int
MAV_MISSION_INVALID_PARAM3: int
MAV_MISSION_INVALID_PARAM4: int
MAV_MISSION_INVALID_PARAM5_X: int
MAV_MISSION_INVALID_PARAM6_Y: int
MAV_MISSION_INVALID_PARAM7: int
MAV_MISSION_INVALID_SEQUENCE: int
MAV_MISSION_DENIED: int
MAV_MISSION_RESULT_ENUM_END: int
MAV_SEVERITY_EMERGENCY: int
MAV_SEVERITY_ALERT: int
MAV_SEVERITY_CRITICAL: int
MAV_SEVERITY_ERROR: int
MAV_SEVERITY_WARNING: int
MAV_SEVERITY_NOTICE: int
MAV_SEVERITY_INFO: int
MAV_SEVERITY_DEBUG: int
MAV_SEVERITY_ENUM_END: int
MAV_POWER_STATUS_BRICK_VALID: int
MAV_POWER_STATUS_SERVO_VALID: int
MAV_POWER_STATUS_USB_CONNECTED: int
MAV_POWER_STATUS_PERIPH_OVERCURRENT: int
MAV_POWER_STATUS_PERIPH_HIPOWER_OVERCURRENT: int
MAV_POWER_STATUS_CHANGED: int
MAV_POWER_STATUS_ENUM_END: int
SERIAL_CONTROL_DEV_TELEM1: int
SERIAL_CONTROL_DEV_TELEM2: int
SERIAL_CONTROL_DEV_GPS1: int
SERIAL_CONTROL_DEV_GPS2: int
SERIAL_CONTROL_DEV_SHELL: int
SERIAL_CONTROL_DEV_ENUM_END: int
SERIAL_CONTROL_FLAG_REPLY: int
SERIAL_CONTROL_FLAG_RESPOND: int
SERIAL_CONTROL_FLAG_EXCLUSIVE: int
SERIAL_CONTROL_FLAG_BLOCKING: int
SERIAL_CONTROL_FLAG_MULTI: int
SERIAL_CONTROL_FLAG_ENUM_END: int
MAV_DISTANCE_SENSOR_LASER: int
MAV_DISTANCE_SENSOR_ULTRASOUND: int
MAV_DISTANCE_SENSOR_INFRARED: int
MAV_DISTANCE_SENSOR_ENUM_END: int
MAV_SENSOR_ROTATION_NONE: int
MAV_SENSOR_ROTATION_YAW_45: int
MAV_SENSOR_ROTATION_YAW_90: int
MAV_SENSOR_ROTATION_YAW_135: int
MAV_SENSOR_ROTATION_YAW_180: int
MAV_SENSOR_ROTATION_YAW_225: int
MAV_SENSOR_ROTATION_YAW_270: int
MAV_SENSOR_ROTATION_YAW_315: int
MAV_SENSOR_ROTATION_ROLL_180: int
MAV_SENSOR_ROTATION_ROLL_180_YAW_45: int
MAV_SENSOR_ROTATION_ROLL_180_YAW_90: int
MAV_SENSOR_ROTATION_ROLL_180_YAW_135: int
MAV_SENSOR_ROTATION_PITCH_180: int
MAV_SENSOR_ROTATION_ROLL_180_YAW_225: int
MAV_SENSOR_ROTATION_ROLL_180_YAW_270: int
MAV_SENSOR_ROTATION_ROLL_180_YAW_315: int
MAV_SENSOR_ROTATION_ROLL_90: int
MAV_SENSOR_ROTATION_ROLL_90_YAW_45: int
MAV_SENSOR_ROTATION_ROLL_90_YAW_90: int
MAV_SENSOR_ROTATION_ROLL_90_YAW_135: int
MAV_SENSOR_ROTATION_ROLL_270: int
MAV_SENSOR_ROTATION_ROLL_270_YAW_45: int
MAV_SENSOR_ROTATION_ROLL_270_YAW_90: int
MAV_SENSOR_ROTATION_ROLL_270_YAW_135: int
MAV_SENSOR_ROTATION_PITCH_90: int
MAV_SENSOR_ROTATION_PITCH_270: int
MAV_SENSOR_ROTATION_PITCH_180_YAW_90: int
MAV_SENSOR_ROTATION_PITCH_180_YAW_270: int
MAV_SENSOR_ROTATION_ROLL_90_PITCH_90: int
MAV_SENSOR_ROTATION_ROLL_180_PITCH_90: int
MAV_SENSOR_ROTATION_ROLL_270_PITCH_90: int
MAV_SENSOR_ROTATION_ROLL_90_PITCH_180: int
MAV_SENSOR_ROTATION_ROLL_270_PITCH_180: int
MAV_SENSOR_ROTATION_ROLL_90_PITCH_270: int
MAV_SENSOR_ROTATION_ROLL_180_PITCH_270: int
MAV_SENSOR_ROTATION_ROLL_270_PITCH_270: int
MAV_SENSOR_ROTATION_ROLL_90_PITCH_180_YAW_90: int
MAV_SENSOR_ROTATION_ROLL_90_YAW_270: int
MAV_SENSOR_ROTATION_ROLL_315_PITCH_315_YAW_315: int
MAV_SENSOR_ORIENTATION_ENUM_END: int
MAV_PROTOCOL_CAPABILITY_MISSION_FLOAT: int
MAV_PROTOCOL_CAPABILITY_PARAM_FLOAT: int
MAV_PROTOCOL_CAPABILITY_MISSION_INT: int
MAV_PROTOCOL_CAPABILITY_COMMAND_INT: int
MAV_PROTOCOL_CAPABILITY_PARAM_UNION: int
MAV_PROTOCOL_CAPABILITY_FTP: int
MAV_PROTOCOL_CAPABILITY_SET_ATTITUDE_TARGET: int
MAV_PROTOCOL_CAPABILITY_SET_POSITION_TARGET_LOCAL_NED: int
MAV_PROTOCOL_CAPABILITY_SET_POSITION_TARGET_GLOBAL_INT: int
MAV_PROTOCOL_CAPABILITY_TERRAIN: int
MAV_PROTOCOL_CAPABILITY_SET_ACTUATOR_TARGET: int
MAV_PROTOCOL_CAPABILITY_FLIGHT_TERMINATION: int
MAV_PROTOCOL_CAPABILITY_COMPASS_CALIBRATION: int
MAV_PROTOCOL_CAPABILITY_ENUM_END: int
MAV_ESTIMATOR_TYPE_NAIVE: int
MAV_ESTIMATOR_TYPE_VISION: int
MAV_ESTIMATOR_TYPE_VIO: int
MAV_ESTIMATOR_TYPE_GPS: int
MAV_ESTIMATOR_TYPE_GPS_INS: int
MAV_ESTIMATOR_TYPE_ENUM_END: int
MAV_BATTERY_TYPE_UNKNOWN: int
MAV_BATTERY_TYPE_LIPO: int
MAV_BATTERY_TYPE_LIFE: int
MAV_BATTERY_TYPE_LION: int
MAV_BATTERY_TYPE_NIMH: int
MAV_BATTERY_TYPE_ENUM_END: int
MAV_BATTERY_FUNCTION_UNKNOWN: int
MAV_BATTERY_FUNCTION_ALL: int
MAV_BATTERY_FUNCTION_PROPULSION: int
MAV_BATTERY_FUNCTION_AVIONICS: int
MAV_BATTERY_TYPE_PAYLOAD: int
MAV_BATTERY_FUNCTION_ENUM_END: int
MAV_VTOL_STATE_UNDEFINED: int
MAV_VTOL_STATE_TRANSITION_TO_FW: int
MAV_VTOL_STATE_TRANSITION_TO_MC: int
MAV_VTOL_STATE_MC: int
MAV_VTOL_STATE_FW: int
MAV_VTOL_STATE_ENUM_END: int
MAV_LANDED_STATE_UNDEFINED: int
MAV_LANDED_STATE_ON_GROUND: int
MAV_LANDED_STATE_IN_AIR: int
MAV_LANDED_STATE_ENUM_END: int
ADSB_ALTITUDE_TYPE_PRESSURE_QNH: int
ADSB_ALTITUDE_TYPE_GEOMETRIC: int
ADSB_ALTITUDE_TYPE_ENUM_END: int
ADSB_EMITTER_TYPE_NO_INFO: int
ADSB_EMITTER_TYPE_LIGHT: int
ADSB_EMITTER_TYPE_SMALL: int
ADSB_EMITTER_TYPE_LARGE: int
ADSB_EMITTER_TYPE_HIGH_VORTEX_LARGE: int
ADSB_EMITTER_TYPE_HEAVY: int
ADSB_EMITTER_TYPE_HIGHLY_MANUV: int
ADSB_EMITTER_TYPE_ROTOCRAFT: int
ADSB_EMITTER_TYPE_UNASSIGNED: int
ADSB_EMITTER_TYPE_GLIDER: int
ADSB_EMITTER_TYPE_LIGHTER_AIR: int
ADSB_EMITTER_TYPE_PARACHUTE: int
ADSB_EMITTER_TYPE_ULTRA_LIGHT: int
ADSB_EMITTER_TYPE_UNASSIGNED2: int
ADSB_EMITTER_TYPE_UAV: int
ADSB_EMITTER_TYPE_SPACE: int
ADSB_EMITTER_TYPE_UNASSGINED3: int
ADSB_EMITTER_TYPE_EMERGENCY_SURFACE: int
ADSB_EMITTER_TYPE_SERVICE_SURFACE: int
ADSB_EMITTER_TYPE_POINT_OBSTACLE: int
ADSB_EMITTER_TYPE_ENUM_END: int
ADSB_FLAGS_VALID_COORDS: int
ADSB_FLAGS_VALID_ALTITUDE: int
ADSB_FLAGS_VALID_HEADING: int
ADSB_FLAGS_VALID_VELOCITY: int
ADSB_FLAGS_VALID_CALLSIGN: int
ADSB_FLAGS_VALID_SQUAWK: int
ADSB_FLAGS_SIMULATED: int
ADSB_FLAGS_ENUM_END: int
MAVLINK_MSG_ID_BAD_DATA: int
MAVLINK_MSG_ID_HEARTBEAT: int
MAVLINK_MSG_ID_GLOBAL_POSITION_INT: int
MAVLINK_MSG_ID_SCALED_SVS: int
MAVLINK_MSG_ID_CHAMBER_STATUS: int
MAVLINK_MSG_ID_SYSTEM_STATUS_2: int
MAVLINK_MSG_ID_PINGER_DATA: int

class MAVLink_heartbeat_message(MAVLink_message):
    id: int
    name: str
    fieldnames: List[str]
    ordered_fieldnames: List[str]
    fieldtypes: List[str]
    fielddisplays_by_name: dict
    fieldenums_by_name: dict
    fieldunits_by_name: dict
    format: str
    native_format: bytearray
    orders: List[int]
    lengths: List[int]
    array_lengths: List[int]
    crc_extra: int
    unpacker: struct.Struct
    instance_field: Any
    instance_offset: int
    type: int
    autopilot: int
    base_mode: int
    custom_mode: int
    system_status: int
    mavlink_version: int
    def __init__(self, type: int, autopilot: int, base_mode: int, custom_mode: int, system_status: int,
                 mavlink_version: int) -> None: ...
    def pack(self, mav: MAVLink, force_mavlink1: bool = ...) -> MutableSequence[int]: ...

class MAVLink_global_position_int_message(MAVLink_message):
    id: int
    name: str
    fieldnames: List[str]
    ordered_fieldnames: List[str]
    fieldtypes: List[str]
    fielddisplays_by_name: dict
    fieldenums_by_name: dict
    fieldunits_by_name: dict
    format: str
    native_format: bytearray
    orders: List[int]
    lengths: List[int]
    array_lengths: List[int]
    crc_extra: int
    unpacker: struct.Struct
    instance_field: Any
    instance_offset: int
    time_boot_ms: int
    lat: int
    lon: int
    alt: float
    relative_alt: float
    bottom_clearnce: float
    depth: float
    vx: float
    vy: float
    vz: float
    hdg: float
    def __init__(self, time_boot_ms: int, lat: int, lon: int, alt: float, relative_alt: float, bottom_clearnce: float,
                 depth: float, vx: float, vy: float, vz: float, hdg: float) -> None: ...
    def pack(self, mav: MAVLink, force_mavlink1: bool = ...) -> MutableSequence[int]: ...

class MAVLink_scaled_svs_message(MAVLink_message):
    id: int
    name: str
    fieldnames: List[str]
    ordered_fieldnames: List[str]
    fieldtypes: List[str]
    fielddisplays_by_name: dict
    fieldenums_by_name: dict
    fieldunits_by_name: dict
    format: str
    native_format: bytearray
    orders: List[int]
    lengths: List[int]
    array_lengths: List[int]
    crc_extra: int
    unpacker: struct.Struct
    instance_field: Any
    instance_offset: int
    time_boot_ms: int
    Speed_of_Sound: float
    Depth: float
    Temperature: int
    Status: int
    Reserved: float
    def __init__(self, time_boot_ms, Speed_of_Sound, Depth, Temperature, Status, Reserved) -> None: ...
    def pack(self, mav: MAVLink, force_mavlink1: bool = ...) -> MutableSequence[int]: ...

class MAVLink_chamber_status_message(MAVLink_message):
    id: int
    name: str
    fieldnames: List[str]
    ordered_fieldnames: List[str]
    fieldtypes: List[str]
    fielddisplays_by_name: dict
    fieldenums_by_name: dict
    fieldunits_by_name: dict
    format: str
    native_format: bytearray
    orders: List[int]
    lengths: List[int]
    array_lengths: List[int]
    crc_extra: int
    unpacker: struct.Struct
    instance_field: Any
    instance_offset: int
    time_boot_ms: int
    chamber_num: int
    pressure: int
    temperature: int
    humidity: int
    def __init__(self, time_boot_ms: int, chamber_num: int, pressure: int, temperature: int, humidity: int) -> None: ...
    def pack(self, mav: MAVLink, force_mavlink1: bool = ...) -> MutableSequence[int]: ...

class MAVLink_system_status_2_message(MAVLink_message):
    id: int
    name: str
    fieldnames: List[str]
    ordered_fieldnames: List[str]
    fieldtypes: List[str]
    fielddisplays_by_name: dict
    fieldenums_by_name: dict
    fieldunits_by_name: dict
    format: str
    native_format: bytearray
    orders: List[int]
    lengths: List[int]
    array_lengths: List[int]
    crc_extra: int
    unpacker: struct.Struct
    instance_field: Any
    instance_offset: int
    time_boot_ms: int
    hc_mode: int
    hc_system_status: int
    hc_err_id: int
    debug1: float
    debug2: float
    def __init__(self, time_boot_ms: int, hc_mode: int, hc_system_status: int, hc_err_id: int, debug1: float,
                 debug2:float) -> None: ...
    def pack(self, mav: MAVLink, force_mavlink1: bool = ...) -> MutableSequence[int]: ...

class MAVLink_pinger_data_message(MAVLink_message):
    id: int
    name: str
    fieldnames: List[str]
    ordered_fieldnames: List[str]
    fieldtypes: List[str]
    fielddisplays_by_name: dict
    fieldenums_by_name: dict
    fieldunits_by_name: dict
    format: str
    native_format: bytearray
    orders: List[int]
    lengths: List[int]
    array_lengths: List[int]
    crc_extra: int
    unpacker: struct.Struct
    instance_field: Any
    instance_offset: int
    time_boot_ms: int
    range: float
    azimuth: float
    def __init__(self, time_boot_ms:int, range: float, azimuth: float) -> None: ...
    def pack(self, mav: MAVLink, force_mavlink1: bool = ...) -> MutableSequence[int]: ...

mavlink_map: dict[int, type]

class MAVError(Exception):
    message: str
    def __init__(self, msg:str) -> None: ...

class MAVString(str):
    def __init__(self, s) -> None: ...

class MAVLink_bad_data(MAVLink_message):
    data: MutableSequence[int]
    reason: str
    def __init__(self, data: MutableSequence[int], reason: str) -> None: ...

class MAVLinkSigning:
    secret_key: Any
    timestamp: int
    link_id: int
    sign_outgoing: bool
    allow_unsigned_callback: Any
    stream_timestamps: Any
    sig_count: int
    badsig_count: int
    goodsig_count: int
    unsigned_count: int
    reject_count: int
    def __init__(self) -> None: ...

class MAVLink:
    seq: int
    file: BinaryIO
    srcSystem: int
    srcComponent: int
    callback: Callable
    callback_args: Any
    callback_kwargs: Any
    send_callback: Callable
    send_callback_args: Any
    send_callback_kwargs: Any
    buf: bytearray
    buf_index: int
    expected_length: int
    have_prefix_error: bool
    robust_parsing: bool
    protocol_marker: int
    little_endian: bool
    crc_extra: bool
    sort_fields: bool
    total_packets_sent: int
    total_bytes_sent: int
    total_packets_received: int
    total_bytes_received: int
    total_receive_errors: int
    startup_time: float
    signing: MAVLinkSigning
    native: Any
    test_buf: bytearray
    mav20_unpacker: struct.Struct
    mav10_unpacker: struct.Struct
    mav20_h3_unpacker: struct.Struct
    mav_csum_unpacker: struct.Struct
    mav_sign_unpacker: struct.Struct
    def __init__(self, file: BinaryIO, srcSystem: int = ..., srcComponent: int = ..., use_native: bool = ...
                 ) -> None: ...
    def set_callback(self, callback: Callable, *args: Any, **kwargs: Any) -> None: ...
    def set_send_callback(self, callback: Callable, *args:Any, **kwargs: Any) -> None: ...
    def send(self, mavmsg: MAVLink_message, force_mavlink1: bool = ...) -> None: ...
    def buf_len(self) -> int: ...
    def bytes_needed(self) -> int: ...
    def parse_char(self, c) -> Any: ...
    def parse_buffer(self, s: Sequence[int]) -> Any: ...
    def check_signature(self, msgbuf: Any, srcSystem: int, srcComponent: int) -> bool: ...
    def decode(self, msgbuf: array.array ) -> MAVLink_message: ...
    def heartbeat_encode(self, type, autopilot, base_mode, custom_mode, system_status, mavlink_version: int = ...): ...
    def heartbeat_send(self, type, autopilot, base_mode, custom_mode, system_status, mavlink_version: int = ..., force_mavlink1: bool = ...): ...
    def global_position_int_encode(self, time_boot_ms, lat, lon, alt, relative_alt, bottom_clearnce, depth, vx, vy, vz, hdg): ...
    def global_position_int_send(self, time_boot_ms, lat, lon, alt, relative_alt, bottom_clearnce, depth, vx, vy, vz, hdg, force_mavlink1: bool = ...): ...
    def scaled_svs_encode(self, time_boot_ms, Speed_of_Sound, Depth, Temperature, Status, Reserved): ...
    def scaled_svs_send(self, time_boot_ms, Speed_of_Sound, Depth, Temperature, Status, Reserved, force_mavlink1: bool = ...): ...
    def chamber_status_encode(self, time_boot_ms, chamber_num, pressure, temperature, humidity): ...
    def chamber_status_send(self, time_boot_ms, chamber_num, pressure, temperature, humidity, force_mavlink1: bool = ...): ...
    def system_status_2_encode(self, time_boot_ms, hc_mode, hc_system_status, hc_err_id, debug1, debug2): ...
    def system_status_2_send(self, time_boot_ms, hc_mode, hc_system_status, hc_err_id, debug1, debug2, force_mavlink1: bool = ...): ...
    def pinger_data_encode(self, time_boot_ms, range, azimuth): ...
    def pinger_data_send(self, time_boot_ms, range, azimuth, force_mavlink1: bool = ...): ...
