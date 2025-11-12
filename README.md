# estación-iot-taller
Material del taller / exposición sobre **Adafruit IO** y una estación meteorológica simulada con Raspberry Pi Pico W (MicroPython).

> Repositorio con la presentación, las dos actividades propuestas y código de ejemplo (simulación de temperatura/humedad/presión, indicador LED y Color Picker para dashboard).

---

---

## Resumen del proyecto
Este taller muestra cómo registrar un dispositivo en **Adafruit IO**, crear feeds para tres variables (temperatura, humedad y presión) y configurar un dashboard que visualice esos valores en tiempo real. Además se muestra cómo enviar un color hexadecimal a un feed para usar el **Color Picker** del dashboard y cómo automatizar acciones (Actions) desde la plataforma. Todo lo anterior está documentado en la presentación incluida. :contentReference[oaicite:3]{index=3}

---

## Descripción de los scripts

### `simple_char.py`
- Conecta la Raspberry Pi Pico W a la red Wi-Fi (usa `secrets.py` con `ssid` y `password`).
- Crea un cliente MQTT para Adafruit IO y publica los feeds:
  - `taller-temperatura`, `taller-humedad`, `taller-presion`. :contentReference[oaicite:4]{index=4}
- En el bucle principal simula valores (temp, hum, pres) cada 10 segundos, los imprime por consola y los publica en Adafruit IO.
- Incluye manejo básico de reconexión Wi-Fi y reconexión MQTT. :contentReference[oaicite:5]{index=5}

### `colores.py`
- Basado en `simple_char.py` pero añade:
  - Control de 3 LEDs físicos conectados a pines (indicador visual: frío/normal/calor).
  - Funciones `temperatura_a_color_hex()` y `temperatura_a_gradiente()` para generar colores hex (ej. `#00ACEC`, `#00FF00`, `#FF0000`) o gradientes suaves entre azul→verde→rojo. :contentReference[oaicite:6]{index=6}
  - Publica además el feed `taller-color` con el color calculado, de modo que el **Color Picker** del dashboard refleje el estado. :contentReference[oaicite:7]{index=7}
- Mantiene la lógica de reconexión y comprobación de mensajes MQTT; apaga LEDs y desconecta al finalizar. :contentReference[oaicite:8]{index=8}

---

## Cómo usar (rápido)
1. Clona el repositorio:
   ```bash
   git clone https://github.com/TU_USUARIO/estacion-iot-taller.git
   cd estacion-iot-taller
