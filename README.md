# Stand Alone Replay Client - SARC

Written in Python.


## General

This is a stand alone client to join Minecraft servers. The client is able to record the incoming packets of the server in the `.TMCPR` format which is compatible with ReplayMod.
This client can be used as lightweight AFK client when recording is disabled.
The main purpose of this client is the recording of long timelapses.


#### Advantages compared to normal user recording with ReplayMod

- Can be hosted serverside for 24/7 recording

- The client detects players in the recorded area and pauses the recording while no player is detected

- There are many optimisations made to the type and amount of recorded packets to decrease filesize of replays as much as possible so the ReplayMod can handle replays with many hours of footage

- Several options to modify the world

- Recording can be turned off for only afking


## Configuration

```ip``` : IP-Address of the Minecraft server.

```port``` : Port of the Minecraft server.

```username``` : Username or email for the used Minecraft account.

```password``` : Password for the used Minecraft account.

```recording``` : True if SARC should actually record anything.

```minimal_packets``` : SARC will only record the minimum needed packets for a proper recording when this option is turned on. This should be used to decrease the filesize of recordings while recording long term projects (timelapse).

```daytime``` : Sets the daytime once to the defined time in the recording and ignores all further changes from the server. If set to `-1` the normal day/night cycle is recorded.

```weather``` : Turns weather in the recording on or off.

```remove_items``` : If set to true, all dropped items wont be recorded. This can potentially decrease filesize.

```remove_bats``` : If set to true, bats wont be recorded. This can potentially decrease filesize.

```debug_mode``` : Outputs all received, sent and recorded packets.

```auto_relog``` : If this option is enabled and the client gets disconnected, it will automatically reconnect after 3 seconds.

```require_op``` : If true, the client will only accept commands by opped players.


## Other

To reduce hassle with big files in ReplayMod, SARC automatically switches to a new file after the recording reached 300MB.
The SARC account should be opped and in spectator mode to make the following ingame commands avaliable:

```!relog``` : Relogs the client and starts recording in a new file.

```!stop``` : Disconnects the client and stops recording.

```!ping``` : Sends a pong response back for testing.

```!filesize``` : Sends the current filesize of the recording.

```!time``` : Sends the length of the recording.

```!timeonline``` : Sends the elapsed time since SARC was connected.

```!move``` : Teleports the SARC account to the executer.

```!glow``` : Gives the SARC account glowing effect for better visibility.

#### Developers
- Robi
- Nessie
- Thanks to elij for help
