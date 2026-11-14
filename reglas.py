import paho.mqtt.client as mqtt
import time
import sys
import json
from config import (
    BROKER_DEFAULT,
    PUERTO_DEFAULT,
    GRUPO_DEFAULT,
    KEEPALIVE_DEFAULT,
    TIPO_SENSOR_TOPIC_HUMEDAD,
    TIPO_SENSOR_TOPIC_LUZ,
    TIPO_SENSOR_TOPIC_PRESENCIA,
    TIPO_SENSOR_TOPIC_TEMPERATURA,
    topic_base,
    topic_sensor,
    UMBRAL_LUZ_BAJA,
    UMBRAL_LUZ_ALTA,
    UMBRAL_HUMEDAD_ALTA,
    UMBRAL_HUMEDAD_BAJA,
)

TOPIC_SENSORES_ALL = f"{topic_base(GRUPO_DEFAULT)}/sensor/#"
TOPIC_ACTUADORES_ESTADO_ALL = f"{topic_base(GRUPO_DEFAULT)}/actuador/+/estado"

TOPIC_PUB_SENSOR_LUZ = topic_sensor(TIPO_SENSOR_TOPIC_LUZ)
TOPIC_PUB_SENSOR_HUMEDAD = topic_sensor(TIPO_SENSOR_TOPIC_HUMEDAD)
TOPIC_PUB_SENSOR_TEMPERATURA = topic_sensor(TIPO_SENSOR_TOPIC_TEMPERATURA)
TOPIC_PUB_SENSOR_PRESENCIA = topic_sensor(TIPO_SENSOR_TOPIC_PRESENCIA)

estado_actual_habitacion = {
    "humedad": 0.0,
    "luz": 0.0,
    "presencia": 0,
    "temperatura": 0.0
}

def procesar_mensaje(topic, payload):
    datos = json.loads(payload)
    global estado_actual_habitacion

    if topic == TOPIC_PUB_SENSOR_HUMEDAD:
        humedad = datos["valor"]

        if humedad > UMBRAL_HUMEDAD_ALTA:
            # abrir persiana
            print("abrir persiana")
        elif (estado_actual_habitacion["luz"] > UMBRAL_LUZ_ALTA and humedad < UMBRAL_HUMEDAD_BAJA):
            # cerrar persiana
            print("cerrar persiana")

        estado_actual_habitacion["humedad"] = humedad
    elif topic == TOPIC_PUB_SENSOR_LUZ:
        presencia_actual = estado_actual_habitacion["presencia"]
        humedad_actual = estado_actual_habitacion["humedad"]
        luz = datos["valor"]

        if (presencia_actual == 1.0 and luz < UMBRAL_LUZ_BAJA):
            print("Encender bombilla")
        elif (luz > UMBRAL_LUZ_ALTA and humedad_actual < UMBRAL_HUMEDAD_BAJA):
            # cerrar persiana
            print("cerrar persiana")

        estado_actual_habitacion["luz"] = luz
    elif topic == TOPIC_PUB_SENSOR_PRESENCIA:
        presencia = datos["valor"]
        presencia_actual = estado_actual_habitacion["presencia"]
        luz_actual = estado_actual_habitacion["luz"]

        if presencia_actual == 0.0 and presencia == 1.0 and luz_actual < UMBRAL_LUZ_BAJA:
            print("Encender bombilla")
        elif presencia_actual == 1.0 and presencia == 0.0:
            print("Apagar bombilla y cerrar persiana")

        estado_actual_habitacion["presencia"] = presencia
    elif topic == TOPIC_PUB_SENSOR_TEMPERATURA:
        temperatura = datos["valor"]
        estado_actual_habitacion["temperatura"] = temperatura

    print("Estado actual de la habitación:")
    print(json.dumps(estado_actual_habitacion, indent=4, ensure_ascii=False))


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Motor de reglas conectado al broker MQTT.")
        client.subscribe(TOPIC_SENSORES_ALL, qos=0)
        print(f"Escuchando órdenes en: {TOPIC_SENSORES_ALL}")
        client.subscribe(TOPIC_ACTUADORES_ESTADO_ALL, qos=0)
        print(f"Escuchando órdenes en: {TOPIC_ACTUADORES_ESTADO_ALL}")
    else:
        print(f"Error de conexión al broker. Código: {rc}")

def on_publish(client, userdata, mid, reason_code=None, properties=None):
    """Callback invocado cuando un mensaje ha sido enviado al broker."""
    print(f"Mensaje {mid} entregado al broker")

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

    procesar_mensaje(topic, payload)

def main():
    # Creación del cliente (compatible con paho-mqtt v1 y v2)
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"motor-reglas-{GRUPO_DEFAULT}")
    except AttributeError:
        client = mqtt.Client(client_id=f"motor-reglas-{GRUPO_DEFAULT}")
    
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_message = on_message
    
    # Conexión al broker
    print(f"Conectando a {BROKER_DEFAULT}...")

    try:
        client.connect(BROKER_DEFAULT, PUERTO_DEFAULT, keepalive=KEEPALIVE_DEFAULT)
            
        time.sleep(1)  # Breve pausa para completar el handshake
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n\n Deteniendo el motor de reglas...")
        client.disconnect()
        print(" Desconectado correctamente.")
        sys.exit(0)

if __name__ == "__main__":
    main()