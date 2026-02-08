import time

import datetime
import json
import os
import select
import zipfile

from sarc.helpers import is_bad_packet, BAD_PACKETS, convert_millis
from sarc.network import send_chat_message
from sarc.packet import Packet
from sarc.protocol import CLIENTBOUND, SERVERBOUND, MC_VERSION, PROTOCOL_VERSION, METADATA_FILE_FORMAT


def run_recorder(config, debug, address, connection):
    start_time = int(time.time() * 1000)
    last_player_movement = start_time
    should_restart = False
    client_name = config.get('username', '').strip()
    client_name_lower = client_name.lower()
    entity_packets = ['Entity', 'Entity Relative Move', 'Entity Look And Relative Move', 'Entity Look',
                      'Entity Teleport']
    player_uuids = []
    player_ids = []
    blocked_entity_ids = []
    write_buffer = bytearray()
    file_size = 0
    afk_time = 0
    last_t = 0
    if config.get('recording', False):
        open('recording.tmcpr', 'w').close()
    time.sleep(0.5)
    if 'Time Update' in BAD_PACKETS:
        BAD_PACKETS.remove('Time Update')

    while True:
        ready_to_read = select.select([connection.socket], [], [], 0)[0]
        if ready_to_read:
            t = int(time.time() * 1000)
            try:
                packet_in = connection.receive_packet()
            except IOError:
                break
            packet_recorded = int(t - start_time - afk_time).to_bytes(4, byteorder='big', signed=True)
            packet_recorded += len(packet_in.received).to_bytes(4, byteorder='big', signed=True)
            packet_recorded += packet_in.received
            packet_id = packet_in.read_varint()
            packet_name = CLIENTBOUND[str(packet_id)]
            if debug:
                print('P Packet ' + hex(packet_id) + ': ' + packet_name)

            if packet_name == 'Keep Alive (clientbound)':
                packet_out = Packet()
                packet_out.write_varint(SERVERBOUND['Keep Alive (serverbound)'])
                keepalive_id = packet_in.read_long()
                packet_out.write_long(keepalive_id)
                connection.send_packet(packet_out)

            if packet_name == 'Update Health':
                health = packet_in.read_float()
                food = packet_in.read_varint()
                food_sat = packet_in.read_float()
                if health == 0.0:
                    packet_out = Packet()
                    packet_out.write_varint(SERVERBOUND['Client Status'])
                    packet_out.write_varint(0)
                    connection.send_packet(packet_out)

            if (24000 > config['daytime'] > 0 and packet_name == 'Time Update' and not
            is_bad_packet(packet_name, config['minimal_packets'])):
                print('Set daytime to: ' + str(config['daytime']))
                packet_daytime = Packet()
                packet_daytime.write_varint(
                    int(list(CLIENTBOUND.keys())[list(CLIENTBOUND.values()).index('Time Update')]))
                world_age = packet_in.read_long()
                packet_daytime.write_long(world_age)
                packet_daytime.write_long(-config['daytime'])
                packet_recorded = int(t - start_time).to_bytes(4, byteorder='big', signed=True)
                packet_recorded += len(packet_daytime.received).to_bytes(4, byteorder='big', signed=True)
                packet_recorded += packet_daytime.received
                write_buffer += packet_recorded
                BAD_PACKETS.append('Time Update')

            if not config['weather'] and packet_name == 'Change Game State':
                reason = packet_in.read_ubyte()
                if reason == 1 or reason == 2:
                    packet_recorded = ''

            if packet_name == 'Player Position And Look (clientbound)':
                x = packet_in.read_double()
                y = packet_in.read_double()
                z = packet_in.read_double()
                yaw = packet_in.read_float()
                pitch = packet_in.read_float()
                flag = packet_in.read_byte()
                teleport_id = packet_in.read_varint()
                packet_out = Packet()
                packet_out.write_varint(SERVERBOUND['Teleport Confirm'])
                packet_out.write_varint(teleport_id)
                connection.send_packet(packet_out)

            if packet_name == 'Spawn Player':
                entity_id = packet_in.read_varint()
                if entity_id not in player_ids:
                    player_ids.append(entity_id)
                uuid = packet_in.read_uuid()
                if uuid not in player_uuids:
                    player_uuids.append(uuid)
                last_player_movement = int(time.time() * 1000)

            if ((config['remove_items'] or config['remove_bats']) and
                    (packet_name == 'Spawn Object' or packet_name == 'Spawn Mob')):
                entity_id = packet_in.read_varint()
                uuid = packet_in.read_uuid()
                type = packet_in.read_byte()
                if ((packet_name == 'Spawn Object' and type == 2) or
                        (packet_name == 'Spawn Mob' and type == 65)):
                    blocked_entity_ids.append(entity_id)
                    packet_recorded = ''

            if config['remove_items'] and packet_name == 'Collect Item':
                packet_recorded = ''

            if packet_name in entity_packets:
                entity_id = packet_in.read_varint()
                if config['recording'] and entity_id in player_ids:
                    last_player_movement = t
                if entity_id in blocked_entity_ids:
                    recorded_packet = ''

            if packet_name == 'Player List Item':
                action = packet_in.read_varint()
                if config['recording'] and action == 0:
                    write_buffer += packet_recorded
                    player_number = packet_in.read_varint()
                    uuid = packet_in.read_uuid()
                    name = packet_in.read_utf()

            if packet_name == 'Chat Message (clientbound)':
                try:
                    chat = packet_in.read_utf()
                    chat = json.loads(chat)
                    if chat['translate'] == 'chat.type.text':
                        name = chat['with'][0]['hoverEvent']['value']['text'].split(':"')[1].split('"', 1)[0]
                        player_uuid = chat['with'][0]['hoverEvent']['value']['text'].split(':"')[2].split('"', 1)[0]
                        message = chat['with'][1]
                        print('<' + name + '> ' + message)

                        if message.startswith('!'):
                            parts = message.split(' ', 1)
                            command = parts[0].lower()
                            target_bot = parts[1].strip() if len(parts) > 1 else ''
                            target_bot_lower = target_bot.lower()

                            should_respond = not target_bot or not client_name or target_bot_lower == client_name_lower

                            if should_respond:
                                if command == '!relog':
                                    should_restart = True
                                    print('Relogging...')
                                    break
                                if command == '!stop':
                                    should_restart = False
                                    print('Stopping...')
                                    break
                                if command == '!ping':
                                    send_chat_message(connection, SERVERBOUND, 'pong!')
                                if command == '!filesize':
                                    send_chat_message(connection, SERVERBOUND,
                                                      str(round(file_size / 1000000, 1)) + 'MB')
                                if command == '!time':
                                    send_chat_message(connection, SERVERBOUND,
                                                      'Recorded time: ' + convert_millis(
                                                          t - start_time - afk_time))
                                if command == '!timeonline':
                                    send_chat_message(connection, SERVERBOUND,
                                                      'Time client was online: ' + convert_millis(
                                                          t - start_time))
                                if command == '!move':
                                    packet_out = Packet()
                                    packet_out.write_varint(SERVERBOUND['Spectate'])
                                    packet_out.write_uuid(player_uuid)
                                    connection.send_packet(packet_out)
                                    send_chat_message(connection, SERVERBOUND, 'moved to ' + name)
                                if command == '!glow':
                                    send_chat_message(connection, SERVERBOUND,
                                                      '/effect @p minecraft:glowing 1000000 0 true')
                except:
                    pass

            if (config['recording'] and t - last_player_movement <= 5000 and not
            is_bad_packet(packet_name, config['minimal_packets'])):
                if packet_recorded != '':
                    write_buffer += packet_recorded
                if len(write_buffer) > 8192:
                    with open('recording.tmcpr', 'ab+') as replay_recording:
                        replay_recording.write(write_buffer)
                        if debug:
                            print('Recorded:' + str(write_buffer)[:80] + '...')
                        file_size += len(write_buffer)
                        write_buffer = bytearray()

            if not config['recording'] and len(write_buffer) > 0:
                write_buffer = bytearray()

            if config['recording'] and t - last_player_movement > 5000:
                afk_time += t - last_t

            last_t = t

            if config['recording'] and file_size > 150000000:
                pass

            if config['recording']:
                limit_mb = config.get('filesize_limit_mb', 150)
                if file_size > int(limit_mb * 1000000):
                    curr_mb = round(file_size / 1000000, 1)
                    print(f'Filesize limit reached! limit: {limit_mb}MB, current: {curr_mb}MB')
                    send_chat_message(connection, SERVERBOUND, f'Filesize limit reached ({limit_mb}MB), current {curr_mb}MB, restarting...')
                    should_restart = True
                    time.sleep(1)
                    break

                limit_min = config.get('recording_time_limit_min', 300)
                recorded_ms = t - start_time - afk_time
                if recorded_ms > limit_min * 60 * 1000:
                    recorded_min = round(recorded_ms / (60 * 1000), 1)
                    print(f'Recording time limit reached! limit: {limit_min}min, current: {recorded_min}min')
                    send_chat_message(connection, SERVERBOUND, f'Recording time limit reached ({limit_min}min), current {recorded_min}min, restarting...')
                    should_restart = True
                    time.sleep(1)
                    break

        else:
            time.sleep(0.0001)

    print('Disconnected')
    if config['recording'] and len(write_buffer) > 0:
        with open('recording.tmcpr', 'ab+') as replay_recording:
            replay_recording.write(write_buffer)
            write_buffer = bytearray()
    print('Time client was online: ' + convert_millis(t - start_time))

    if config['recording']:
        print('Recorded time: ' + convert_millis(t - start_time - afk_time))

        with open('metaData.json', 'w') as json_file:
            meta_data = {'singleplayer': 'false', 'serverName': address[0],
                         'duration': int(time.time() * 1000) - start_time - afk_time, 'date': int(time.time() * 1000),
                         'mcversion': MC_VERSION, 'fileFormat': 'MCPR', 'generator': 'SARC',
                         'fileFormatVersion': METADATA_FILE_FORMAT,
                         'protocol': PROTOCOL_VERSION, 'selfId': -1, 'players': player_uuids}
            json.dump(meta_data, json_file)

        print('Creating .mcpr file...')
        date = datetime.datetime.today().strftime('SARC_%Y%m%d_%H_%S')
        zipf = zipfile.ZipFile(date + '.mcpr', 'w', zipfile.ZIP_DEFLATED)
        zipf.write('metaData.json')
        zipf.write('recording.tmcpr')
        os.remove('metaData.json')
        os.remove('recording.tmcpr')
        print('Finished!')
    connection.close()
    return should_restart
