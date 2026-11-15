#!/usr/bin/env python3
"""Lanzador Conjunto Todo-en-Uno para la Práctica 2 IoT (MQTT Simple).
Permite ejecutar en un solo comando todos los módulos de la habitación inteligente:
  • Monitor de Eventos en tiempo real
  • Actuador Bombilla
  • Actuador Persiana
  • Motor de Reglas
  • 4 Sensores Virtuales (Luz, Humedad, Temperatura, Presencia) con datos CSV

Uso:
  python lanzar_todo.py [grupo] [--periodo S] [--sin-monitor]
  Ejemplo: python lanzar_todo.py g01
"""

import os
import sys
import time
import signal
import argparse
import subprocess
from config import (
    GRUPO_DEFAULT,
    MODO_EJECUCION_SENSORES_SEPARADOS,
    MODO_EJECUCION_SENSORES_AGRUPADOS
)

DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))

def parse_args():
    parser = argparse.ArgumentParser(description="Lanzador conjunto del sistema IoT de la Práctica 2")
    parser.add_argument("grupo", nargs="?", default=GRUPO_DEFAULT,
                        help=f"Identificador de grupo (por defecto '{GRUPO_DEFAULT}')")
    parser.add_argument("--periodo", type=float, default=2.0,
                        help="Periodo de publicación de los sensores en segundos (por defecto 2.0)")
    parser.add_argument("--sin-monitor", action="store_true",
                        help="No iniciar el monitor integrado (útil si se abre en otra ventana)")
    parser.add_argument("--solo-servicios", action="store_true",
                        help="Iniciar solo actuadores y reglas (los sensores los arrancan los alumnos)")
    parser.add_argument("--modo-sensores", choices=[MODO_EJECUCION_SENSORES_SEPARADOS, MODO_EJECUCION_SENSORES_AGRUPADOS],
                        default=MODO_EJECUCION_SENSORES_SEPARADOS,
                        help=f"Modo de ejecución de los sensores ('{MODO_EJECUCION_SENSORES_SEPARADOS}' o '{MODO_EJECUCION_SENSORES_AGRUPADOS}')")
    return parser.parse_args()

def main():
    args = parse_args()
    grupo = args.grupo
    periodo = str(args.periodo)
    python_exe = sys.executable

    print("=" * 72)
    print(f"🚀 INICIANDO SISTEMA COMPLETO IoT (MQTT Simple) · GRUPO: {grupo.upper()}")
    print("=" * 72)
    print(f"• Intérprete Python: {python_exe}")
    print(f"• Directorio base:   {DIR_ACTUAL}")
    print(f"• Periodo sensores:  {periodo} s")
    print("-" * 72)

    procesos = []

    def lanzar(comando, nombre, mostrar_salida=False):
        print(f"▶ Lanzando {nombre}...")
        if mostrar_salida:
            p = subprocess.Popen(comando, cwd=DIR_ACTUAL)
        else:
            p = subprocess.Popen(
            comando,
            cwd=DIR_ACTUAL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        procesos.append((nombre, p))
        time.sleep(0.8)

    try:
        # 1. Monitor de eventos (si no se excluye)
        if not args.sin_monitor:
            lanzar([python_exe, "-u","monitor.py", grupo], "Monitor de Eventos", mostrar_salida=True)

        # 2. Actuadores
        lanzar([python_exe, "actuador.py", "--tipo", "bombilla", "--grupo", grupo], "Actuador Bombilla")
        lanzar([python_exe, "actuador.py", "--tipo", "persiana", "--grupo", grupo], "Actuador Persiana")

        # 3. Motor de Reglas
        lanzar([python_exe, "reglas.py", grupo], "Motor de Reglas")

        # 4. Sensores (si no es modo solo-servicios)
        if not args.solo_servicios:
            if args.modo_sensores == MODO_EJECUCION_SENSORES_SEPARADOS:
                sensores = ["luz", "humedad", "temperatura", "presencia"]
                for s in sensores:
                    lanzar([python_exe, "sensor.py", "--tipo", s, "--grupo", grupo, "--periodo", periodo],
                        f"Sensor {s.capitalize()}")
            elif args.modo_sensores == MODO_EJECUCION_SENSORES_AGRUPADOS:
                lanzar([python_exe, "sensor.py", "--modo", MODO_EJECUCION_SENSORES_AGRUPADOS],"Sensores Agrupados")
                
        print("\n" + "=" * 72)
        print("✅ ¡TODOS LOS MÓDULOS ESTÁN EN EJECUCIÓN Y CONECTADOS A HIVEMQ!")
        print("=" * 72)
        print("💡 Para interactuar con los actuadores manualmente o ver logs aislados,")
        print("   puedes abrir otra terminal y ejecutar:")
        print(f"   • python actuador_bombilla.py {grupo}")
        print(f"   • python monitor.py {grupo}")
        print("\n🛑 Presiona Ctrl+C en esta terminal para detener todo el sistema limpiamente.")
        print("=" * 72 + "\n")

        while True:
            # Comprobar si algún proceso ha terminado inesperadamente
            for nombre, p in procesos:
                codigo = p.poll()
                if codigo is not None:
                    # El proceso terminó
                    pass
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 Solicitud de parada recibida. Cerrando todos los procesos...")
        for nombre, p in reversed(procesos):
            try:
                print(f"   • Deteniendo {nombre}...")
                p.terminate()
            except Exception:
                pass
        
        # Esperar 2 segundos y forzar kill si no han salido
        time.sleep(1.5)
        for nombre, p in procesos:
            if p.poll() is None:
                try:
                    p.kill()
                except Exception:
                    pass

        print("✔ Todos los módulos se han detenido correctamente. ¡Hasta pronto!\n")

if __name__ == "__main__":
    main()
