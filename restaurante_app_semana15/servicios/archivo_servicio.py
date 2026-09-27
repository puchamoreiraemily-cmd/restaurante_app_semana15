import json
import os

class ArchivoServicio:
    @staticmethod
    def cargar_json(ruta_archivo: str) -> list:
        if not os.path.exists(ruta_archivo):
            return []
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                return json.load(archivo)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    @staticmethod
    def guardar_json(ruta_archivo: str, datos: list) -> bool:
        try:
            os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar datos en {ruta_archivo}: {e}")
            return False