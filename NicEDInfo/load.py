import sys
import tkinter as tk
import myNotebook as nb
from config import config
from ttkHyperlinkLabel import HyperlinkLabel

this = sys.modules[__name__]
this.plugin_name = "Nic ED Info"
this.plugin_url = "https://github.com/jpwalsh1/NicEDInfo"
this.version_info = (0, 3, 0)
this.version = ".".join(map(str, this.version_info))
this.missions = {}


def plugin_start(plugin_dir):
    return this.plugin_name


def plugin_start3(plugin_dir):
    return plugin_start(plugin_dir)


def plugin_app(parent):
    label = tk.Label(parent, text="%s:" % this.plugin_name)
    this.status = tk.Label(parent, text="Ready", anchor=tk.W)
    return label, this.status


def plugin_prefs(parent, cmdr, is_beta):

    PADX = 10

    frame = nb.Frame(parent)
    frame.columnconfigure(1, weight=1)

    HyperlinkLabel(
        frame, text="Nic Streaming Plugin on Github", background=nb.Label().cget("background"),
        url=this.plugin_url, underline=True
    ).grid(row=8, padx=PADX, sticky=tk.W)
    nb.Label(frame, text="Version: %s" % this.version).grid(row=8, column=1, padx=PADX, sticky=tk.E)
    nb.Label(frame, text="Plugin saves game information in various files you can use in your OBS/Streamlabs scenes.").grid(row=9, padx=PADX, sticky=tk.W)
    nb.Label(frame, text="Files are saved in to output directory selected on the Output tab").grid(row=10, padx=PADX, sticky=tk.W)

    return frame


def set_state_frame_childs(frame, state):
    for child in frame.winfo_children():
        if child.winfo_class() in ("TFrame", "Frame", "Labelframe"):
            set_state_frame_childs(child, state)
        else:
            child["state"] = state


def journal_entry(cmdr, is_beta, system, station, entry, state):

    # Get current system
    if entry["event"] in ["Docked", "FSDJump", "Location", "SupercruiseEntry", "SupercruiseExit"] and not is_beta:
        this.status["text"] = "Updating Files..."

        # this.system = entry.get('StarSystem')
        current_system = config.get('outdir') + "/system.txt"
        with open(current_system, 'w') as system_file:
            system_file.write(entry.get('StarSystem'))
        # End current system update

        this.status["text"] = "System updated"

    # Get current game mode
    elif entry["event"] in ["LoadGame"] and not is_beta:
        if entry.get('GameMode') == "Open":
            this.mode = "Open"
        elif entry.get('GameMode') == "Solo":
            this.mode = "Solo"
        else:
            this.mode = entry.get('Group')
        current_mode = config.get('outdir') + "/mode.txt"
        with open(current_mode, "w") as mode_file:
            mode_file.write(this.mode)
        this.status["text"] = "Mode updated"
    # End get current game mode

    # Store the name of your Fleet Carrier.
    elif entry["event"] in ["CarrierStats"] and not is_beta:
        this.fleetcarrier_name = entry.get('Name')
        carrier_name = config.get('outdir') + "/carrier_name.txt"
        with open(carrier_name, "w") as carrier_name_file:
            carrier_name_file.write(this.fleetcarrier_name)

    # Build a message about your pending Fleet Carrier Jump
    elif entry["event"] in ["CarrierJumpRequest"] and not is_beta:
        this.system = entry.get('SystemName')
        # Get Fleet Carrier Name
        carrier_name = config.get('outdir') + "/carrier_name.txt"
        with open(carrier_name, "r") as carrier_name_file:
            this.fleetcarrier_name = carrier_name_file.read()
        # Message: [Fleet Carrier] is jumping to the [System Name] system.
        jump_text = "{} is jumping to the {} system.     ".format(this.fleetcarrier_name, this.system)
        carrier_jump = config.get('outdir') + "/carrier_jump.txt"
        with open(carrier_jump, "w") as jump_file:
            jump_file.write(jump_text)
        this.status["text"] = "Carrier Jump Detected"
    # Clear out carrier message file if jump is completed or cancelled.
    elif entry["event"] in ["CarrierJumpCancelled", "CarrierJump"] and not is_beta:
        carrier_info = config.get('outdir') + "/carrier_jump.txt"
        carrier_file = open(carrier_info, "r+")
        carrier_file.truncate(0)
        carrier_file.close()
        this.station["text"] = "Carrier Jump File Updated"

    # Log Passenger missions when accepted
    elif entry["event"] in ["MissionAccepted"] and not is_beta:
        if entry["Name"] in ["Mission_DS_PassengerBulk"]:
            this.missions[entry["MissionID"]] = entry["PassengerCount"]
            passenger_path = config.get('outdir') + "/passengers.txt"
            with open(passenger_path, "w") as passenger_file:
                pass
            this.status["text"] = "Passenger Mission Accepted: {} passengers".format(entry["PassengerCount"])

    # Once mission is completed, grab current total, add passengers from mission, update file
    elif entry["event"] in ["MissionCompleted"] and not is_beta:
        if entry["Name"] in ["Mission_DS_PassengerBulk_name"]:
            # Get current count
            passenger_path = config.get('outdir') + "/passengers.txt"
            with open(passenger_path, "r") as passenger_file:
                contents = passenger_file.readline()
                if not contents:
                    this.passenger_counts = 0
                else:
                    this.passenger_counts = int(contents)
            # Try to add completed mission passenger count
            try:
                this.passenger_counts += int(this.missions[entry["MissionID"]])
                del this.missions[entry["MissionID"]]
                passenger_path = config.get('outdir') + "/passengers.txt"
                with open(passenger_path, "w+") as passenger_file:
                    passenger_file.write(str(this.passenger_counts))
                this.status["text"] = "Delivered {} passengers.".format(str(this.passenger_counts))
            except KeyError:
                this.status["text"] = "Unknown Mission Completed"
    else:
        this.status["text"] = "Ready CMDR " + cmdr


