# Práctica 1 - Comunicación Mesh con MQTT

## Descripción del proyecto

Este proyecto simula una red de comunicación entre nodos utilizando MQTT como protocolo de transporte. Cada nodo puede enviar mensajes cifrados, compartir su posición GPS y registrar datos de sensores ambientales. Toda la información se guarda en archivos JSON para mantener un historial persistente.

El sistema está desarrollado en Python y estructurado en clases para facilitar su mantenimiento y escalabilidad. Se ha probado en entorno local y está preparado para integrarse en redes Mesh reales.

## Requisitos

- Python 3.8 o superior
- Paquetes necesarios:
  - meshtastic
  - paho-mqtt
  - cryptography

-Instalación rápida:
pip install meshtastic paho-mqtt cryptography


## Estructura del proyecto

- `main.py`: punto de entrada del sistema.
- `interfaz.py`: menú interactivo por consola para el usuario.
- `comunicador.py`: gestiona la conexión MQTT, el cifrado AES CTR y el envío/recepción de mensajes.
- `dispositivo.py`: maneja la identidad del nodo y guarda los datos en JSON.
- `data/`: carpeta donde se almacenan los archivos `mensajes.json`, `gps.json` y `sensores.json`.

## Cómo ejecutar

-Desde la terminal, en la raíz del proyecto:
python main.py


Una vez iniciado, se mostrará un menú con opciones para enviar mensajes, posiciones, simular sensores, etc.

## Autor

Christian Barreira

## Repositorio

Puedes consultar el código completo en GitHub:

https://github.com/christianbarreira25/Practica1poochristianbarreira
