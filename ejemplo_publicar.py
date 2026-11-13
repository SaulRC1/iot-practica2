#!/usr/bin/env python3
"""Ejemplo básico e introductorio de Publicación MQTT (HiveMQ).
Práctica 2 - IoT (MQTT Simple).

Este script muestra los pasos fundamentales para enviar mensajes a un broker MQTT:
1. Crear el cliente MQTT.
2. Definir callbacks (opcional para depuración de conexión).
3. Conectar al broker (broker.hivemq.com:1883).
4. Publicar mensajes en un topic específico.
5. Desconectar limpiamente.
"""

import time
import json
import paho.mqtt.client as mqtt

# 1. Configuración de conexión y topic
BROKER = "broker.hivemq.com"
PUERTO = 1883
GRUPO = "g01"                     # Cambia este identificador por el de tu grupo
TOPIC = f"iotlab26/{GRUPO}/prueba/saludo"

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback invocado cuando el broker responde a nuestra solicitud de conexión."""
    if rc == 0:
        print(" Conectado exitosamente al broker HiveMQ")
    else:
        print(f" Error de conexión con código {rc}")

def on_publish(client, userdata, mid, reason_code=None, properties=None):
    """Callback invocado cuando un mensaje ha sido enviado al broker."""
    print(f" Mensaje {mid} entregado al broker")

def main():
    print("=" * 60)
    print(" EJEMPLO BÁSICO: PUBLICADOR MQTT")
    print("=" * 60)
    print(f"Broker: {BROKER}:{PUERTO}")
    print(f"Topic:  {TOPIC}\n")

    # 2. Creación del cliente (compatible con paho-mqtt v1 y v2)
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"pub-intro-{GRUPO}")
    except AttributeError:
        client = mqtt.Client(client_id=f"pub-intro-{GRUPO}")

    client.on_connect = on_connect
    client.on_publish = on_publish

    # 3. Conexión al broker
    print(f"Conectando a {BROKER}...")
    client.connect(BROKER, PUERTO, keepalive=60)
    client.loop_start()  # Inicia un hilo secundario para gestionar la red

    time.sleep(1)  # Breve pausa para completar el handshake

    # 4. Publicar varios mensajes de prueba
    for i in range(1, 6):
        mensaje = {
            "contador": i,
            "texto": f"Hola desde Python (mensaje {i})",
            "timestamp": time.strftime("%H:%M:%S")
        }
        payload_str = json.dumps(mensaje)

        print(f"\n📤 Publicando en '{TOPIC}':")
        print(f"   Payload: {payload_str}")
        
        # client.publish(topic, payload, qos=0, retain=False)
        info = client.publish(TOPIC, payload_str, qos=0)
        info.wait_for_publish()
        
        time.sleep(2)

    # 5. Cierre limpio
    print("\n Finalizada la prueba. Desconectando...")
    client.loop_stop()
    client.disconnect()
    print(" Desconectado.")

if __name__ == "__main__":
    main()
