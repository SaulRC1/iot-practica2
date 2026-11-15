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
        print(" Nodo sensor conectado exitosamente al broker MQTT.")
        
        # Topic donde publicaremos nuestro estado de presencia
        topic_estado_nodo = f"iotlab26/{GRUPO_DEFAULT}/sensor/presencia"
        
        # Publicamos que ahora estamos ONLINE (con retain=True para que quede constancia)
        payload_online = json.dumps({
            "estado": "ONLINE",
            "timestamp": time.strftime("%H:%M:%S")
        })
        client.publish(topic_estado_nodo, payload_online, qos=1, retain=True)
        print(f" Estado publicado en '{topic_estado_nodo}': ONLINE")
    else:
        print(f" Error de conexión al broker. Código: {rc}")

def main():
    client_id = f"nodo-lwt-{GRUPO_DEFAULT}"

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    except AttributeError:
        client = mqtt.Client(client_id=client_id)

    client.user_data_set({"grupo": GRUPO_DEFAULT})
    client.on_connect = on_connect

    # ---- CONFIGURACIÓN DEL LAST WILL AND TESTAMENT (LWT) ----
    # Definimos el topic de testamento para este sensor
    topic_lwt = f"iotlab26/{GRUPO_DEFAULT}/sensor/presencia"
    
    # El mensaje que el broker publicará automáticamente si este cliente cae por sorpresa
    payload_lwt = json.dumps({
        "estado": "OFFLINE",
        "motivo": "Caida abrupta de tension o perdida de red",
        "timestamp": time.strftime("%H:%M:%S")
    })
    
    # Configuramos el Will antes de hacer el connect()
    client.will_set(topic_lwt, payload=payload_lwt, qos=1, retain=True)
    print(" Testamento (LWT) configurado correctamente en el cliente.")
    # ---------------------------------------------------------

    print(f"Conectando a {BROKER_DEFAULT}:{PUERTO_DEFAULT} para el grupo '{GRUPO_DEFAULT}'...")
    client.connect(BROKER_DEFAULT, PUERTO_DEFAULT, keepalive=KEEPALIVE_DEFAULT)
    client.loop_start()

    time.sleep(2)  # Pausa para ver la conexión y el mensaje ONLINE

    print("\n" + "="*55)
    print("   SIMULACIÓN DE NODO ACTIVO CON LWT CONFIGURADO   ")
    print("="*55)
    print("El nodo está funcionando y publicando su estado.")
    print("  Para probar la caída abrupta:")
    print("    1. Ten tu 'suscriptor_test.py' escuchando en otra terminal.")
    print("    2. Cierra esta ventana o mata el proceso de golpe (Ctrl+Z o cerrando la terminal).")
    print("    3. Verás cómo el broker publica automáticamente el mensaje OFFLINE.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n Nodo cerrado de forma controlada.")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()