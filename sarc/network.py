import json
import os
import requests
import select
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives.serialization import load_der_public_key
from hashlib import sha1

from sarc.connection import TCPConnection
from sarc.packet import Packet
from sarc.protocol import PROTOCOL_VERSION


def get_server_status(address):
    connection = TCPConnection(address)

    packet_out = Packet()
    packet_out.write_varint(0x00)
    packet_out.write_varint(PROTOCOL_VERSION)
    packet_out.write_utf(address[0])
    packet_out.write_ushort(address[1])
    packet_out.write_varint(1)
    connection.send_packet(packet_out)

    packet_out = Packet()
    packet_out.write_varint(0x00)
    connection.send_packet(packet_out)

    packet_in = connection.receive_packet()
    packet_id = packet_in.read_varint()
    if packet_id != 0x00:
        connection.close()
        raise RuntimeError("Unexpected status response packet")

    status_data = json.loads(packet_in.read_utf())
    connection.close()
    return status_data


def login(address, debug, uuid, user_name, session_server, auth_string):
    connection = TCPConnection(address, debug)

    packet_out = Packet()
    packet_out.write_varint(0x00)
    packet_out.write_varint(PROTOCOL_VERSION)
    packet_out.write_utf(address[0])
    packet_out.write_ushort(address[1])
    packet_out.write_varint(2)
    connection.send_packet(packet_out)

    packet_out = Packet()
    packet_out.write_varint(0x00)
    packet_out.write_utf(user_name)
    connection.send_packet(packet_out)

    while True:
        receive_ready, send_ready, exception_ready = select.select([connection.socket], [connection.socket], [], 0.01)
        if len(receive_ready) > 0:
            packet_in = connection.receive_packet()
            packet_id = packet_in.read_varint()
            if debug:
                print('L Packet ' + hex(packet_id))

            if packet_id == 0x00:
                print(packet_in.read_utf())

            if packet_id == 0x01:
                server_id = packet_in.read_utf()
                pub_key = packet_in.read_bytearray_as_str()
                ver_tok = packet_in.read_bytearray_as_str()

                shared_secret = os.urandom(16)
                verify_hash = sha1()
                verify_hash.update(server_id.encode('utf-8'))
                verify_hash.update(shared_secret)
                verify_hash.update(pub_key)
                server_id = format(int.from_bytes(verify_hash.digest(), byteorder='big', signed=True), 'x')

                payload = {
                    'selectedProfile': uuid,
                    'serverId': server_id
                }
                if auth_string:
                    payload['authString'] = auth_string

                res = requests.post(session_server,
                                    data=json.dumps(payload),
                                    headers={'content-type': 'application/json'})
                print('Client session auth', res.status_code)

                packet_out = Packet()
                packet_out.write_varint(0x01)
                pub_key = load_der_public_key(pub_key, default_backend())
                encrypt_token = pub_key.encrypt(ver_tok, PKCS1v15())
                encrypt_secret = pub_key.encrypt(shared_secret, PKCS1v15())
                packet_out.write_varint(len(encrypt_secret))
                packet_out.write(encrypt_secret)
                packet_out.write_varint(len(encrypt_token))
                packet_out.write(encrypt_token)
                connection.send_packet(packet_out)
                connection.configure_encryption(shared_secret)

            if packet_id == 0x02:
                u = packet_in.read_utf()
                n = packet_in.read_utf()
                print('Name: ' + n + '  |  UUID: ' + u)
                print('Switching to PLAY')
                break

            if packet_id == 0x03:
                connection.compression_threshold = packet_in.read_varint()
                print('Compression enabled, threshold:', connection.compression_threshold)
    return connection


def send_chat_message(connection, serverbound, message):
    packet_out = Packet()
    packet_out.write_varint(serverbound['Chat Message (serverbound)'])
    packet_out.write_utf(message)
    connection.send_packet(packet_out)
