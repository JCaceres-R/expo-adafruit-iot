# main.py - Raspberry Pi Pico W con umqtt.simple
import network
import time
import random
from umqtt.simple import MQTTClient
from secrets import secrets  # Archivo con tus credenciales

# --- CONFIGURACIÓN DE FEEDS ---
FEED_TEMP = "taller-temperatura"
FEED_HUM = "taller-humedad"
FEED_PRES = "taller-presion"

# --- FUNCIÓN DE CONEXIÓN WIFI ---
def wifi_connect():
    print("Conectando a WiFi...", end="")
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets['ssid'], secrets['password'])
    
    timeout = 0
    while not wlan.isconnected() and timeout < 20:
        print(".", end="")
        time.sleep(1)
        timeout += 1
    
    if wlan.isconnected():
        print(" ¡Conectado!")
        print("IP:", wlan.ifconfig()[0])
        return True
    else:
        print(" Error al conectar WiFi")
        return False

# --- CALLBACK PARA MENSAJES RECIBIDOS (OPCIONAL) ---
def mensaje_recibido(topic, msg):
    print(f"Mensaje en {topic.decode()}: {msg.decode()}")

# --- INICIAR CONEXIÓN WIFI ---
if not wifi_connect():
    print("No se pudo conectar al WiFi. Reiniciando...")
    time.sleep(5)
    import machine
    machine.reset()

# --- CONFIGURAR CLIENTE MQTT ---
# Formato de tópicos para Adafruit IO
feed_temp_mqtt = f"{secrets['aio_username']}/feeds/{FEED_TEMP}"
feed_hum_mqtt = f"{secrets['aio_username']}/feeds/{FEED_HUM}"
feed_pres_mqtt = f"{secrets['aio_username']}/feeds/{FEED_PRES}"

# Crear cliente MQTT
mqtt_client = MQTTClient(
    client_id=secrets['aio_username'],  # ID único del cliente
    server="io.adafruit.com",           # Servidor de Adafruit IO
    port=1883,                          # Puerto MQTT estándar
    user=secrets['aio_username'],       # Tu username de Adafruit IO
    password=secrets['aio_key'],        # Tu AIO Key
    keepalive=60                        # Mantener conexión viva
)

# Asignar callback (opcional, para recibir mensajes)
mqtt_client.set_callback(mensaje_recibido)

# --- CONECTAR A ADAFRUIT IO ---
print(f"Conectando a Adafruit IO como {secrets['aio_username']}...")
try:
    mqtt_client.connect()
    print("¡Conectado a Adafruit IO!")
except Exception as e:
    print(f"Error al conectar a Adafruit IO: {e}")
    print("Reiniciando en 5 segundos...")
    time.sleep(5)
    import machine
    machine.reset()

# --- BUCLE PRINCIPAL ---
print("Enviando datos de la 'Estación Meteorológica' cada 10 segundos...")
print("Presiona Ctrl+C para detener\n")

contador = 0
try:
    while True:
        try:
            # 1. Simular los 3 valores
            temp = round(random.uniform(20.0, 30.0), 2)
            hum = round(random.uniform(40.0, 60.0), 2)
            pres = round(random.uniform(950.0, 1050.0), 2)
            
            contador += 1
            print(f"[{contador}] Enviando: Temp={temp}°C, Hum={hum}%, Pres={pres} hPa")
            
            # 2. Publicar (enviar) los 3 valores a Adafruit IO
            # umqtt.simple requiere que los valores sean strings
            mqtt_client.publish(feed_temp_mqtt, str(temp))
            mqtt_client.publish(feed_hum_mqtt, str(hum))
            mqtt_client.publish(feed_pres_mqtt, str(pres))
            
            print("    ✓ Datos enviados correctamente\n")
            
            # 3. Verificar si hay mensajes (para mantener conexión viva)
            mqtt_client.check_msg()
            
            # 4. Esperar 10 segundos
            time.sleep(10)
            
        except OSError as e:
            # Error de conexión MQTT
            print(f"Error de conexión MQTT: {e}")
            print("Reintentando conexión...")
            
            try:
                mqtt_client.disconnect()
            except:
                pass
            
            # Verificar WiFi
            wlan = network.WLAN(network.STA_IF)
            if not wlan.isconnected():
                print("WiFi desconectado, reconectando...")
                wifi_connect()
            
            # Reconectar MQTT
            time.sleep(2)
            mqtt_client.connect()
            print("Reconectado a Adafruit IO")
            
        except Exception as e:
            print(f"Error inesperado: {e}")
            time.sleep(5)

except KeyboardInterrupt:
    print("\n\nPrograma detenido por el usuario")
    mqtt_client.disconnect()
    print("Desconectado de Adafruit IO")