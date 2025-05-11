import requests
import threading
import time
import random
import json
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor

class LoadTester:
    def __init__(self, host="http://127.0.0.1:8000", token=None):
        self.host = host
        self.token = token
        self.results = {
            "requests": 0,
            "success": 0,
            "errors": 0,
            "response_times": [],
        }
        self.running = False
        self.lock = threading.Lock()
        
    def get_token(self):
        """Obtener un token de autenticación si no se proporcionó uno"""
        try:
            response = requests.post(
                f"{self.host.replace('8000', '5000')}/token", 
                json={"username": "test_user"}
            )
            if response.status_code == 200:
                return response.json().get("token")
        except Exception as e:
            print(f"Error al obtener token: {e}")
        return None
    
    def make_request(self, endpoint, method="GET", data=None):
        """Realizar una solicitud y registrar el resultado"""
        headers = {}
        if self.token:
            headers["Authorization"] = self.token
            
        url = f"{self.host}/{endpoint}"
        start_time = time.time()
        success = False
            
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
                
            success = 200 <= response.status_code < 300
            
            # Registrar tiempo de respuesta en milisegundos
            response_time = (time.time() - start_time) * 1000
            
            with self.lock:
                self.results["requests"] += 1
                if success:
                    self.results["success"] += 1
                else:
                    self.results["errors"] += 1
                self.results["response_times"].append(response_time)
            
            return {
                "success": success,
                "status_code": response.status_code,
                "response_time": response_time,
                "data": response.json() if success else None
            }
            
        except Exception as e:
            with self.lock:
                self.results["requests"] += 1
                self.results["errors"] += 1
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def data_endpoint_test(self):
        """Test para el endpoint /data"""
        return self.make_request("data")
    
    def long_task_test(self):
        """Test para el endpoint /longtask"""
        task_types = ["report", "notification", "default"]
        task_type = random.choice(task_types)
        
        data = {
            "type": task_type,
            "parameters": {
                "priority": random.choice(["high", "medium", "low"]),
                "timestamp": time.time()
            }
        }
        
        return self.make_request("longtask", method="POST", data=data)
    
    def run_test(self, test_type, num_requests, concurrency):
        """Ejecutar prueba con concurrencia específica"""
        self.running = True
        self.results = {
            "test_type": test_type,
            "requests": 0,
            "success": 0, 
            "errors": 0,
            "response_times": [],
            "start_time": time.time(),
            "end_time": None
        }
        
        print(f"Iniciando prueba de carga: {test_type} con {num_requests} solicitudes y {concurrency} conexiones concurrentes")
        
        # Seleccionar la función de test adecuada
        if test_type == "data":
            test_func = self.data_endpoint_test
        elif test_type == "longtask":
            test_func = self.long_task_test
        else:
            print(f"Tipo de prueba desconocido: {test_type}")
            return
        
        # Ejecutar pruebas con un pool de threads
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = [executor.submit(test_func) for _ in range(num_requests)]
            
            # Esperar a que terminen las pruebas
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    print(f"Error en ejecución de prueba: {e}")
        
        self.running = False
        self.results["end_time"] = time.time()
        
        # Calcular estadísticas
        self.calculate_stats()
        self.print_results()
        
    def calculate_stats(self):
        """Calcular estadísticas basadas en los resultados"""
        # Duración total en segundos
        duration = self.results["end_time"] - self.results["start_time"]
        
        # Estadísticas para agregar
        stats = {
            "duration_seconds": duration,
            "requests_per_second": self.results["requests"] / duration if duration > 0 else 0,
            "success_rate": (self.results["success"] / self.results["requests"]) * 100 if self.results["requests"] > 0 else 0,
            "avg_response_time": sum(self.results["response_times"]) / len(self.results["response_times"]) if self.results["response_times"] else 0,
        }
        
        # Agregar percentiles si hay datos
        if self.results["response_times"]:
            sorted_times = sorted(self.results["response_times"])
            stats["min_response_time"] = sorted_times[0]
            stats["max_response_time"] = sorted_times[-1]
            stats["median_response_time"] = sorted_times[len(sorted_times) // 2]
            stats["p95_response_time"] = sorted_times[int(len(sorted_times) * 0.95)]
            stats["p99_response_time"] = sorted_times[int(len(sorted_times) * 0.99)]
        
        # Agregar estadísticas al resultado
        self.results.update(stats)
    
    def print_results(self):
        """Imprimir resultados de forma legible"""
        print("\n" + "="*50)
        print(f"RESULTADOS DE LA PRUEBA: {self.results['test_type']}")
        print("="*50)
        print(f"Total de solicitudes: {self.results['requests']}")
        print(f"Solicitudes exitosas: {self.results['success']} ({self.results['success_rate']:.2f}%)")
        print(f"Errores: {self.results['errors']}")
        print(f"Duración: {self.results['duration_seconds']:.2f} segundos")
        print(f"Solicitudes por segundo: {self.results['requests_per_second']:.2f}")
        print(f"Tiempo promedio de respuesta: {self.results['avg_response_time']:.2f} ms")
        
        if "min_response_time" in self.results:
            print("\nTiempos de respuesta (ms):")
            print(f"  Min: {self.results['min_response_time']:.2f}")
            print(f"  Mediana: {self.results['median_response_time']:.2f}")
            print(f"  95p: {self.results['p95_response_time']:.2f}")
            print(f"  99p: {self.results['p99_response_time']:.2f}")
            print(f"  Max: {self.results['max_response_time']:.2f}")
        
        print("="*50 + "\n")
    
    def save_results(self, filename):
        """Guardar resultados en archivo JSON"""
        # Reducir el tamaño de los datos de respuesta para el archivo
        results_copy = self.results.copy()
        
        # Limitar los tiempos de respuesta individuales
        if len(results_copy["response_times"]) > 100:
            # Tomar 100 muestras aleatorias
            results_copy["response_times"] = random.sample(results_copy["response_times"], 100)
        
        with open(filename, 'w') as f:
            json.dump(results_copy, f, indent=2)
            
        print(f"Resultados guardados en {filename}")

def main():
    parser = argparse.ArgumentParser(description="Herramienta de pruebas de carga para arquitectura escalable")
    parser.add_argument("test_type", choices=["data", "longtask"], help="Tipo de prueba a ejecutar")
    parser.add_argument("--requests", type=int, default=100, help="Número total de solicitudes")
    parser.add_argument("--concurrency", type=int, default=10, help="Número de conexiones concurrentes")
    parser.add_argument("--host", default="http://127.0.0.1:8000", help="Host base para las pruebas")
    parser.add_argument("--token", help="Token de autenticación (opcional)")
    parser.add_argument("--output", help="Archivo de salida para resultados (opcional)")
    
    args = parser.parse_args()
    
    # Crear y configurar el tester
    tester = LoadTester(host=args.host, token=args.token)
    
    # Obtener token si no se proporcionó
    if not tester.token:
        print("Obteniendo token de autenticación...")
        tester.token = tester.get_token()
        
        if not tester.token:
            print("No se pudo obtener un token. Asegúrate de que el API Gateway esté en funcionamiento.")
            sys.exit(1)
    
    # Ejecutar la prueba
    tester.run_test(args.test_type, args.requests, args.concurrency)
    
    # Guardar resultados si se especificó un archivo
    if args.output:
        tester.save_results(args.output)

if __name__ == "__main__":
    main()