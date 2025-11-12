# main.py - Raspberry Pi Pico W con LEDs simples y Color Picker indicador
import network
import time
import random
from machine import Pin
from umqtt.simple import MQTTClient
from secrets import secrets  # Archivo con tus credenciales

# --- CONFIGURACIÓN DE PINES DE LEDs SIMPLES ---
LED_FRIO = Pin(15, Pin.OUT)    # LED Azul - Temperatura baja
LED_NORMAL = Pin(14, Pin.OUT)  # LED Verde - Temperatura normal
LED_CALOR = Pin(13, Pin.OUT)   # LED Rojo - Temperatura alta

# --- RANGOS DE TEMPERATURA ---
TEMP_BAJA = 23.0      # Por debajo de esto: LED azul (frío)
TEMP_ALTA = 27.0      # Por encima de esto: LED rojo (calor)
                      # Entre ambos: LED verde (normal)

# --- CONFIGURACIÓN DE FEEDS ---
FEED_TEMP = "taller-temperatura"
FEED_HUM = "taller-humedad"
FEED_PRES = "taller-presion"
FEED_COLOR = "taller-color"  # NUEVO: Feed para mostrar color según temperatura

# --- FUNCIÓN PARA OBTENER COLOR HEX SEGÚN TEMPERATURA ---
def temperatura_a_color_hex(temperatura):
    """
    Convierte la temperatura a un color hexadecimal:
    - Frío (< 23°C): Azul (#00ACEC)
    - Normal (23-27°C): Verde (#00FF00)
    - Calor (> 27°C): Rojo (#FF0000)
    
    También puede generar gradientes intermedios
    """
    if temperatura < TEMP_BAJA:
        # Azul para frío
        return "#00ACEC"
    elif temperatura > TEMP_ALTA:
        # Rojo para calor
        return "#FF0000"
    else:
        # Verde para normal
        return "#00FF00"

# --- FUNCIÓN ALTERNATIVA: GRADIENTE SUAVE DE COLORES ---
def temperatura_a_gradiente(temperatura, temp_min=20.0, temp_max=30.0):
    """
    Crea un gradiente de color desde azul (frío) hasta rojo (caliente)
    pasando por verde en el medio
    """
    # Normalizar temperatura entre 0 y 1
    temp_norm = (temperatura - temp_min) / (temp_max - temp_min)
    temp_norm = max(0.0, min(1.0, temp_norm))  # Limitar entre 0 y 1
    
    if temp_norm < 0.5:
        # De azul a verde (primera mitad)
        factor = temp_norm * 2  # 0 a 1
        r = 0
        g = int(255 * factor)
        b = int(255 * (1 - factor))
    else:
        # De verde a rojo (segunda mitad)
        factor = (temp_norm - 0.5) * 2  # 0 a 1
        r = int(255 * factor)
        g = int(255 * (1 - factor))
        b = 0
    
    # Convertir a hexadecimal
    return "#{:02X}{:02X}{:02X}".format(r, g, b)

# --- FUNCIÓN PARA CONTROLAR LEDs SEGÚN TEMPERATURA ---
def actualizar_leds(temperatura):
    """
    Enciende el LED correspondiente según el rango de temperatura
    """
    # Apagar todos los LEDs primero
    LED_FRIO.off()
    LED_NORMAL.off()
    LED_CALOR.off()
    
    # Encender el LED apropiado
    if temperatura < TEMP_BAJA:
        LED_FRIO.on()
        return "🔵 FRÍO"
    elif temperatura > TEMP_ALTA:
        LED_CALOR.on()
        return "🔴 CALOR"
    else:
        LED_NORMAL.on()
        return "🟢 NORMAL"

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

# --- SECUENCIA DE INICIO DE LEDs ---
print("=== Sistema de Monitoreo con Indicador Visual ===")
print("Probando LEDs...")
LED_FRIO.on()
time.sleep(0.3)
LED_NORMAL.on()
time.sleep(0.3)
LED_CALOR.on()
time.sleep(0.3)
LED_FRIO.off()
LED_NORMAL.off()
LED_CALOR.off()
print("✓ LEDs funcionando\n")

print(f"Rangos de temperatura:")
print(f"  🔵 Frío:   < {TEMP_BAJA}°C")
print(f"  🟢 Normal: {TEMP_BAJA}°C - {TEMP_ALTA}°C")
print(f"  🔴 Calor:  > {TEMP_ALTA}°C")
print(f"\n💡 El Color Picker del dashboard cambiará según la temperatura\n")

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
feed_color_mqtt = f"{secrets['aio_username']}/feeds/{FEED_COLOR}"

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
print("\nEnviando datos y actualizando color cada 10 segundos...")
print("Presiona Ctrl+C para detener\n")

contador = 0
USE_GRADIENTE = True  # Cambiar a False para usar colores fijos (azul/verde/rojo)

try:
    while True:
        try:
            # 1. Simular los 3 valores
            temp = round(random.uniform(20.0, 30.0), 2)
            hum = round(random.uniform(40.0, 60.0), 2)
            pres = round(random.uniform(950.0, 1050.0), 2)
            
            # 2. Actualizar LEDs según temperatura
            estado_temp = actualizar_leds(temp)
            
            # 3. Calcular color para el dashboard
            if USE_GRADIENTE:
                color_hex = temperatura_a_gradiente(temp, 20.0, 30.0)
            else:
                color_hex = temperatura_a_color_hex(temp)
            
            contador += 1
            print(f"[{contador}] Temp={temp}°C {estado_temp} | Hum={hum}% | Pres={pres} hPa")
            print(f"       Color enviado: {color_hex}")
            
            # 4. Publicar (enviar) los 4 valores a Adafruit IO
            mqtt_client.publish(feed_temp_mqtt, str(temp))
            mqtt_client.publish(feed_hum_mqtt, str(hum))
            mqtt_client.publish(feed_pres_mqtt, str(pres))
            mqtt_client.publish(feed_color_mqtt, color_hex)  # Enviar color
            
            print("    ✓ Datos enviados correctamente\n")
            
            # 5. Verificar si hay mensajes (para mantener conexión viva)
            mqtt_client.check_msg()
            
            # 6. Esperar 10 segundos
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
    # Apagar todos los LEDs
    LED_FRIO.off()
    LED_NORMAL.off()
    LED_CALOR.off()
    mqtt_client.disconnect()
    print("LEDs apagados y desconectado de Adafruit IO")