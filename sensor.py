import csv
import paho.mqtt.client as mqtt
import time
import json
from config import BROKER_DEFAULT, PUERTO_DEFAULT, GRUPO_DEFAULT, KEEPALIVE_DEFAULT, TIPO_SENSOR_TOPIC_HUMEDAD, TIPO_SENSOR_TOPIC_LUZ, TIPO_SENSOR_TOPIC_PRESENCIA, TIPO_SENSOR_TOPIC_TEMPERATURA, topic_sensor, topic_todo

class DatoSensorGenerico:

    def __init__(self, segundo, valor, unidad):
        self.segundo = segundo
        self.valor = valor
        self.unidad = unidad
    
    def __str__(self):
        return f"Segundo: {self.segundo}, Valor: {self.valor}, Unidad: {self.unidad}"

class DatoSensorAgrupado:

    def __init__(self, paso, segundo, luz, humedad, temperatura, presencia, comentario):
        self.paso = paso
        self.segundo = segundo
        self.luz = luz
        self.humedad = humedad
        self.temperatura = temperatura
        self.presencia = presencia
        self.comentario = comentario
    
    def __str__(self):
        return f"Paso: {self.paso}, Segundo: {self.segundo}, Luz: {self.luz}, Humedad: {self.humedad}, Temperatura: {self.temperatura}, Presencia: {self.presencia}, Comentario: {self.comentario}"

def leer_datos_csv(ruta, tipo):
    with open(ruta, "r", encoding="utf-8") as fichero:
        lector = csv.DictReader(fichero)

        datos_sensor = []

        for fila in lector:
            if tipo == DatoSensorGenerico:
                dato_generico = DatoSensorGenerico(int(fila["segundo"]), float(fila["valor"]), fila["unidad"])
                datos_sensor.append(dato_generico)
            elif tipo == DatoSensorAgrupado:
                dato_agrupado = DatoSensorAgrupado(int(fila["paso"]), int(fila["segundo"]), int(fila["luz"]), \
                                float(fila["humedad"]), float(fila["temperatura"]), int(fila["presencia"]), fila["comentario"])
                datos_sensor.append(dato_agrupado)
        
        return datos_sensor

TOPIC_PUB_SENSOR_LUZ = topic_sensor(TIPO_SENSOR_TOPIC_LUZ)
TOPIC_PUB_SENSOR_HUMEDAD = topic_sensor(TIPO_SENSOR_TOPIC_HUMEDAD)
TOPIC_PUB_SENSOR_TEMPERATURA = topic_sensor(TIPO_SENSOR_TOPIC_TEMPERATURA)
TOPIC_PUB_SENSOR_PRESENCIA = topic_sensor(TIPO_SENSOR_TOPIC_PRESENCIA)

def on_connect(client, userdata, flags, rc, properties=None):
    """Callback invocado cuando el broker responde a nuestra solicitud de conexión."""
    if rc == 0:
        print(" Conectado exitosamente al broker HiveMQ")
    else:
        print(f" Error de conexión con código {rc}")

def on_publish(client, userdata, mid, reason_code=None, properties=None):
    """Callback invocado cuando un mensaje ha sido enviado al broker."""
    print(f" Mensaje {mid} entregado al broker")

def construir_payload_sensor(dato_sensor, tipo_dato, tipo_sensor):
    if tipo_dato == DatoSensorGenerico:
        mensaje = {
                    "sensor": tipo_sensor,
                    "valor": dato_sensor.valor,
                    "unidad": dato_sensor.unidad,
                    "timestamp": time.strftime("%H:%M:%S"),
                    "grupo": GRUPO_DEFAULT
                }
        return json.dumps(mensaje)
    elif tipo_dato == DatoSensorAgrupado:
        return None

def main():
    datos_humedad = leer_datos_csv("datos_humedad.csv", DatoSensorGenerico)

    for dato in datos_humedad:
        print(dato)

    datos_sensores = leer_datos_csv("datos_sensores.csv", DatoSensorAgrupado)
    
    for dato in datos_sensores:
        print(dato)
    
    # 2. Creación del cliente (compatible con paho-mqtt v1 y v2)
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"pub-sensores-{GRUPO_DEFAULT}")
    except AttributeError:
        client = mqtt.Client(client_id=f"pub-sensores-{GRUPO_DEFAULT}")

    client.on_connect = on_connect
    client.on_publish = on_publish

    # 3. Conexión al broker
    print(f"Conectando a {BROKER_DEFAULT}...")
    client.connect(BROKER_DEFAULT, PUERTO_DEFAULT, keepalive=KEEPALIVE_DEFAULT)
    client.loop_start()  # Inicia un hilo secundario para gestionar la red

    time.sleep(1)  # Breve pausa para completar el handshake

    for dato in datos_humedad:
        payload_str = construir_payload_sensor(dato, DatoSensorGenerico, "humedad")

        print(f"\n📤 Publicando en '{TOPIC_PUB_SENSOR_HUMEDAD}':")
        print(f"   Payload: {payload_str}")
        
        # client.publish(topic, payload, qos=0, retain=False)
        info = client.publish(TOPIC_PUB_SENSOR_HUMEDAD, payload_str, qos=0)
        info.wait_for_publish()
        
        time.sleep(2)

    # 5. Cierre limpio
    print("\n Finalizada la prueba. Desconectando...")
    client.loop_stop()
    client.disconnect()
    print(" Desconectado.")


if __name__ == "__main__":
    main()