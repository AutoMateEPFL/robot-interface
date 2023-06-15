import dynamixel_sdk as dsdk
import asyncio
from functools import partial
from robotinterface.drivers.dynamixel.address_book import *
from concurrent.futures import ThreadPoolExecutor

import logging

log = logging.getLogger(__name__)


class Dynamixel:
    def __init__(self, id, port_name, baudrate, series_name="xm"):
        # Communication inputs
        if type(id) == list:
            self.multiple_motors = True
        else:
            self.multiple_motors = False

        self.id = id
        self.port_name = port_name
        self.baudrate = baudrate

        self.executor = ThreadPoolExecutor(max_workers=2)
        self.loop = asyncio.get_event_loop()

        # Set series name
        if type(self.id) == list:
            if type(series_name) == list and len(series_name) == len(self.id):
                self.series_name = {}
                for i in range(len(self.id)):
                    self.series_name[self.id[i]] = series_name[i]
            else:
                raise ValueError("Provide correct series name type / length")

        else:
            if type(series_name) == str:
                self.series_name = {self.id: series_name}
            else:
                raise ValueError("Provide correct series name type")

        for id, series in self.series_name.items():
            # Check for series name
            all_series_names = ["xm", "xl"]
            if series not in all_series_names:
                print("Series name invalid for motor with id,", id, "Choose one of:", all_series_names)

        # Communication settings
        self.port_handler = dsdk.PortHandler(self.port_name)
        self.packet_handler = dsdk.PacketHandler(2)

        self.port_handler.openPort()
        logging.debug(f"Port open successfully for Dynamixel controller")

        # Set port baudrate
        self.port_handler.setBaudRate(self.baudrate)
        logging.debug(f"Baudrate set successfully for Dynamixel controller")

    def fetch_and_check_id(self, id):
        if self.multiple_motors:
            match id:
                case None:
                    raise ValueError(
                        "You specified multiple dynamixels on this port. But did not specify which motor to operate "
                        "upon. Please specify id.")
                case "all":
                    return self.id
                case _ if isinstance(id, list):
                    for id in id:
                        if id not in self.id:
                            raise ValueError(
                                f"The id you specified: {id} in the list {id} does not exist in the list of IDs you "
                                f"initialized.")
                    return id
                case _:
                    if id in self.id:
                        return [id]
                    else:
                        raise ValueError(
                            f"The id you specified: {id} does not exist in the list of IDs you initialized.")
        else:
            return [self.id]

    def _print_error_msg(self, process_name, dxl_comm_result, dxl_error, selected_ids):
        if dxl_comm_result != dsdk.COMM_SUCCESS:
            logging.error("!!", process_name, "failed for: Dynamixel Controller")
            logging.error("Communication error:", self.packet_handler.getTxRxResult(dxl_comm_result))
            raise ValueError(f"!! {process_name} failed for: Dynamixel Controller")

        elif dxl_error != 0:
            logging.error("!!", process_name, "failed for: Dynamixel Controller")
            logging.error(f"Dynamixel error: {self.packet_handler.getRxPacketError(dxl_error)}")
            raise ValueError(f"!! {process_name} failed for: Dynamixel Controller")

        else:
            logging.debug(f"{process_name} successful for: Dynamixel Controller id: {selected_ids}")

    async def toggle_torque(self, enable, process_name, id=None):
        selected_ids = self.fetch_and_check_id(id)
        for selected_ID in selected_ids:
            dxl_comm_result, dxl_error = await self._write1ByteTxRx(self.port_handler, selected_ID,
                                                                    ADDR_TORQUE_ENABLE, int(enable))
            self._print_error_msg(process_name, dxl_comm_result, dxl_error, selected_ID)

    async def enable_torque(self, id=None):
        await self.toggle_torque(True, "Torque enable", id)

    async def disable_torque(self, id=None):
        await self.toggle_torque(False, "Torque disable", id)

    async def is_torque_on(self, id=None):
        selected_ids = self.fetch_and_check_id(id)
        for selected_ID in selected_ids:
            torque_status, dxl_comm_result, dxl_error = await self._read1ByteTxRx(self.port_handler,
                                                                                  selected_ID,
                                                                                  ADDR_TORQUE_ENABLE)
            self._print_error_msg("Read torque status", dxl_comm_result, dxl_error, selected_ID)

            if torque_status == False:
                return False

        return True

    async def ping(self, id=None):
        selected_ids = self.fetch_and_check_id(id)
        for selected_ID in selected_ids:
            _, dxl_comm_result, dxl_error = await self._ping(self.port_handler, selected_ID)
            self._print_error_msg("Ping", dxl_comm_result, dxl_error, selected_ID)

    async def set_operating_mode(self, mode, id=None):
        selected_ids = self.fetch_and_check_id(id)
        for selected_ID in selected_ids:

            series = self.series_name[selected_ID]
            if series == "xm":
                operating_modes = operating_modes_xm
            elif series == "xl":
                operating_modes = operating_modes_xl

            if mode in operating_modes:
                # Check if torque was enabled
                was_torque_on = False
                if await self.is_torque_on(id=selected_ID):
                    was_torque_on = True
                    await self.disable_torque(id=selected_ID)

                mode_id = operating_modes[mode]
                dxl_comm_result, dxl_error = await self._write1ByteTxRx(self.port_handler, selected_ID,
                                                                        ADDR_OPERATING_MODE, mode_id)
                self._print_error_msg("Mode set to " + mode + " control", dxl_comm_result, dxl_error, selected_ID)

                if was_torque_on:
                    await self.enable_torque(id=selected_ID)
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

    async def read_data(self, method, address, twos_complement_key, id=None):
        selected_ids = self.fetch_and_check_id(id)
        reading = []
        for selected_ID in selected_ids:
            data, dxl_comm_result, dxl_error = await method(self.port_handler, selected_ID, address)
            self._print_error_msg(f"Read {twos_complement_key}", dxl_comm_result, dxl_error, selected_ID)
            reading.append(self.compensate_twos_complement(data, twos_complement_key))

        if len(selected_ids) == 1:
            return reading[0]
        else:
            return reading

    async def read_position(self, id=None):
        return await self.read_data(self._read4ByteTxRx, ADDR_PRESENT_POSITION, "position", id)

    async def read_velocity(self, id=None):
        return await self.read_data(self._read4ByteTxRx, ADDR_PRESENT_VELOCITY, "velocity", id)

    async def read_current(self, id=None):
        return await self.read_data(self._read2ByteTxRx, ADDR_PRESENT_CURRENT, "current", id)

    async def read_pwm(self, id=None):
        return await self.read_data(self._read2ByteTxRx, ADDR_PRESENT_PWM, "pwm", id)

    def read_from_address(self, number_of_bytes, ADDR, id=None):
        method = None
        twos_complement_key = ""
        if number_of_bytes == 1:
            method = self._write1ByteTxRx
            twos_complement_key = "1 byte"
        elif number_of_bytes == 2:
            method = self._write2ByteTxRx
            twos_complement_key = "2 bytes"
        else:
            method = self._write4ByteTxRx
            twos_complement_key = "4 bytes"
        return self.read_data(method, ADDR, twos_complement_key, id)

    async def write_data(self, method, address, data, log_key, id=None):
        selected_ids = self.fetch_and_check_id(id)
        for selected_ID in selected_ids:
            dxl_comm_result, dxl_error = await method(self.port_handler, selected_ID, address, int(data))
            self._print_error_msg(f"Write {log_key}", dxl_comm_result, dxl_error, selected_ID)

    async def write_position(self, pos, id=None):
        await self.write_data(self._write4ByteTxRx, ADDR_GOAL_POSITION, pos, "position", id)

    async def write_velocity(self, vel, id=None):
        await self.write_data(self._write4ByteTxRx, ADDR_GOAL_VELOCITY, vel, "velocity", id)

    async def write_current(self, current, id=None):
        await self.write_data(self._write2ByteTxRx, ADDR_GOAL_CURRENT, current, "current", id)

    async def write_pwm(self, pwm, id=None):
        await self.write_data(self._write2ByteTxRx, ADDR_GOAL_PWM, pwm, "pwm", id)

    async def write_profile_velocity(self, profile_vel, id=None):
        await self.write_data(self._write4ByteTxRx, ADDR_PROFILE_VELOCITY, profile_vel, "profile velocity", id)

    async def write_profile_acceleration(self, profile_acc, id=None):
        await self.write_data(self._write4ByteTxRx, ADDR_PROFILE_ACCELERATION, profile_acc,
                              "profile acceleration", id)

    def write_to_address(self, value, number_of_bytes, ADDR, id=None):
        method = None
        if number_of_bytes == 1:
            method = self._write1ByteTxRx
        elif number_of_bytes == 2:
            method = self._write2ByteTxRx
        else:
            method = self._write4ByteTxRx
        self.write_data(method, ADDR, value, "to address", id)

    async def _write4ByteTxRx(self, port_handler, selected_ID, address, data):
        return await self.loop.run_in_executor(self.executor,
                                               partial(self.packet_handler.write4ByteTxRx, port_handler, selected_ID,
                                                       address, data))

    async def _write2ByteTxRx(self, port_handler, selected_ID, address, data):
        return await self.loop.run_in_executor(self.executor,
                                               partial(self.packet_handler.write2ByteTxRx, port_handler, selected_ID,
                                                       address, data))

    async def _write1ByteTxRx(self, port_handler, selected_ID, address, data):
        return await self.loop.run_in_executor(self.executor,
                                               partial(self.packet_handler.write1ByteTxRx, port_handler, selected_ID,
                                                       address, data))

    async def _read4ByteTxRx(self, port_handler, selected_ID, address):
        return await self.loop.run_in_executor(self.executor,
                                               partial(self.packet_handler.read4ByteTxRx, port_handler, selected_ID,
                                                       address))

    async def _read2ByteTxRx(self, port_handler, selected_ID, address):
        return await self.loop.run_in_executor(self.executor,
                                               partial(self.packet_handler.read2ByteTxRx, port_handler, selected_ID,
                                                       address))

    async def _read1ByteTxRx(self, port_handler, selected_ID, address):
        return await self.loop.run_in_executor(self.executor,
                                               partial(self.packet_handler.read1ByteTxRx, port_handler, selected_ID,
                                                       address))

    async def _ping(self, port_handler, selected_ID):
        return await self.loop.run_in_executor(self.executor,
                                               partial(self.packet_handler.ping, port_handler, selected_ID))
