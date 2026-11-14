import csv
import paho.mqtt.client as mqtt
import time
import json
import threading
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
        return json.dumps(mensaje, ensure_ascii=False)
    elif tipo_dato == DatoSensorAgrupado:
        return None

def siguiente_indice(indice_actual, indice_max):
    if(indice_actual >= indice_max):
        return 0

    return indice_actual + 1


parar = False

def escuchar_teclado():
    global parar

    input("Pulsa ENTER para detener el programa\n")
    parar = True

def main():
    datos_humedad = leer_datos_csv("datos_humedad.csv", DatoSensorGenerico)
    datos_luz = leer_datos_csv("datos_luz.csv", DatoSensorGenerico)
    datos_presencia = leer_datos_csv("datos_presencia.csv", DatoSensorGenerico)
    datos_temperatura = leer_datos_csv("datos_temperatura.csv", DatoSensorGenerico)
    
    datos_sensores = leer_datos_csv("datos_sensores.csv", DatoSensorAgrupado)
    
    # Creación del cliente (compatible con paho-mqtt v1 y v2)
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"pub-sensores-{GRUPO_DEFAULT}")
    except AttributeError:
        client = mqtt.Client(client_id=f"pub-sensores-{GRUPO_DEFAULT}")

    client.on_connect = on_connect
    client.on_publish = on_publish

    # Conexión al broker
    print(f"Conectando a {BROKER_DEFAULT}...")
    client.connect(BROKER_DEFAULT, PUERTO_DEFAULT, keepalive=KEEPALIVE_DEFAULT)
    client.loop_start()  # Inicia un hilo secundario para gestionar la red

    time.sleep(1)  # Breve pausa para completar el handshake

    indice_humedad = 0
    max_indice_humedad = len(datos_humedad) - 1

    indice_luz = 0
    max_indice_luz = len(datos_luz) - 1

    indice_presencia = 0
    max_indice_presencia = len(datos_presencia) - 1

    indice_temperatura = 0
    max_indice_temperatura = len(datos_temperatura) - 1

    # Iniciar hilo para escuchar teclado y parar el script
    hilo = threading.Thread(target=escuchar_teclado, daemon=True)
    hilo.start()

    while not parar:
        # Obtención de payload de los sensores para publicar en MQTT
        # -------------------------------------------------------------------------------------
        dato_humedad = datos_humedad[indice_humedad]
        payload_humedad = construir_payload_sensor(dato_humedad, DatoSensorGenerico, "humedad")

        dato_luz = datos_luz[indice_luz]
        payload_luz = construir_payload_sensor(dato_luz, DatoSensorGenerico, "luz")

        dato_presencia = datos_presencia[indice_presencia]
        payload_presencia = construir_payload_sensor(dato_presencia, DatoSensorGenerico, "presencia")

        dato_temperatura = datos_temperatura[indice_temperatura]
        payload_temperatura = construir_payload_sensor(dato_temperatura, DatoSensorGenerico, "temperatura")

        # Calcular siguientes indices
        # -------------------------------------------------------------------
        indice_humedad = siguiente_indice(indice_humedad, max_indice_humedad)
        indice_luz = siguiente_indice(indice_luz, max_indice_luz)
        indice_presencia = siguiente_indice(indice_presencia, max_indice_presencia)
        indice_temperatura = siguiente_indice(indice_temperatura, max_indice_temperatura)

        # Publicación de datos de sensores en MQTT
        # --------------------------------------------------------------------------
        info = client.publish(TOPIC_PUB_SENSOR_HUMEDAD, payload_humedad.encode("utf-8"), qos=0)
        info.wait_for_publish()

        info = client.publish(TOPIC_PUB_SENSOR_LUZ, payload_luz.encode("utf-8"), qos=0)
        info.wait_for_publish()

        info = client.publish(TOPIC_PUB_SENSOR_PRESENCIA, payload_presencia.encode("utf-8"), qos=0)
        info.wait_for_publish()

        info = client.publish(TOPIC_PUB_SENSOR_TEMPERATURA, payload_temperatura.encode("utf-8"), qos=0)
        info.wait_for_publish()
                
        time.sleep(2)

    # Cierre limpio
    print("\n Finalizada la prueba. Desconectando...")
    client.loop_stop()
    client.disconnect()
    print(" Desconectado.")


if __name__ == "__main__":
    main()