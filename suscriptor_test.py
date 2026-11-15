import sys
import time
import paho.mqtt.client as mqtt
from config import (
    BROKER_DEFAULT,
    PUERTO_DEFAULT,
    GRUPO_DEFAULT,
    KEEPALIVE_DEFAULT,
    topic_todo
)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(" Suscriptor de prueba conectado al broker MQTT.")

        topic_comodin = topic_todo(GRUPO_DEFAULT)
        
        client.subscribe(topic_comodin, qos=0)
        print(f" Escuchando todo en el topic comodín: '{topic_comodin}'")
        print(" Esperando mensajes retenidos del broker... (Pulsa Ctrl+C para salir)\n")
    else:
        print(f" Error de conexión al broker. Código: {rc}")

def on_message(client, userdata, msg):
    # Se ejecuta al recibir cualquier mensaje (incluyendo los retenidos al conectar)
    payload_decodificado = msg.payload.decode("utf-8")
    print(f"  [MENSAJE RECIBIDO]")
    print(f"   Topic   : {msg.topic}")
    print(f"   Payload : {payload_decodificado}")
    print(f"   Retain  : {msg.retain} (True = Guardado en el broker / False = Efímero)\n")

def main():  
    client_id = f"suscriptor-test-{GRUPO_DEFAULT}"

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    except AttributeError:
        client = mqtt.Client(client_id=client_id)

    client.on_connect = on_connect
    client.on_message = on_message

    print(f"Conectando a {BROKER_DEFAULT}:{PUERTO_DEFAULT} para el grupo '{GRUPO_DEFAULT}'...")
    client.connect(BROKER_DEFAULT, PUERTO_DEFAULT, KEEPALIVE_DEFAULT)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nSuscriptor cerrado por el usuario. Desconectando...")
        client.disconnect()
        print("Desconexión completada.")

if __name__ == "__main__":
    main()