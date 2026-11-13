#!/usr/bin/env python3
"""Ejemplo básico e introductorio de Suscripción MQTT (HiveMQ).
Práctica 2 - IoT (MQTT Simple).

Este script muestra los pasos fundamentales para recibir mensajes desde un broker:
1. Crear el cliente MQTT.
2. Definir el callback `on_message` que se ejecuta cada vez que llega un mensaje.
3. Conectar al broker (broker.hivemq.com:1883).
4. Suscribirse a un topic o a un comodín (#).
5. Mantener la escucha activa con `loop_forever()`.
"""

import sys
import paho.mqtt.client as mqtt

# 1. Configuración de conexión y topic
BROKER = "broker.hivemq.com"
PUERTO = 1883
GRUPO = "g01"                     # Cambia este identificador por el de tu grupo
TOPIC_SUSCRIPCION = f"iotlab26/{GRUPO}/prueba/#"

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback que se ejecuta al conectar con el broker.
    Aquí realizamos las suscripciones deseadas.
    """
    if rc == 0:
        print(" Conectado exitosamente al broker HiveMQ")
        print(f"📡 Suscribiéndose al topic: {TOPIC_SUSCRIPCION}")
        client.subscribe(TOPIC_SUSCRIPCION, qos=0)
    else:
        print(f" Error de conexión con código {rc}")

def on_message(client, userdata, msg):
    """Callback invocado automáticamente cada vez que llega un mensaje en un topic suscrito."""
    topic = msg.topic
    payload = msg.payload.decode("utf-8", errors="replace")
    qos = msg.qos
    retain = msg.retain

    print("\n📨 MENSAJE RECIBIDO:")
    print(f"   • Topic:  {topic}")
    print(f"   • QoS:    {qos} | Retenido: {retain}")
    print(f"   • Cuerpo: {payload}")

def main():
    print("=" * 60)
    print(" EJEMPLO BÁSICO: RECEPTOR / SUSCRIPTOR MQTT")
    print("=" * 60)
    print(f"Broker: {BROKER}:{PUERTO}")
    print(f"Topic:  {TOPIC_SUSCRIPCION}")
    print("Presiona Ctrl+C en cualquier momento para detener la escucha.\n")

    # 2. Creación del cliente (compatible con paho-mqtt v1 y v2)
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"sub-intro-{GRUPO}")
    except AttributeError:
        client = mqtt.Client(client_id=f"sub-intro-{GRUPO}")

    client.on_connect = on_connect
    client.on_message = on_message

    # 3. Conexión al broker
    print(f"Conectando a {BROKER}...")
    try:
        client.connect(BROKER, PUERTO, keepalive=60)
        # 4. Bucle infinito de escucha (bloqueante)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\n Deteniendo el receptor...")
        client.disconnect()
        print(" Desconectado correctamente. ¡Hasta luego!")
        sys.exit(0)

if __name__ == "__main__":
    main()
