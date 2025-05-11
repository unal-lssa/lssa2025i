import subprocess
import sys
import time
import argparse
import os
import signal
import psutil
   
# Definir servicios y sus comandos
services = {
    "monitor": {
        "cmd": "python improved_monitor.py",
        "required": True,
        "port": 5006,
        "description": "Sistema de monitoreo"
    },
    "cache": {
        "cmd": "python improved_cache.py",
        "required": True,
        "port": 5004,
        "description": "Servicio de caché"
    },
    "database": {
        "cmd": "python improved_database.py",
        "required": True,
        "port": 5002,
        "description": "Servicio de base de datos"
    },
    "worker": {
        "cmd": "python improved_worker.py",
        "required": True,
        "port": 5005,
        "description": "Servicio de procesamiento asíncrono"
    },
    "microservice": {
        "cmd": "python microservice.py",
        "required": False,
        "port": 5001,
        "description": "Microservicio de lógica de negocio"
    },
    "api_gateway1": {
        "cmd": "python improved_api_gateway.py --port 5000",
        "required": True,
        "port": 5000,
        "description": "API Gateway (instancia 1)"
    },
    "api_gateway2": {
        "cmd": "python improved_api_gateway.py --port 5003",
        "required": True,
        "port": 5003,
        "description": "API Gateway (instancia 2)"
    },
    "api_gateway3": {
        "cmd": "python improved_api_gateway.py --port 5007",
        "required": False,
        "port": 5007,
        "description": "API Gateway (instancia 3)"
    },
    "api_gateway4": {
        "cmd": "python improved_api_gateway.py --port 5008",
        "required": False,
        "port": 5008,
        "description": "API Gateway (instancia 4)"
    },
    "load_balancer": {
        "cmd": "python improved_load_balancer.py",
        "required": True,
        "port": 8000,
        "description": "Balanceador de carga"
    }
}

# Lista para mantener procesos
processes = {}

def is_port_in_use(port):
    """Verificar si un puerto está en uso"""
    for proc in psutil.process_iter(['connections']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port and conn.status in ['LISTEN', 'ESTABLISHED']:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return False

def start_services(selected_services=None, verbose=False):
    """Iniciar los servicios seleccionados"""
    services_to_start = []
    
    # Determinar qué servicios iniciar
    if selected_services:
        # Iniciar solo los servicios especificados
        for svc in selected_services:
            if svc in services:
                services_to_start.append(svc)
            else:
                print(f"Servicio desconocido: {svc}")
    else:
        # Iniciar todos los servicios requeridos
        for svc_name, svc_info in services.items():
            if svc_info["required"]:
                services_to_start.append(svc_name)
    
    print("\nIniciando servicios:")
    print("=" * 40)
    
    # Iniciar servicios en orden
    for svc_name in services_to_start:
        svc_info = services[svc_name]
        port = svc_info["port"]
        
        # Verificar si el puerto ya está en uso
        if is_port_in_use(port):
            print(f"⚠️  {svc_name}: puerto {port} ya está en uso, omitiendo...")
            continue
        
        print(f"🚀 Iniciando {svc_name} ({svc_info['description']}) en puerto {port}...")
        
        try:
            # Abrir nueva ventana de terminal según el sistema operativo
            if sys.platform == "win32":
                # Windows
                process = subprocess.Popen(
                    ["start", "cmd", "/k", svc_info["cmd"]],
                    shell=True
                )
            elif sys.platform == "darwin":
                # macOS
                process = subprocess.Popen([
                    "osascript", "-e",
                    f'tell app "Terminal" to do script "{svc_info["cmd"]}"'
                ])
            else:
                # Linux
                try:
                    # Probar con gnome-terminal
                    process = subprocess.Popen([
                        "gnome-terminal", "--", "bash", "-c", f"{svc_info['cmd']}; exec bash"
                    ])
                except FileNotFoundError:
                    try:
                        # Probar con xterm
                        process = subprocess.Popen([
                            "xterm", "-e", f"{svc_info['cmd']}; bash"
                        ])
                    except FileNotFoundError:
                        # Terminal genérica
                        process = subprocess.Popen(
                            svc_info["cmd"],
                            shell=True
                        )
            
            # Guardar referencia al proceso
            processes[svc_name] = process
            
            if verbose:
                print(f"  Comando: {svc_info['cmd']}")
            
            # Pequeña pausa entre inicios para evitar race conditions
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Error al iniciar {svc_name}: {e}")
    
    print("\nTodos los servicios iniciados correctamente!")
    print("\nAccede al dashboard: http://localhost:5006/dashboard")
    print("Para probar el sistema: http://localhost:8000/status")
    print("\nPresiona Ctrl+C para detener todos los servicios...")

def stop_services():
    """Detener todos los servicios iniciados"""
    print("\nDeteniendo servicios...")
    
    for svc_name, process in processes.items():
        try:
            if sys.platform == "win32":
                # En Windows, necesitamos usar taskkill para terminar procesos cmd
                subprocess.call(f"taskkill /F /T /PID {process.pid}", shell=True)
            else:
                # En Unix, podemos usar kill
                process.terminate()
                process.wait(timeout=5)
            print(f"✓ Servicio {svc_name} detenido")
        except Exception as e:
            print(f"❌ Error al detener {svc_name}: {e}")
            try:
                # Intentar con kill
                if not sys.platform == "win32":
                    os.kill(process.pid, signal.SIGKILL)
            except:
                pass
    
    print("Todos los servicios detenidos.")

def check_services():
    """Verificar estado de todos los servicios"""
    print("\nVerificando servicios...")
    print("=" * 40)
    
    all_running = True
    
    for svc_name, svc_info in services.items():
        port = svc_info["port"]
        
        if is_port_in_use(port):
            print(f"✓ {svc_name}: ACTIVO (puerto {port})")
        else:
            print(f"❌ {svc_name}: INACTIVO (puerto {port})")
            all_running = False
    
    if all_running:
        print("\nTodos los servicios están funcionando correctamente.")
    else:
        print("\nAlgunos servicios no están activos. Use './start_system.py start' para iniciarlos.")
    
    return all_running