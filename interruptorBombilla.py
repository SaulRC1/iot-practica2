import time
import paho.mqtt.client as mqtt
import threading
from config import (
    BROKER_DEFAULT,
    PUERTO_DEFAULT,
    GRUPO_DEFAULT,
    KEEPALIVE_DEFAULT,
    topic_actuador_set
)

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Interruptor de Bombilla conectado al broker MQTT.")
    else:
        print(f"Error de conexión al broker. Código: {rc}")

def escuchar_teclado(client, topic_destino):
    print("INTERRUPTOR MANUAL DE BOMBILLA")
    print("Escriba el comando ON u OFF para encender/apagar la bombilla")
    print("Escriba SALIR para cerrar el programa.\n")

    try:
        while True:
            comando = input("Nuevo estado estado para la bombilla: ").strip().upper()

            if comando == "SALIR":
                print("Cerrando interruptor...")
                break
            if comando in ["ON", "OFF"]:
                info = client.publish(topic_destino, comando, qos=0)
                info.wait_for_publish()
                print(f"Orden enviada a '{topic_destino}': '{comando}'")
            else:
                print("Comando no válido")
    except Exception as e:
        print(f" Error en la lectura del comando: {e}")

def main():
    client_id = f"interruptor-bombilla-{GRUPO_DEFAULT}"
    topic_destino = topic_actuador_set("bombilla", GRUPO_DEFAULT)

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    except AttributeError:
        client = mqtt.Client(client_id=client_id)

    client.on_connect
    print(f"Conectando a {BROKER_DEFAULT}:{PUERTO_DEFAULT}...")
    client.connect(BROKER_DEFAULT, PUERTO_DEFAULT, KEEPALIVE_DEFAULT)
    client.loop_start()

    time.sleep(1)

    hilo = threading.Thread(target=escuchar_teclado, args=(client, topic_destino), daemon=True)
    hilo.start()

    try:
        while hilo.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n Interrupción recibida")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()

    
