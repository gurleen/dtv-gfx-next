import PySimpleGUI as sg
from serial.tools.list_ports import comports

from util.ident_fetch import get_items, get_ident, CONF_ROOT

def config_window():
    ports = comports()
    confs = get_items(CONF_ROOT)
    teams = []
    layout = [
        [sg.Text("DragonsTV Graphics Config")],
        [sg.Text("Set Away Team")],
        [sg.Combo([x[0] for x in confs], enable_events=True)],
        [sg.Combo([], enable_events=True, key="-TEAMS-", expand_x=True)],
        [sg.Text("Select AllSport CG Port")],
        [sg.Combo(ports, key="-SERIAL-")],
        [sg.Button("OK")]
    ]
    window = sg.Window("DragonsTV Graphics", layout)
    while True:
        event, values = window.read()
        if event == "OK" and values[0] and values["-TEAMS-"]:
            team_obj = next((x for x in teams if x[0] == values["-TEAMS-"]))
            ident = get_ident(team_obj[1])
            window.close()
            return {
                "awayName": values["-TEAMS-"].upper(),
                "awayNameLower": values["-TEAMS-"],
                "awayTeamName": ident[2].lstrip(values["-TEAMS-"]).lstrip(" ").upper(),
                "awayTeamNameLower": ident[2].lstrip(values["-TEAMS-"]).lstrip(" "),
                "awayColor": ident[0],
                "awayImg": ident[1],
                "com_port": values["-SERIAL-"].device if not isinstance(values["-SERIAL-"], str) else None
            }
        elif event == sg.WINDOW_CLOSED:
            window.close()
            quit()
        elif event == 0:
            conf_obj = next((x for x in confs if x[0] == values[0]))
            teams = get_items(conf_obj[1])
            window["-TEAMS-"].update(values=[x[0] for x in teams])