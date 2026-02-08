# Stand Alone Replay Client - SARC

Written in Python.

## General

SARC is a stand-alone client that records incoming packets into `.TMCPR` files compatible with ReplayMod.
It targets long-running recordings and can be used as a lightweight AFK client when recording is disabled.
SARC only supports Minecraft 1.12.2 (protocol 340).

Authentication is supported only via SelfhostedYggdrasil: https://github.com/Robitobi01/SelfhostedYggdrasil

The pre-refactor version lives in the legacy branch.

## CLI

SARC is a command-line application. You must provide a config via `-c`.

```bash
sarc -g
sarc -c /path/to/config.json
```

## Configuration

```ip``` : IP address of the Minecraft server.

```port``` : Port of the Minecraft server.

```username``` : Username used for login and command targeting.

```uuid``` : UUID of the account.

```session_server``` : SelfhostedYggdrasil join URL (e.g. `http://localhost/session/minecraft/join`).

```auth_string``` : Optional auth string passed to the join endpoint.

```recording``` : True if SARC should record packets.

```minimal_packets``` : Only record the minimum packets needed for a proper replay.

```daytime``` : Sets the daytime once in the recording and ignores further changes. Use `-1` for normal cycle.

```weather``` : Turns weather recording on or off.

```remove_items``` : If true, dropped items are not recorded.

```remove_bats``` : If true, bats are not recorded.

```debug_mode``` : Outputs all received, sent, and recorded packets.

```auto_relog``` : If enabled, the client reconnects after 3 seconds on disconnect.

```filesize_limit_mb``` : Maximum recording file size in megabytes (MB).

```recording_time_limit_min``` : Maximum recording duration in minutes.

## Commands

Commands can be targeted to a specific SARC instance by adding the username:
`!ping MyRecorder`
If no username is provided, all SARC clients respond.

```!relog``` : Relogs and starts recording in a new file.

```!stop``` : Disconnects and stops recording.

```!ping``` : Sends a pong response.

```!filesize``` : Sends current recording size.

```!time``` : Sends length of current recording.

```!timeonline``` : Sends elapsed time since SARC connected.

```!move``` : Teleports the SARC account to the requester.

```!glow``` : Gives the SARC account glowing effect.

## Developers

- Robi
- Nessie
- Thanks to elij for help
