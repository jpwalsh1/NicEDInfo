import sys
import tkinter as tk
import myNotebook as nb
from config import config
from ttkHyperlinkLabel import HyperlinkLabel

this = sys.modules[__name__]
this.plugin_name = "Nic ED Info"
this.plugin_url = "https://github.com/jpwalsh1/NicEDInfo"
this.version_info = (0, 1, 0)
this.version = ".".join(map(str, this.version_info))


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
    else:
        this.status["text"] = "Ready CMDR " + cmdr


