import csv
import paho.mqtt.client as mqtt

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
            if tipo == DatoSensorAgrupado:
                dato_agrupado = DatoSensorAgrupado(int(fila["paso"]), int(fila["segundo"]), int(fila["luz"]), \
                                float(fila["humedad"]), float(fila["temperatura"]), int(fila["presencia"]), fila["comentario"])
                datos_sensor.append(dato_agrupado)
        
        return datos_sensor



def main():
    datos_humedad = leer_datos_csv("datos_humedad.csv", DatoSensorGenerico)

    for dato in datos_humedad:
        print(dato)

    datos_sensores = leer_datos_csv("datos_sensores.csv", DatoSensorAgrupado)
    
    for dato in datos_sensores:
        print(dato)
    
    # 2. Creación del cliente (compatible con paho-mqtt v1 y v2)
    """try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"pub-intro-{GRUPO}")
    except AttributeError:
        client = mqtt.Client(client_id=f"pub-intro-{GRUPO}")

    client.on_connect = on_connect
    client.on_publish = on_publish

    # 3. Conexión al broker
    print(f"Conectando a {BROKER}...")
    client.connect(BROKER, PUERTO, keepalive=60)
    client.loop_start()  # Inicia un hilo secundario para gestionar la red

    time.sleep(1)  # Breve pausa para completar el handshake

    # 4. Publicar varios mensajes de prueba
    for i in range(1, 6):
        mensaje = {
            "contador": i,
            "texto": f"Hola desde Python (mensaje {i})",
            "timestamp": time.strftime("%H:%M:%S")
        }
        payload_str = json.dumps(mensaje)

        print(f"\n📤 Publicando en '{TOPIC}':")
        print(f"   Payload: {payload_str}")
        
        # client.publish(topic, payload, qos=0, retain=False)
        info = client.publish(TOPIC, payload_str, qos=0)
        info.wait_for_publish()
        
        time.sleep(2)

    # 5. Cierre limpio
    print("\n Finalizada la prueba. Desconectando...")
    client.loop_stop()
    client.disconnect()
    print(" Desconectado.")"""


if __name__ == "__main__":
    main()