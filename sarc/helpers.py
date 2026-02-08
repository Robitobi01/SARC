import json

BAD_PACKETS = [
    'Unlock Recipes',
    'Advancements',
    'Select Advancement Tab',
    'Update Health',
    'Open Window',
    'Close Window (clientbound)',
    'Set Slot',
    'Window Items',
    'Open Sign Editor',
    'Statistics',
    'Set Experience',
    'Camera',
    'Player Abilities (clientbound)',
    'Title'
]

USELESS_PACKETS = [
    'Keep Alive (clientbound)',
    'Statistics',
    'Server Difficulty',
    'Tab-Complete (clientbound)',
    'Chat Message (clientbound)',
    'Confirm Transaction (clientbound)',
    'Window Property',
    'Set Cooldown',
    'Named Sound Effect',
    'Map',
    'Resource Pack Send',
    'Display Scoreboard',
    'Scoreboard Objective',
    'Teams',
    'Update Score',
    'Sound Effect'
]


def is_bad_packet(packet_name, minimal_packets=False):
    if packet_name in BAD_PACKETS:
        return True
    if minimal_packets and packet_name in USELESS_PACKETS:
        return True
    return False


def load_config(path):
    try:
        with open(path, 'r', encoding='utf-8') as json_file:
            config = json.load(json_file)
    except FileNotFoundError:
        raise ValueError(f"Config file not found: {path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON config {path}: {e.msg} (line {e.lineno} column {e.colno})")

    required = ["ip", "port", "username", "uuid", "session_server"]
    missing = [k for k in required if k not in config]
    if missing:
        raise ValueError(f"Missing required config keys in {path}: {', '.join(missing)}")

    return config


def convert_millis(millis):
    seconds = int(millis / 1000) % 60
    minutes = int(millis / (1000 * 60)) % 60
    hours = int(millis / (1000 * 60 * 60))
    if seconds < 10:
        seconds = '0' + str(seconds)
    if minutes < 10:
        minutes = '0' + str(minutes)
    if hours < 10:
        hours = '0' + str(hours)
    return str(hours) + ':' + str(minutes) + ':' + str(seconds)
