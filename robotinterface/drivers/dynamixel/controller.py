from dynamixel_sdk import *
from robotinterface.drivers.dynamixel.address_book import *

import logging

log = logging.getLogger(__name__)


class Dynamixel:
    def __init__(self, ID, descriptive_device_name, port_name, baudrate, series_name="xm"):
        # Communication inputs
        if type(ID) == list:
            self.multiple_motors = True
        else:
            self.multiple_motors = False

        self.ID = ID
        self.descriptive_device_name = descriptive_device_name
        self.port_name = port_name
        self.baudrate = baudrate

        # Set series name
        if type(self.ID) == list:
            if type(series_name) == list and len(series_name) == len(self.ID):
                self.series_name = {}
                for i in range(len(self.ID)):
                    self.series_name[self.ID[i]] = series_name[i]
            else:
                raise ValueError("Provide correct series name type / length")


        else:
            if type(series_name) == str:
                self.series_name = {self.ID: series_name}
            else:
                raise ValueError("Provide correct series name type")

        for id, series in self.series_name.items():
            # Check for series name
            all_series_names = ["xm", "xl"]
            if series not in all_series_names:
                print("Series name invalid for motor with ID,", id, "Choose one of:", all_series_names)
                sys.exit()

        # Communication settings
        self.port_handler = PortHandler(self.port_name)
        self.packet_handler = PacketHandler(2)

        self.port_handler.openPort()
        logging.debug(f"Port open successfully for: {self.descriptive_device_name}")

        # Set port baudrate
        self.port_handler.setBaudRate(self.baudrate)
        logging.debug(f"Baudrate set successfully for: {self.descriptive_device_name}")

    def fetch_and_check_ID(self, ID):
        if self.multiple_motors:
            match ID:
                case None:
                    raise ValueError(
                        "You specified multiple dynamixels on this port. But did not specify which motor to operate "
                        "upon. Please specify ID.")
                case "all":
                    return self.ID
                case _ if isinstance(ID, list):
                    for id in ID:
                        if id not in self.ID:
                            raise ValueError(
                                f"The ID you specified: {id} in the list {ID} does not exist in the list of IDs you "
                                f"initialized.")
                    return ID
                case _:
                    if ID in self.ID:
                        return [ID]
                    else:
                        raise ValueError(
                            f"The ID you specified: {ID} does not exist in the list of IDs you initialized.")
        else:
            return [self.ID]

    def _print_error_msg(self, process_name, dxl_comm_result, dxl_error, selected_IDs):
        if dxl_comm_result != COMM_SUCCESS:
            logging.error("!!", process_name, "failed for:", self.descriptive_device_name)
            logging.error("Communication error:", self.packet_handler.getTxRxResult(dxl_comm_result))
            raise ValueError(f"!! {process_name} failed for: {self.descriptive_device_name}")

        elif dxl_error != 0:
            logging.error("!!", process_name, "failed for:", self.descriptive_device_name)
            logging.error(f"Dynamixel error: {self.packet_handler.getRxPacketError(dxl_error)}")
            raise ValueError(f"!! {process_name} failed for: {self.descriptive_device_name}")

        else:
            logging.debug(f"{process_name} successful for: {self.descriptive_device_name} ID: {selected_IDs}")

    def toggle_torque(self, enable, process_name, print_only_if_error=False, ID=None):
        selected_IDs = self.fetch_and_check_ID(ID)
        for selected_ID in selected_IDs:
            dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(self.port_handler, selected_ID,
                                                                            ADDR_TORQUE_ENABLE, int(enable))
            self._print_error_msg(process_name, dxl_comm_result, dxl_error, selected_ID)

    def enable_torque(self, print_only_if_error=False, ID=None):
        self.toggle_torque(True, "Torque enable", print_only_if_error, ID)

    def disable_torque(self, print_only_if_error=False, ID=None):
        self.toggle_torque(False, "Torque disable", print_only_if_error, ID)

    def is_torque_on(self, print_only_if_error=False, ID=None):
        selected_IDs = self.fetch_and_check_ID(ID)
        for selected_ID in selected_IDs:
            torque_status, dxl_comm_result, dxl_error = self.packet_handler.read1ByteTxRx(self.port_handler,
                                                                                          selected_ID,
                                                                                          ADDR_TORQUE_ENABLE)
            self._print_error_msg("Read torque status", dxl_comm_result, dxl_error, selected_ID)

            if torque_status == False:
                return False

        return True

    def ping(self, ID=None):
        selected_IDs = self.fetch_and_check_ID(ID)
        for selected_ID in selected_IDs:
            _, dxl_comm_result, dxl_error = self.packet_handler.ping(self.port_handler, selected_ID)
            self._print_error_msg("Ping", dxl_comm_result, dxl_error, selected_ID)

    def set_operating_mode(self, mode, ID=None, print_only_if_error=False):
        selected_IDs = self.fetch_and_check_ID(ID)
        for selected_ID in selected_IDs:

            series = self.series_name[selected_ID]
            if series == "xm":
                operating_modes = operating_modes_xm
            elif series == "xl":
                operating_modes = operating_modes_xl

            if mode in operating_modes:
                # Check if torque was enabled
                was_torque_on = False
                if self.is_torque_on(print_only_if_error=True, ID=selected_ID):
                    was_torque_on = True
                    self.disable_torque(print_only_if_error=True, ID=selected_ID)

                mode_id = operating_modes[mode]
                dxl_comm_result, dxl_error = self.packet_handler.write1ByteTxRx(self.port_handler, selected_ID,
                                                                                ADDR_OPERATING_MODE, mode_id)
                self._print_error_msg("Mode set to " + mode + " control", dxl_comm_result, dxl_error, selected_ID)

                if was_torque_on:
                    self.enable_torque(print_only_if_error=True, ID=selected_ID)
            else:
                raise ValueError("Enter valid operating mode. Select one of:\n" + str(list(operating_modes.keys())))

    @staticmethod
    def compensate_twos_complement(value, quantity):
        if quantity in max_register_value:
            max_value = max_register_value[quantity]

            if value < max_value / 2:
                return value
            else:
                return value - max_value
        else:
            raise ValueError("Enter valid operating mode. Select one of:\n" + str(list(max_register_value.keys())))

    def read_data(self, method, address, twos_complement_key, ID=None):
        selected_IDs = self.fetch_and_check_ID(ID)
        reading = []
        for selected_ID in selected_IDs:
            data, dxl_comm_result, dxl_error = method(self.port_handler, selected_ID, address)
            self._print_error_msg(f"Read {twos_complement_key}", dxl_comm_result, dxl_error, selected_ID)
            reading.append(self.compensate_twos_complement(data, twos_complement_key))

        if len(selected_IDs) == 1:
            return reading[0]
        else:
            return reading

    def read_position(self, ID=None):
        return self.read_data(self.packet_handler.read4ByteTxRx, ADDR_PRESENT_POSITION, "position", ID)

    def read_velocity(self, ID=None):
        return self.read_data(self.packet_handler.read4ByteTxRx, ADDR_PRESENT_VELOCITY, "velocity", ID)

    def read_current(self, ID=None):
        return self.read_data(self.packet_handler.read2ByteTxRx, ADDR_PRESENT_CURRENT, "current", ID)

    def read_pwm(self, ID=None):
        return self.read_data(self.packet_handler.read2ByteTxRx, ADDR_PRESENT_PWM, "pwm", ID)

    def read_from_address(self, number_of_bytes, ADDR, ID=None):
        method = None
        twos_complement_key = ""
        if number_of_bytes == 1:
            method = self.packet_handler.read1ByteTxRx
            twos_complement_key = "1 byte"
        elif number_of_bytes == 2:
            method = self.packet_handler.read2ByteTxRx
            twos_complement_key = "2 bytes"
        else:
            method = self.packet_handler.read4ByteTxRx
            twos_complement_key = "4 bytes"
        return self.read_data(method, ADDR, twos_complement_key, ID)

    def write_data(self, method, address, data, log_key, ID=None):
        selected_IDs = self.fetch_and_check_ID(ID)
        for selected_ID in selected_IDs:
            dxl_comm_result, dxl_error = method(self.port_handler, selected_ID, address, int(data))
            self._print_error_msg(f"Write {log_key}", dxl_comm_result, dxl_error, selected_ID)

    def write_position(self, pos, ID=None):
        self.write_data(self.packet_handler.write4ByteTxRx, ADDR_GOAL_POSITION, pos, "position", ID)

    def write_velocity(self, vel, ID=None):
        self.write_data(self.packet_handler.write4ByteTxRx, ADDR_GOAL_VELOCITY, vel, "velocity", ID)

    def write_current(self, current, ID=None):
        self.write_data(self.packet_handler.write2ByteTxRx, ADDR_GOAL_CURRENT, current, "current", ID)

    def write_pwm(self, pwm, ID=None):
        self.write_data(self.packet_handler.write2ByteTxRx, ADDR_GOAL_PWM, pwm, "pwm", ID)

    def write_profile_velocity(self, profile_vel, ID=None):
        self.write_data(self.packet_handler.write4ByteTxRx, ADDR_PROFILE_VELOCITY, profile_vel, "profile velocity", ID)

    def write_profile_acceleration(self, profile_acc, ID=None):
        self.write_data(self.packet_handler.write4ByteTxRx, ADDR_PROFILE_ACCELERATION, profile_acc,
                        "profile acceleration", ID)

    def write_to_address(self, value, number_of_bytes, ADDR, ID=None):
        method = None
        if number_of_bytes == 1:
            method = self.packet_handler.write1ByteTxRx
        elif number_of_bytes == 2:
            method = self.packet_handler.write2ByteTxRx
        else:
            method = self.packet_handler.write4ByteTxRx
        self.write_data(method, ADDR, value, "to address", ID)
