# Proyecto POO – Practica Avanzada

## Introducción
Este proyecto es una continuación de la práctica 1, en la que hemos trabajado con programación orientada a objetos en Python.  
En esta versión se aplican conceptos avanzados como **clases abstractas**, **herencia múltiple**, **decoradores**, **programación defensiva** con `try/except`, y **genericidad** usando clases parametrizadas.  
El proyecto consiste en un sistema de comunicación basado en Meshtastic y MQTT, capaz de enviar y recibir mensajes, posiciones y datos de sensores.

## Objetivos
- Aplicar conceptos avanzados de POO en un proyecto real.
- Implementar clases abstractas y herencia múltiple.
- Usar decoradores (`@staticmethod`, `@property`, `@abstractmethod`) en funciones existentes.
- Aplicar programación defensiva con `try/except` y excepciones personalizadas.
- Demostrar la genericidad con una clase `GestorPayload` capaz de manejar distintos tipos de datos.
- Integrar la comunicación mediante MQTT con sensores y nodos Meshtastic.

  ## Estructura del proyecto
src/
  comunicador.py # Comunicación con nodos y MQTT
  meshtasticcomunicador.py # Clase para gestionar Meshtastic
  comunicadorsensores.py # Lectura de sensores vía MQTT
  basecomunicador.py # Clase abstracta BaseComunicador
  seguridadmixin.py # Herencia múltiple para seguridad
  gestor_payload.py # Clase genérica para manejar datos
  interfaz.py # Menú de interacción con el usuario
  main.py #Ejecución del programa principal.
  
  ## Requisitos
- Python 
- Librerías:
  - `paho-mqtt`
  - `cryptography`
  - `meshtastic`
 
  


  
