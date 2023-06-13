def fetch_and_check_ID(self, ID):
    if self.multiple_motors:
        if ID is None:
            print(
                "You specified multiple dynamixels on this port. But did not specify which motor to operate upon. Please specify ID.")
            sys.exit()
        elif ID == "all":
            return self.ID
        elif type(ID) == list:
            for id in ID:
                if id not in self.ID:
                    print("The ID you specified:", id, "in the list", ID,
                          "does not exist in the list of IDs you initialized.")
                    sys.exit()
            return ID
        else:
            if ID in self.ID:
                return [ID]
            else:
                print("The ID you specified:", ID, "does not exist in the list of IDs you initialized.")
                sys.exit()
    else:
        return [self.ID]

def _print_error_msg(self, process_name, dxl_comm_result, dxl_error, selected_ID, print_only_if_error=False):
    if dxl_comm_result != COMM_SUCCESS:
        print("!!", process_name, "failed for:", self.descriptive_device_name)
        print("Communication error:", self.packet_handler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("!!", process_name, "failed for:", self.descriptive_device_name)
        print("Dynamixel error:", self.packet_handler.getRxPacketError(dxl_error))
    else:
        if not print_only_if_error:
            print(process_name, "successful for:", self.descriptive_device_name, "ID:", selected_ID)


def _print_error_msg(self, process_name, dxl_comm_result, dxl_error, selected_ID, print_only_if_error=False):
    if dxl_comm_result != COMM_SUCCESS:
        print("!!", process_name, "failed for:", self.descriptive_device_name)
        print("Communication error:", self.packet_handler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("!!", process_name, "failed for:", self.descriptive_device_name)
        print("Dynamixel error:", self.packet_handler.getRxPacketError(dxl_error))
    else:
        if not print_only_if_error:
            print(process_name, "successful for:", self.descriptive_device_name, "ID:", selected_ID)

def _print_error_msg_multiple(self, process_name, dxl_comm_result, dxl_error, selected_IDs):
    if dxl_comm_result != COMM_SUCCESS:
        logging.error("!!", process_name, "failed for:", self.descriptive_device_name)
        logging.error("Communication error:", self.packet_handler.getTxRxResult(dxl_comm_result))
        raise ValueError(f"!! {process_name} failed for: {self.descriptive_device_name}")

    elif dxl_error != 0:
        print("!!", process_name, "failed for:", self.descriptive_device_name)
        print("Dynamixel error:", self.packet_handler.getRxPacketError(dxl_error))

    else:
        logging.debug("{process_name} successful for: {self.descriptive_device_name} ID: {selected_ID}")