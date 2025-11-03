from meshtastic.protobuf import mesh_pb2, mqtt_pb2, portnums_pb2
from meshtastic import BROADCAST_NUM, protocols
import paho.mqtt.client as mqtt
import random
import time
import ssl
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import re
from meshtasticcomunicador import MeshtasticClass


class Comunicador:
    def __init__(self, dispositivo):
        self.dispositivo = dispositivo
        self.meshtastic = MeshtasticClass()
        # Debug y opciones base
        self.debug = True
        self.auto_reconnect = True
        self.auto_reconnect_delay = 1
        self.print_service_envelope = False
        self.print_message_packet = False

        self.print_node_info = True
        self.print_node_position = True
        self.print_node_telemetry = True

        # Configuración MQTT por defecto
        self.mqtt_broker = "mqtt.meshtastic.org"
        self.mqtt_port = 1883
        self.mqtt_username = "meshdev"
        self.mqtt_password = "large4cats"
        self.root_topic = "msh/EU_868/ES/2/e/"
        self.channel = "TestMQTT"
        self.key = "ymACgCy9Tdb8jHbLxUxZ/4ADX+BWLOGVihmKHcHTVyo="
        self.message_text = "Hola desde el ordenador de Christian"

        # Generar nodo y variables
        random_hex = "ab70"
        self.node_name = '!abcd' + random_hex
        self.node_number = int(self.node_name.replace("!", ""), 16)
        self.global_message_id = random.getrandbits(32)
        self.client_short_name = "CBS"
        self.client_long_name = "Christian"
        self.lat = "0"
        self.lon = "0"
        self.alt = "0"
        self.client_hw_model = 255

        # Variables internas
        self.default_key = "1PG7OiApB1nwvP+rz05pAQ=="
        self.tls_configured = False

        # Configurar cliente MQTT
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def info_nodo(self):
    # Reenvía la llamada al objeto MeshtasticClass
        return self.meshtastic.info_nodo()

   
    def set_topic(self):
        if self.debug:
            print("set_topic")
        self.subscribe_topic = self.root_topic + self.channel + "/#"
        self.publish_topic = self.root_topic + self.channel + "/" + self.node_name

    def xor_hash(self, data):
        result = 0
        for char in data:
            result ^= char
        return result

    def generate_hash(self, name, key):
        replaced_key = key.replace('-', '+').replace('_', '/')
        key_bytes = base64.b64decode(replaced_key.encode('utf-8'))
        h_name = self.xor_hash(bytes(name, 'utf-8'))
        h_key = self.xor_hash(key_bytes)
        result = h_name ^ h_key
        return result
    
    def on_message(self, client, userdata, msg):
        se = mqtt_pb2.ServiceEnvelope()
        try:
            se.ParseFromString(msg.payload)
            if self.print_service_envelope:
                print("\nService Envelope:\n", se)
            mp = se.packet
            if self.print_message_packet:
                print("\nMessage Packet:\n", mp)
        except Exception as e:
            print(f"*** ServiceEnvelope: {str(e)}")
            return

        if mp.HasField("encrypted") and not mp.HasField("decoded"):
            self.decode_encrypted(mp)

        portNumInt = mp.decoded.portnum if mp.HasField("decoded") else None
        handler = protocols.get(portNumInt) if portNumInt else None

        pb = None
        if handler is not None and handler.protobufFactory is not None:
            pb = handler.protobufFactory()
            pb.ParseFromString(mp.decoded.payload)

        if pb:
            pb_str = str(pb).replace('\n', ' ').replace('\r', ' ').strip()
            mp.decoded.payload = pb_str.encode("utf-8")
            self.dispositivo.registrar_mensaje("remoto", self.node_name, pb_str)

        # Si no quieres ver los mensajes del broker, comenta la siguiente línea
        # if self.debug:
        #     print(mp)

    # -----------------------------------------------------------------
    # DECODIFICAR MENSAJES CIFRADOS
    # -----------------------------------------------------------------
    def decode_encrypted(self, mp):
        try:
            key_bytes = base64.b64decode(self.key.encode('ascii'))
            nonce_packet_id = getattr(mp, "id").to_bytes(8, "little")
            nonce_from_node = getattr(mp, "from").to_bytes(8, "little")
            nonce = nonce_packet_id + nonce_from_node
            cipher = Cipher(algorithms.AES(key_bytes), modes.CTR(nonce), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted_bytes = decryptor.update(getattr(mp, "encrypted")) + decryptor.finalize()
            data = mesh_pb2.Data()
            data.ParseFromString(decrypted_bytes)
            mp.decoded.CopyFrom(data)
        except Exception as e:
            if self.debug:
                print(f"*** Decryption failed: {str(e)}")

    # -----------------------------------------------------------------
    # CONEXIÓN MQTT
    # -----------------------------------------------------------------
    def connect_mqtt(self):
        if self.debug:
            print("connect_mqtt")

        try:
            if ':' in self.mqtt_broker:
                self.mqtt_broker, self.mqtt_port = self.mqtt_broker.split(':')
                self.mqtt_port = int(self.mqtt_port)

            if self.key == "AQ==":
                if self.debug:
                    print("key is default, expanding to AES128")
                self.key = "1PG7OiApB1nwvP+rz05pAQ=="

            padded_key = self.key.ljust(len(self.key) + ((4 - (len(self.key) % 4)) % 4), '=')
            replaced_key = padded_key.replace('-', '+').replace('_', '/')
            self.key = replaced_key

            self.client.username_pw_set(self.mqtt_username, self.mqtt_password)

            if self.mqtt_port == 8883 and not self.tls_configured:
                self.client.tls_set(ca_certs="cacert.pem", tls_version=ssl.PROTOCOL_TLSv1_2)
                self.client.tls_insecure_set(False)
                self.tls_configured = True

            self.client.connect(self.mqtt_broker, int(self.mqtt_port), 60)
            self.client.loop_start()
            self.dispositivo.estado_conexion = True

        except Exception as e:
            print(e)

    def disconnect_mqtt(self):
        if self.debug:
            print("disconnect_mqtt")
        if self.client.is_connected():
            self.client.disconnect()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        self.set_topic()
        if client.is_connected():
            print("client is connected")
        if reason_code == 0:
            if self.debug:
                print(f"Connected to server: {self.mqtt_broker}")
                print(f"Subscribe Topic: {self.subscribe_topic}")
                print(f"Publish Topic: {self.publish_topic}\n")
            client.subscribe(self.subscribe_topic)

    def on_disconnect(self, client, userdata, flags, reason_code, properties):
        if self.debug:
            print("on_disconnect")
        if reason_code != 0:
            if self.auto_reconnect:
                print(f"attempting to reconnect in {self.auto_reconnect_delay} second(s)")
                time.sleep(self.auto_reconnect_delay)
                self.connect_mqtt()

    # -----------------------------------------------------------------
    # ENVIAR MENSAJES
    # -----------------------------------------------------------------
    def send_message(self, destination_id, message_text):
        """Enviar un mensaje de texto por MQTT"""
        if not self.client.is_connected():
            self.connect_mqtt()

        if message_text:
            encoded_message = mesh_pb2.Data()
            encoded_message.portnum = portnums_pb2.TEXT_MESSAGE_APP
            encoded_message.payload = message_text.encode("utf-8")
            self.generate_mesh_packet(destination_id, encoded_message)
        else:
            if self.debug:
                print(" Mensaje vacío, no se envía.")

    def send_position(self, lat, lon, alt):
        """Enviar posición simulada"""
        pos_time = int(time.time())
        latitude = int(float(lat) * 1e7)
        longitude = int(float(lon) * 1e7)
        altitude_units = 1 / 3.28084 if 'ft' in str(alt) else 1.0
        altitude = int(altitude_units * float(re.sub('[^0-9.]', '', str(alt))))

        position_payload = mesh_pb2.Position()
        setattr(position_payload, "latitude_i", latitude)
        setattr(position_payload, "longitude_i", longitude)
        setattr(position_payload, "altitude", altitude)
        setattr(position_payload, "time", pos_time)

        encoded_message = mesh_pb2.Data()
        encoded_message.portnum = portnums_pb2.POSITION_APP
        encoded_message.payload = position_payload.SerializeToString()
        encoded_message.want_response = True

        self.generate_mesh_packet(BROADCAST_NUM, encoded_message)
        print(f"Posición enviada: lat={lat}, lon={lon}, alt={alt}")

    def send_node_info(self, destination_id, want_response):
        """Enviar información del nodo"""
        user_payload = mesh_pb2.User()
        setattr(user_payload, "id", self.node_name)
        setattr(user_payload, "long_name", self.client_long_name)
        setattr(user_payload, "short_name", self.client_short_name)
        setattr(user_payload, "hw_model", self.client_hw_model)

        encoded_message = mesh_pb2.Data()
        encoded_message.portnum = portnums_pb2.NODEINFO_APP
        encoded_message.payload = user_payload.SerializeToString()
        encoded_message.want_response = want_response

        self.generate_mesh_packet(destination_id, encoded_message)
        print("Información de nodo enviada.")

    def generate_mesh_packet(self, destination_id, encoded_message):

        mesh_packet = mesh_pb2.MeshPacket()
        mesh_packet.id = self.global_message_id
        self.global_message_id += 1

        setattr(mesh_packet, "from", self.node_number)
        mesh_packet.to = destination_id
        mesh_packet.channel = self.generate_hash(self.channel, self.key)
        mesh_packet.hop_limit = 3
        mesh_packet.want_ack = False

        try:
            key_bytes = base64.b64decode(self.key.encode('ascii'))
            nonce_packet_id = mesh_packet.id.to_bytes(8, "little")
            nonce_from_node = self.node_number.to_bytes(8, "little")
            nonce = nonce_packet_id + nonce_from_node
            cipher = Cipher(algorithms.AES(key_bytes), modes.CTR(nonce), backend=default_backend())
            encryptor = cipher.encryptor()
            mesh_packet.encrypted = encryptor.update(encoded_message.SerializeToString()) + encryptor.finalize()
        except Exception as e:
            if self.debug:
                print(f"Error cifrando mensaje: {e}")
            mesh_packet.decoded.CopyFrom(encoded_message)

        service_envelope = mqtt_pb2.ServiceEnvelope()
        service_envelope.packet.CopyFrom(mesh_packet)
        service_envelope.channel_id = self.channel
        service_envelope.gateway_id = self.node_name

        payload = service_envelope.SerializeToString()
        self.client.publish(self.root_topic + self.channel + "/" + self.node_name, payload)
        print(f"Mensaje enviado: {encoded_message.payload.decode('utf-8', errors='ignore')}")

