import time
from importlib import resources

import argparse
import os
import traceback

from sarc.helpers import load_config
from sarc.network import get_server_status, login
from sarc.protocol import PROTOCOL_VERSION, MC_VERSION
from sarc.recorder import run_recorder


def write_example_config(destination):
    content = resources.files("sarc").joinpath("config.example.json").read_text(encoding="utf-8")
    with open(destination, "w", encoding="utf-8") as config_file:
        config_file.write(content)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="sarc")
    parser.add_argument("-c", "--config", help="Path to config JSON")
    parser.add_argument("-g", "--generate-config", action="store_true", help="Write example config to ./config.json")
    args = parser.parse_args(argv)

    if args.generate_config:
        destination = os.path.join(os.getcwd(), "config.json")
        write_example_config(destination)
        print(destination)
        return 0

    if not args.config:
        parser.error("the following arguments are required: -c/--config")

    try:
        config = load_config(args.config)
    except ValueError as e:
        print(f"Error loading config: {e}")
        return 3

    debug = config["debug_mode"]
    address = (config["ip"], int(config["port"]))
    session_server = config.get("session_server", "https://sessionserver.mojang.com/session/minecraft/join")
    auth_string = config.get("auth_string", "")
    user_name = config["username"]
    uuid = config["uuid"]

    try:
        status = get_server_status(address)
    except Exception as e:
        print(f"Failed to retrieve server status: {e}")
        return 4

    status_version = status.get("version", {})
    server_protocol = status_version.get("protocol")
    server_name = status_version.get("name", "unknown")
    if server_protocol != PROTOCOL_VERSION:
        print(
            f"Server protocol is {server_protocol} ({server_name}), this only supports {MC_VERSION} ({PROTOCOL_VERSION}).")
        return 2

    while True:
        try:
            connection = login(address, debug, uuid, user_name, session_server, auth_string)
            should_restart = run_recorder(config, debug, address, connection)

            if not should_restart:
                break
            else:
                print("Reconnecting...")
        except KeyboardInterrupt:
            print("Interrupted, shutting down...")
            break
        except Exception as e:
            if debug:
                print("Connection lost: " + traceback.format_exc())
            else:
                print("Connection lost: " + str(e))
            if not config["auto_relog"]:
                break
            else:
                print("Reconnecting...")
        time.sleep(3)
    print("Ending...")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
