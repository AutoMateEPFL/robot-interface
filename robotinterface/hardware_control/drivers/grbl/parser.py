import logging
from robotinterface.hardware_control.drivers.grbl import constants

log = logging.getLogger(__name__)

def handle_error_alarm(answer: str) -> str:
    """
    Handles error or alarm messages returned by the GRBL controller.

    Args:
        answer (str): The answer received from the GRBL controller.

    Returns:
        str: The answer if there is no error or alarm

    Raises:
        ValueError: If the answer starts with "ALARM:" or "error:"
    """
    if answer.startswith("ALARM:"):
        answer = answer.replace("ALARM:", "")
        code = int(answer)
        raise ValueError(f"Alarm: {constants.grblalarm[code]}")
    elif answer.startswith("error:"):
        answer = answer.replace("error:", "")
        code = int(answer)
        raise ValueError(f"error: {constants.grblerror[code]}")
    else:
        return answer

def welcome_parser(answer: str) -> None:
    """
    Parses the welcome message received from the GRBL controller.

    Args:
        answer (str): The answer received from the GRBL controller.

    Raises:
        ValueError: If the answer does not match the expected welcome message.
    """
    handle_error_alarm(answer)
    if not constants.WELCOME_MSG == answer:
        raise ValueError(f"Message received: {answer}")
    logging.debug(f"Successfully connected to GRBL controller")

def homing_start_parser(answer: str) -> None:
    """
    Parses the homing start message received from the GRBL controller.

    Args:
        answer (str): The answer received from the GRBL controller.

    Raises:
        ValueError: If the answer does not contain the expected homing start message.
    """
    handle_error_alarm(answer)
    if "Home" not in answer:
        raise ValueError
    logging.debug("Homing has successfully started")

def homing_end_parser(ack_homing_1: str, ack_homing_2: str) -> None:
    """
    Parses the homing end acknowledgment messages received from the GRBL controller.

    Args:
        ack_homing_1 (str): The first acknowledgment message received from the GRBL controller.
        ack_homing_2 (str): The second acknowledgment message received from the GRBL controller.

    Raises:
        ValueError: If either of the acknowledgment messages does not match the expected format.
    """
    handle_error_alarm(ack_homing_1)
    handle_error_alarm(ack_homing_2)
    if "[MSG:]" not in ack_homing_1 or "ok" not in ack_homing_2:
        raise ValueError
    logging.debug("Homing has successfully ended")

def idle_parser(answer: str) -> bool:
    """
    Parses the idle message received from the GRBL controller.

    Args:
        answer (str): The answer received from the GRBL controller.

    Returns:
        bool: True if the answer contains "Idle", indicating an idle state, False otherwise.
    """
    handle_error_alarm(answer)
    if "Idle" in answer:
        return True
    else:
        return False

def move_parser(answer: str) -> None:
    """
    Parses the move acknowledgment message received from the GRBL controller.

    Args:
        answer (str): The answer received from the GRBL controller.

    Raises:
        ValueError: If the answer does not match the expected "ok" message.
    """
    handle_error_alarm(answer)
    if answer != "ok":
        raise ValueError
    logging.debug("Gcode read successfully")
