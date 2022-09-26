# IntegradoraTelematica
Detección de Actividades no Autorizadas en los Laboratorios y Parqueaderos de FIEC Utilizando un Sistema de Seguridad IoT Controlada por una Aplicación Móvil

# Procesador de imagen
Este programa ayuda al procesamiento de imagen que se captura desde la webcam y a la conexión de node-red por medio de MQTT.
Para la implementación del producto se sugiere lo siguiente:
 1.- Cambiar la ruta del video. 
 2.- Cambiar la IP del broker. 

Por otro lado, en caso de implementar en la ESPOL se sugiera que todo el sistema este en la misma red. Esto quiere decir, tanto la cámara, el servidor y el módulo deben estar en la misma red.

# Flujo node-red
El flujo de node-red se encuentra como servicio en la micro SD.

# Detector de Personas
Este programa ayuda a receptar la señal del sensor y conectar por medio de MQTT al servicio de node-red.

