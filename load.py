import os
from typing import Any, MutableMapping, Mapping, Optional
import tkinter as tk

from config import appname, appversion
import logging

from EDMCOverlay import edmcoverlay

route = None
parent_application = None
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
    check_overlay_message()
    global route
    route = read_route()
    return f"Copilot v{PLUGIN_VERSION}"


def plugin_app(parent: tk.Frame) -> Optional[tk.Frame]:
    global parent_application
    global OVERLAY
    parent_application = parent
    frame = tk.Frame(parent)
    button = tk.Button(
        frame,
        text="Test overlay",
        command=check_overlay_message,
    )
    button.grid(row=0)
    route_button = tk.Button(
        frame,
        text="Refresh route",
        command=read_route,
    )
    route_button.grid(row=1)
    return frame


def journal_entry(
    cmdr: str,
    is_beta: bool,
    system: str,
    station: str,
    entry: MutableMapping[str, Any],
    state: Mapping[str, Any],
) -> None:
    if entry["event"] == "StartJump":
        if entry["StarClass"] == "N":
            OVERLAY.send_message(
                "Copilot-neutron-warning",
                f"WARNING Neutron Star ahead",
                "#ff0000",
                x=520,
                y=410,
                ttl=5,
                size="large",
            )
    if entry["event"] in ["FSDJump", "Location"]:
        if entry["StarSystem"] in route["System Name"]:
            current_system_index = route["System Name"].index(entry["StarSystem"])
            logger.info(
                f"Current system is {entry['StarSystem']} (index {current_system_index})."
            )
            if route["Refuel"][current_system_index] == "Yes":
                logger.info(f" Refuel: {route['Refuel'][current_system_index]}")
                OVERLAY.send_message(
                    "Copilot-refuel",
                    f"Refuel now",
                    "#ff9966",
                    x=600,
                    y=410,
                    ttl=20,
                    size="large",
                )
            route_distance = float(route["Distance Remaining"][0])
            distance_remaining = float(
                route["Distance Remaining"][current_system_index]
            )
            next_system = route["System Name"][current_system_index + 1]
            global parent_application
            parent_application.clipboard_clear()
            parent_application.clipboard_append(next_system)
            parent_application.update()
            OVERLAY.send_message(
                "Copilot-next-waypoint",
                f"Next waypoint: {next_system}\n"
                + f"Distance remaining: {distance_remaining:.2f}ly\n"
                + f"Progress: {(1-distance_remaining/route_distance)*100:.2f}%",
                "#aaf9ff",
                x=500,
                y=70,
                ttl=10,
                size="large",
            )


def check_overlay_message():
    global OVERLAY
    OVERLAY.send_message(
        "Copilot",
        f"Copilot overlay is operational",
        "#ff9966",
        x=520,
        y=200,
        ttl=10,
        size="large",
    )


def read_route():
    logger.info("Reading route file")
    with open(os.path.join(PLUGIN_DIRECTORY, "route.csv"), "r") as f:
        lines = [[field[1:-1] for field in line.split(",")] for line in f.readlines()]
    route = {name: [line[i] for line in lines[1:]] for i, name in enumerate(lines[0])}
    return route
