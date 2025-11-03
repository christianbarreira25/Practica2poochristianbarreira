import time
import os
from comunicador import Comunicador
from meshtasticcomunicador import MeshtasticClass
from comunicadorsensores import ComunicadorSensores

class Interfaz:
    def __init__(self):
        # Crear el dispositivo y comunicador
        self.dispositivo = MeshtasticClass()
        self.comunicacion = Comunicador(self.dispositivo)

        # Conectar al servidor MQTT aquí (no en Comunicador.__init__)
        print("Conectando al servidor MQTT...")
        self.comunicacion.connect_mqtt()
        time.sleep(1)
        print(" Conectado. Mostrando menú...")

    def mostrar_menu(self):
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Enviar mensaje")
        print("2. Enviar posición")
        print("3. Enviar info nodos")
        print("4. Escuchar sensores")
        print("5. Limpiar consola")
        print("6. Desconectar")
        print("7. Mostrar información del nodo")
        print("0. Salir")

    def ejecutar(self):
        while True:
            self.mostrar_menu()
            opcion = input("Selecciona una opción: ").strip()

            if opcion == "1":
                msg = input("Mensaje a enviar: ")
                self.comunicacion.send_message(self.comunicacion.node_number, msg)
                self.comunicacion.message_text= msg

            elif opcion == "2":
                lat = input("Latitud: ")
                lon = input("Longitud: ")
                alt = input("Altitud: ")
                self.comunicacion.send_position(lat, lon, alt)

            elif opcion == "3":
                self.comunicacion.send_node_info(self.comunicacion.node_number, False)

            elif opcion == "4":
                print("Esperando mensajes... Presiona Ctrl+C para salir")
                

            elif opcion == "5":
                os.system("cls" if os.name == "nt" else "clear")

            elif opcion == "6":
                print("Desconectando del servidor MQTT...")
                self.comunicacion.disconnect_mqtt()

            elif opcion == "7":
                print("Información del nodo:")
                print(self.comunicacion.info_nodo())

            elif opcion == "0":
                print("Saliendo del programa...")
                self.comunicacion.disconnect_mqtt()
                break

            else:
                print("Opción no válida, intenta de nuevo.")

            time.sleep(1)
