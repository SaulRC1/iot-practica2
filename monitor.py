#!/usr/bin/env python3
"""Visor y Monitor de Eventos MQTT en Tiempo Real (Versión ALUMNO).
Objetivo:
1. Suscribirse a la raíz del grupo iotlab26/<grupo>/# (TODO 1).
2. Procesar y clasificar los mensajes recibidos según su topic (TODO 2):
   - Sensores (/sensor/)
   - Órdenes a actuadores (/actuador/.../set)
   - Estados de actuadores (/actuador/.../estado)
   - Reglas activadas (/sistema/regla)
"""

import sys
import time
import json
import paho.mqtt.client as mqtt

from config import BROKER_DEFAULT, PUERTO_DEFAULT, GRUPO_DEFAULT, topic_todo

GRUPO = sys.argv[1] if len(sys.argv) > 1 else GRUPO_DEFAULT

# Estado en memoria de la habitación para el resumen
estado_resumen = {
    "luz": "--",
    "humedad": "--",
    "temperatura": "--",
    "presencia": "--",
    "bombilla": "--",
    "persiana": "--",
    "ultima_regla": "Ninguna",
    "ultimo_cambio": "--"
}

def imprimir_resumen_habitacion():
    pres_str = "🚶 SÍ (1)" if estado_resumen["presencia"] == 1 else ("🚪 NO (0)" if estado_resumen["presencia"] == 0 else "--")
    print("\n" + "┌" + "─" * 68 + "┐")
    print(f"│ 🏠 ESTADO DE LA HABITACIÓN INTELIGENTE (Grupo: {GRUPO:<6})  Hora: {time.strftime('%H:%M:%S'):<8} │")
    print("├" + "─" * 68 + "┤")
    print(f"│ 💡 Luz: {str(estado_resumen['luz']):<10} | 💧 Humedad: {str(estado_resumen['humedad']):<8} | 🌡️ Temp: {str(estado_resumen['temperatura']):<12} │")
    print(f"│ 👤 Presencia: {pres_str:<8} | 💡 Bombilla: {str(estado_resumen['bombilla']):<6} | 🪟 Persiana: {str(estado_resumen['persiana']):<10} │")
    print(f"│ 🎯 Última Regla: {estado_resumen['ultima_regla'][:48]:<48} │")
    print("└" + "─" * 68 + "┘\n")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        # --- INICIO TODO 1 (Alumno): Suscribirse a todo el tráfico del grupo ---
        topic = topic_todo(GRUPO)  # 'iotlab26/<grupo>/#'
        print("✔ Monitor conectado exitosamente a HiveMQ")
        print(f"📡 Escuchando toda la actividad en: {topic}\n")
        client.subscribe(topic, qos=0)
        # --- FIN TODO 1 ---
    else:
        print(f"❌ Error de conexión al broker. Código rc={rc}")

def on_message(client, userdata, msg):
    """TODO 2: Filtrar y formatear eventos según el topic de procedencia."""
    global estado_resumen
    topic = msg.topic
    payload_str = msg.payload.decode("utf-8", errors="replace")
    ahora = time.strftime("%H:%M:%S")

    # --- INICIO TODO 2 (Alumno): Clasificación de eventos ---
    # 1. Sensores: iotlab26/<grupo>/sensor/<tipo>
    if "/sensor/" in topic and not topic.endswith("/lwt"):
        tipo_sensor = topic.split("/")[-1]
        try:
            if payload_str.startswith("{"):
                datos = json.loads(payload_str)
                valor = datos.get("valor", "--")
                unidad = datos.get("unidad", "")
            else:
                valor = payload_str
                unidad = ""

            estado_resumen[tipo_sensor] = f"{valor} {unidad}".strip()
            if tipo_sensor == "presencia":
                estado_resumen["presencia"] = int(float(valor))

            iconos = {"luz": "💡", "humedad": "💧", "temperatura": "🌡️", "presencia": "🚶"}
            icono = iconos.get(tipo_sensor, "📡")
            print(f"[{ahora}] {icono} [SENSOR]   {tipo_sensor.upper():<12} = {valor} {unidad}")
        except Exception:
            print(f"[{ahora}] 📡 [SENSOR]   {topic}: {payload_str}")

    # 2. Órdenes a Actuadores: .../actuador/<tipo>/set
    elif "/actuador/" in topic and topic.endswith("/set"):
        tipo_act = topic.split("/")[-2]
        print(f"[{ahora}] ⚡ [ORDEN ACT] {tipo_act.upper():<12} ➜ {payload_str}")

    # 3. Estado Confirmado: .../actuador/<tipo>/estado
    elif "/actuador/" in topic and topic.endswith("/estado"):
        tipo_act = topic.split("/")[-2]
        try:
            if payload_str.startswith("{"):
                datos = json.loads(payload_str)
                estado = datos.get("estado", "--")
                origen = datos.get("origen", "MQTT")
            else:
                estado = payload_str
                origen = "RAW"

            estado_resumen[tipo_act] = estado
            ret = " [RETENIDO]" if msg.retain else ""
            print(f"[{ahora}] ⚙️ [ESTADO ACT] {tipo_act.upper():<12} = {estado} (Origen: {origen}){ret}")
            imprimir_resumen_habitacion()
        except Exception:
            print(f"[{ahora}] ⚙️ [ESTADO ACT] {tipo_act.upper()}: {payload_str}")

    # 4. Reglas del Sistema: .../sistema/regla
    elif "/sistema/regla" in topic:
        try:
            if payload_str.startswith("{"):
                datos = json.loads(payload_str)
                regla = datos.get("regla", payload_str)
            else:
                regla = payload_str
            estado_resumen["ultima_regla"] = regla
            print(f"\n[{ahora}] 🎯 [REGLA ACTIVADA] {regla}\n")
        except Exception:
            print(f"[{ahora}] 🎯 [REGLA]: {payload_str}")
    # --- FIN TODO 2 ---

def main():
    print("=" * 70)
    print(f"🖥️ MONITOR Y VISOR DE EVENTOS MQTT (Alumno - Grupo: {GRUPO})")
    print("=" * 70)
    print(f"• Broker:  {BROKER_DEFAULT}:{PUERTO_DEFAULT}")
    print(f"• Filtro:  {topic_todo(GRUPO)}")
    print("• Pulse Ctrl+C para finalizar.")
    print("-" * 70)

    imprimir_resumen_habitacion()

    client_id = f"monitor-{GRUPO}-{int(time.time())}"
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id)
    except AttributeError:
        client = mqtt.Client(client_id=client_id)

    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER_DEFAULT, PUERTO_DEFAULT, keepalive=60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo monitor...")
        client.disconnect()
        print("✔ Monitor cerrado.\n")

if __name__ == "__main__":
    main()

