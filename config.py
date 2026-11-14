"""Configuración central para la Práctica 2 de IoT (MQTT Simple).
Define los parámetros de conexión al broker HiveMQ, los umbrales de las
reglas domóticas y los generadores de topics MQTT.
"""

# ---- BROKER MQTT ----
BROKER_DEFAULT = "broker.hivemq.com"
PUERTO_DEFAULT = 1883
KEEPALIVE_DEFAULT = 60

# Grupo por defecto si no se pasa por argumento
GRUPO_DEFAULT = "gjuan_saul"

# ---- UMBRALES DE LAS REGLAS DOMÓTICAS ----
# R1: Entra persona y luz < UMBRAL_LUZ_BAJA -> Encender Bombilla
# R2: Sale persona -> Apagar Bombilla y Cerrar Persiana
# R3: Humedad > UMBRAL_HUMEDAD_ALTA -> Abrir Persiana (ventilación)
# R4: Luz > UMBRAL_LUZ_ALTA y Humedad < UMBRAL_HUMEDAD_BAJA -> Cerrar Persiana (protección solar)
# R5: Luz < UMBRAL_LUZ_BAJA -> Encender Bombilla
UMBRAL_LUZ_BAJA = 150.0      # lux
UMBRAL_LUZ_ALTA = 600.0      # lux
UMBRAL_HUMEDAD_ALTA = 70.0   # %
UMBRAL_HUMEDAD_BAJA = 40.0   # %

# --------- TIPOS DE TOPICS DE SENSORES --------- #
TIPO_SENSOR_TOPIC_LUZ = "luz"
TIPO_SENSOR_TOPIC_HUMEDAD = "humedad"
TIPO_SENSOR_TOPIC_TEMPERATURA = "temperatura"
TIPO_SENSOR_TOPIC_PRESENCIA = "presencia"

# ---- GENERADORES DE TOPICS MQTT ----
def topic_base(grupo=GRUPO_DEFAULT):
    """Devuelve el prefijo raíz para el grupo."""
    return f"iotlab26/{grupo}"

def topic_sensor(tipo, grupo=GRUPO_DEFAULT):
    """Topic para la telemetría de un sensor: luz, humedad, temperatura, presencia."""
    return f"{topic_base(grupo)}/sensor/{tipo}"

def topic_actuador_set(nombre, grupo=GRUPO_DEFAULT):
    """Topic para enviar órdenes a un actuador: bombilla, persiana."""
    return f"{topic_base(grupo)}/actuador/{nombre}/set"

def topic_actuador_estado(nombre, grupo=GRUPO_DEFAULT):
    """Topic donde el actuador publica su estado confirmado (con Retain)."""
    return f"{topic_base(grupo)}/actuador/{nombre}/estado"

def topic_reglas(grupo=GRUPO_DEFAULT):
    """Topic para auditoría de reglas activadas por el motor."""
    return f"{topic_base(grupo)}/sistema/regla"

def topic_todo(grupo=GRUPO_DEFAULT):
    """Topic comodín para suscribirse a toda la actividad del grupo."""
    return f"{topic_base(grupo)}/#"
