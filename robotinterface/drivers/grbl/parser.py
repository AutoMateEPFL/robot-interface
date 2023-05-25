import logging
from robotinterface.drivers.grbl import constants

log = logging.getLogger(__name__)

def handle_error_alarm(answer: str) -> str:
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
    handle_error_alarm(answer)
    if not constants.WELCOME_MSG == answer:
        raise ValueError
    logging.debug(f"Sucessfully connected to GRBL controller")
    return

def homing_start_parser(answer: str) -> None:
    handle_error_alarm(answer)
    if "Home" not in answer:
        raise ValueError
    logging.debug("homing has sucessfuly started")
    return

def homing_end_parser(ack_homing_1: str, ack_homing_2: str) -> None:
    handle_error_alarm(ack_homing_1)
    handle_error_alarm(ack_homing_2)
    if "[MSG:]" not in ack_homing_1 or "ok" not in ack_homing_2:
        raise ValueError
    logging.debug("homing has sucessfuly ended")
    return

def idle_parser(answer: str) -> bool:
    handle_error_alarm(answer)
    if "Idle" in answer:
        return True
    else:
        return False

def move_parser(answer: str) -> None:
    handle_error_alarm(answer)
    if answer != "ok":
        raise ValueError
    logging.debug("Gcode read sucessfully")
    return
