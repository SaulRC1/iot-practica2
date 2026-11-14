import paho.mqtt.client as mqtt
import json
import time
from config import (
    BROKER_DEFAULT,
    PUERTO_DEFAULT,
    GRUPO_DEFAULT,
    KEEPALIVE_DEFAULT,
    ESTADO_PERSIANA_CERRADA,
    ESTADO_PERSIANA_ABIERTA,
    TIPO_ACTUADOR_TOPIC_PERSIANA,
    topic_actuador_set
)

TOPIC_PUB_ACTUADOR_PERSIANA = topic_actuador_set(TIPO_ACTUADOR_TOPIC_PERSIANA)

def publicar_estado_persiana(cliente_mqtt, estado):
    payload = estado.encode("utf-8")
    info = cliente_mqtt.publish(TOPIC_PUB_ACTUADOR_PERSIANA, payload, qos=0)
    info.wait_for_publish()

def mostrar_menu(cliente_mqtt):
    while True:
        print("\n===== MENÚ PRINCIPAL =====")
        print("1. ABRIR PERSIANA")
        print("2. CERRAR PERSIANA")
        print("3. SALIR")

        opcion = input("Selecciona una opción: ")

        if opcion == "1":
            print("Abriendo persiana...")
            publicar_estado_persiana(cliente_mqtt, ESTADO_PERSIANA_ABIERTA)

        elif opcion == "2":
            print("Cerrando persiana...")
            publicar_estado_persiana(cliente_mqtt, ESTADO_PERSIANA_CERRADA)

        elif opcion == "3":
            print("Saliendo del programa...")
            break

        else:
            print("Opción no válida")

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback invocado cuando el broker responde a nuestra solicitud de conexión."""
    if rc == 0:
        print(" Conectado exitosamente al broker HiveMQ")
    else:
        print(f" Error de conexión con código {rc}")

def on_publish(client, userdata, mid, reason_code=None, properties=None):
    """Callback invocado cuando un mensaje ha sido enviado al broker."""
    print(f"Mensaje {mid} entregado al broker")

def main():
    # Creación del cliente (compatible con paho-mqtt v1 y v2)
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"pub-interruptorPersiana-{GRUPO_DEFAULT}")
    except AttributeError:
        client = mqtt.Client(client_id=f"pub-interruptorPersiana-{GRUPO_DEFAULT}")
    
    client.on_connect = on_connect
    client.on_publish = on_publish
    
    # Conexión al broker
    print(f"Conectando a {BROKER_DEFAULT}...")
    client.connect(BROKER_DEFAULT, PUERTO_DEFAULT, keepalive=KEEPALIVE_DEFAULT)
    client.loop_start()  # Inicia un hilo secundario para gestionar la red
    
    time.sleep(1)  # Breve pausa para completar el handshake

    # Mostrar menú
    mostrar_menu(client)

    # Cierre limpio
    print("\n Finalizada la prueba. Desconectando...")
    client.loop_stop()
    client.disconnect()
    print(" Desconectado.")

if __name__ == "__main__":
    main()