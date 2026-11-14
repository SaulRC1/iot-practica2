import time
import json
import paho.mqtt.client as mqtt
from config import (
    BROKER_DEFAULT,
    PUERTO_DEFAULT,
    GRUPO_DEFAULT,
    KEEPALIVE_DEFAULT,
    ESTADO_PERSIANA_CERRADA,
    ESTADO_PERSIANA_ABIERTA,
    ESTADO_BOMBILLA_APAGADA,
    ESTADO_BOMBILLA_ENCENDIDA,
    topic_actuador_estado
)

# Estado inicial de los actuadores simulados
estados_actuadores = {
    "bombilla": ESTADO_BOMBILLA_APAGADA,
    "persiana": ESTADO_PERSIANA_CERRADA
}

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Actuador conectado al broker MQTT.")
        # Nos suscribimos a las peticiones de set de cualquier actuador (+)
        topic_suscripcion = f"iotlab26/{GRUPO_DEFAULT}/actuador/+/set"
        client.subscribe(topic_suscripcion, qos=0)
        print(f"Escuchando órdenes en: {topic_suscripcion}")
    else:
        print(f"Error de conexión al broker. Código: {rc}")

def on_message(client, userdata, msg):
    try:
        # El topic es del estilo: iotlab26/gjuan_saul/actuador/bombilla/set
        partes_topic = msg.topic.split("/")
        nombre_actuador = partes_topic[3]  # "bombilla" o "persiana"

        # Decodificar el comando recibido
        payload_recibido = msg.payload.decode("utf-8").strip()
        print(f"\n Orden recibida para [{nombre_actuador}]: '{payload_recibido}'")
        
        # Validar y actualizar según el tipo de actuador
        nuevo_estado = None
        if nombre_actuador == "bombilla":
            comando_upper = payload_recibido.upper()
            if comando_upper in [ESTADO_BOMBILLA_ENCENDIDA, ESTADO_BOMBILLA_APAGADA]:
                nuevo_estado = comando_upper
        elif nombre_actuador == "persiana":
            comando_upper = payload_recibido.upper()
            if comando_upper in [ESTADO_PERSIANA_ABIERTA, ESTADO_PERSIANA_CERRADA]:
                nuevo_estado = comando_upper
                
        if nuevo_estado:
            # Actualizamos el estado interno
            estados_actuadores[nombre_actuador] = nuevo_estado
            print(f"Estado físico cambiado: {nombre_actuador} -> {nuevo_estado}")
            
            # Publicar el nuevo estado confirmado con RETAIN = True
            topic_estado = topic_actuador_estado(nombre_actuador, GRUPO_DEFAULT)
            
            payload_estado = json.dumps({
                "actuador": nombre_actuador,
                "estado": nuevo_estado,
                "timestamp": time.strftime("%H:%M:%S")
            })
            
            client.publish(topic_estado, payload_estado, qos=0, retain=True)
            print(f"Estado publicado (Retained) en: {topic_estado}")
        else:
            print(f"Orden inválida para '{nombre_actuador}': '{payload_recibido}'")
            
    except Exception as e:
        print(f"Error procesando el mensaje recibido: {e}")

def main():
    client_id = f"actuador-central-{GRUPO_DEFAULT}"

    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    except AttributeError:
        client = mqtt.Client(client_id=client_id)

    client.on_connect = on_connect
    client.on_message = on_message

    print(f"Conectando a {BROKER_DEFAULT}:{PUERTO_DEFAULT}...")
    client.connect(BROKER_DEFAULT, PUERTO_DEFAULT, KEEPALIVE_DEFAULT)
    
    # loop_forever mantiene el script escuchando indefinidamente
    print("Iniciando bucle de escucha del actuador. Pulsa Ctrl+C para salir.")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario. Desconectando...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()