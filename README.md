# Stand Alone Replay Client - SARC

Written in Python.


## General

This is a stand alone client to join Minecraft servers. The client is able to record the incoming packets of the server in the `.TMCPR` format which is compatible with ReplayMod.
This client can be used as lightweight AFK client when recording is disabled.
The main purpose of this client is the recording of long timelapses.
This client can join vanilla servers and does **not** require any server side support like plugins. It should be able to join custom servers like spigot aswell since it performs the vanilla joining handshake, any kind of server side anti cheat is probably going to cause issues.
The used Accoutn should be opped and in spectator mode. Basic functionality might exist, however using an account without op is not supported or tested.

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

```!filesize``` : Sends current filesize of the recording.

```!time``` : Sends the length of current recording.

```!timeonline``` : Sends the elapsed time since SARC was connected.

```!move``` : Teleports the SARC account to the executer.

```!glow``` : Gives the SARC account glowing effect for better visibility.



## Currrently avaliable protocol versions:
4 - Minecraft 1.7.2 & 1.7.4 & 1.7.5

5 - Minecraft 1.7.6 & 1.7.7 & 1.7.8 & 1.7.9 & 1.7.10

47 - Minecraft 1.8 & 1.8.1 & 1.8.2 & 1.8.3 & 1.8.4 & 1.8.5 & 1.8.6 & 1.8.7 & 1.8.8 & 1.8.9

107 - Minecraft 1.9

109 - Minecraft 1.9.2

110 - Minecraft 1.9.3 & 1.9.4

210 - Minecraft 1.10 & 1.10.1 & 1.10.2

315 - Minecraft 1.11

316 - Minecraft 1.11.1 & 1.11.2

335 - Minecraft 1.12

338 - Minecraft 1.12.1

340 - Minecraft 1.12.2

401 - Minecraft 1.13.1

404 - Minecraft 1.13.2

498 - Minecraft 1.14.4

578 - Minecraft 1.15.2


Any kind of protocol version in between these listed ones, is going to end up using the protocol table from the next lower listed one.
Joining and/or recording in protocol versions in between might still work even if its not listed here.
SARC only interacts with a very small amount of different packet types, all other packets just get saved to a file. Therefor changes to the procol often have very little effect on this client.

### Developers
- Robi
- Nessie
- Thanks to elij for help
