import os
from typing import Any, MutableMapping, Mapping

from config import appname, appversion
import logging

from EDMCOverlay import edmcoverlay

OVERLAY = None
logger = None

PLUGIN_VERSION = "0.1.0"
PLUGIN_DIRECTORY = os.path.abspath(os.path.dirname(__file__))


# This could also be returned from plugin_start3()
plugin_name = os.path.basename(os.path.dirname(__file__))

# A Logger is used per 'found' plugin to make it easy to include the plugin's
# folder name in the logging output format.
# NB: plugin_name here *must* be the plugin's folder name as per the preceding
#     code, else the logger won't be properly set up.
logger = logging.getLogger(f"{appname}.{plugin_name}")

# If the Logger has handlers then it was already set up by the core code, else
# it needs setting up here.
if not logger.hasHandlers():
    level = logging.INFO  # So logger.info(...) is equivalent to print()

    logger.setLevel(level)
    logger_channel = logging.StreamHandler()
    logger_formatter = logging.Formatter(
        f"%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d:%(funcName)s: %(message)s"
    )
    logger_formatter.default_time_format = "%Y-%m-%d %H:%M:%S"
    logger_formatter.default_msec_format = "%s.%03d"
    logger_channel.setFormatter(logger_formatter)
    logger.addHandler(logger_channel)


def plugin_start3(plugin_dir: str) -> str:
    """
    Load this plugin into EDMC
    """
    global OVERLAY
    OVERLAY = edmcoverlay.Overlay()
    read_route()
    return f"Copilot v{PLUGIN_VERSION}"


def journal_entry(
    cmdr: str,
    is_beta: bool,
    system: str,
    station: str,
    entry: MutableMapping[str, Any],
    state: Mapping[str, Any],
) -> None:
    if entry["event"] == "StartJump" and entry["JumpType"] == "Hyperspace":
        OVERLAY.send_message(
            "Copilot",
            f"Jumping to {entry['StarSystem']}",
            "#aaf9ff",
            x=520,
            y=120,
            ttl=3,
            size="large",
        )
    if entry["event"] == "FSDJump":
        OVERLAY.send_message(
            "Copilot",
            f"Arrived at {entry['StarSystem']}",
            "#aaf9ff",
            x=520,
            y=120,
            ttl=3,
            size="large",
        )


def read_route():
    with open(os.path.join(PLUGIN_DIRECTORY, "route.csv"), "r") as f:
        for line in f.readlines():
            logger.info(line)
