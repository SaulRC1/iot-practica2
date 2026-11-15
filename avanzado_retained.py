import sys
import time
import json
import paho.mqtt.client as mqtt
from config import (
    BROKER_DEFAULT,
    PUERTO_DEFAULT,
    GRUPO_DEFAULT,
    KEEPALIVE_DEFAULT
)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Publicador de prueba conectado al broker MQTT.")
    else:
        print(f"Error de conexión al broker. Código: {rc}")

def main():
    
    client_id = f"avanzado-retained-{GRUPO_DEFAULT}"

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    except AttributeError:
        client = mqtt.Client(client_id=client_id)

    client.on_connect = on_connect

    print(f"Conectando a {BROKER_DEFAULT}:{PUERTO_DEFAULT} para el grupo '{GRUPO_DEFAULT}'...")
    client.connect(BROKER_DEFAULT, PUERTO_DEFAULT, KEEPALIVE_DEFAULT)
    client.loop_start() 

    time.sleep(1)

    # Definir topics de prueba
    topic_sensor_efimero = f"iotlab26/{GRUPO_DEFAULT}/sensor/temperatura"
    topic_actuador_retenido = f"iotlab26/{GRUPO_DEFAULT}/actuador/bombilla/estado"

    print("\n" + "="*50)
    print("   DEMOSTRACIÓN DE MENSAJES RETAINED vs EFÍMEROS   ")
    print("="*50)

    # 1. Publicar mensaje EFÍMERO (retain=False) - Simula un sensor
    payload_sensor = json.dumps({
        "valor": 22.5,
        "unidad": "ºC",
        "timestamp": time.strftime("%H:%M:%S"),
        "nota": "Este es un dato de sensor efímero"
    })
    print(f"\nPublicando EFÍMERO (retain=False) en '{topic_sensor_efimero}'...")
    client.publish(topic_sensor_efimero, payload_sensor, qos=0, retain=False)

    time.sleep(1)

    # 2. Publicar mensaje RETENIDO (retain=True) - Simula el estado de un actuador
    payload_actuador = json.dumps({
        "actuador": "bombilla",
        "estado": "ON",
        "timestamp": time.strftime("%H:%M:%S"),
        "nota": "Este es un estado retenido"
    })
    print(f"Publicando RETENIDO (retain=True) en '{topic_actuador_retenido}'...")
    client.publish(topic_actuador_retenido, payload_actuador, qos=0, retain=True)

    time.sleep(1)

    print("\n El emisor ha terminado de publicar y se va a desconectar...")
    client.loop_stop()
    client.disconnect()
    print(" Emisor desconectado del broker con éxito.")

if __name__ == "__main__":
    main()