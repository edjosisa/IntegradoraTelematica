from time import sleep
import cv2 # libreria para procesar imagen
import numpy as np
import easyocr 
import time
import paho.mqtt.client as mqttclient
import MySQLdb #libreria de base de dato

# Conexión para la base de datos. 
db=MySQLdb.connect(host="localhost",user="admin",passwd="password", database="placas")
cur= db.cursor()

# Función para conectar al servicio de MQTT
def on_connect (client, usedata, flags, rc) :
    if rc==0:
        print("client is connected")
        global connected
        connected=True
    else:
        print("client is not connected")

def ordenar_puntos(puntos):
    n_puntos = np.concatenate([puntos[0], puntos[1], puntos[2], puntos[3]]).tolist()

    y_order = sorted(n_puntos, key=lambda n_puntos: n_puntos[1])

    x1_order = y_order[:2]
    x1_order = sorted(x1_order, key=lambda x1_order: x1_order[0])

    x2_order = y_order[2:4]
    x2_order = sorted(x2_order, key=lambda x2_order: x2_order[0])
    
    return [x1_order[0], x1_order[1], x2_order[0], x2_order[1]]
def has_numbers(string):
     return any(char.isdigit() for char in string)    
reader = easyocr.Reader(["en"], gpu=False)

#Conexión con la ruta del stream
cap = cv2.VideoCapture("http://192.168.100.14:8081/0/stream/")
#cap = cv2.VideoCapture("/dev/video1")
connected=False
broker_address="192.168.100.14"
port=1883

#Conexión MQTT
client=mqttclient.Client ("MQTT")
#client.username_pw_set (user, password=password)
client.on_connect=on_connect
client.connect (broker_address, port=port)
client.loop_start()
while connected!=True:
	time.sleep (0.2)
while True:
     ret, frame = cap.read()
     if ret == False:
          break
     start = time.time()
     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
     canny = cv2.Canny(gray, 80, 150)
     canny = cv2.dilate(canny, None, iterations=0)
     cv2.imshow("Canny", canny)
     cnts = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
     cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:1]

     for c in cnts:
          epsilon = 0.01*cv2.arcLength(c,True)
          approx = cv2.approxPolyDP(c,epsilon,True)
          
          if len(approx)==4:
               cv2.drawContours(frame, [approx], 0, (0,255,255),2)
               
               puntos = ordenar_puntos(approx)

               cv2.circle(frame, tuple(puntos[0]), 7, (255,0,0), 2)
               cv2.circle(frame, tuple(puntos[1]), 7, (0,255,0), 2)
               cv2.circle(frame, tuple(puntos[2]), 7, (0,0,255), 2)
               cv2.circle(frame, tuple(puntos[3]), 7, (255,255,0), 2)
               
               pts1 = np.float32(puntos)
               pts2 = np.float32([[0,0],[270,0],[0,70],[270,70]])
               M = cv2.getPerspectiveTransform(pts1,pts2)
               dst = cv2.warpPerspective(gray,M,(270,70))
               dst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
               cv2.imshow('dst', dst)

               result = reader.readtext(dst)
               #print(result)
               for res in result:
			
                    if has_numbers(res[1])  and res[2]>0.80 :
                         print(res[1].replace(" ","").replace("-","")) #res[1] texto placa
                         print(res[2])
			
                         val=cur.execute("""SELECT * from placas_carros WHERE texto=%s;""",(str(res[1].replace(" ","").replace("-","")),))#validacion 1 cuando placa es encontrada en la base y 0 sino
                         print(val)
                         print(type(val))
                         if val==0:
				# Se agrega la alarma a la base de datos local
                         	client.publish("outTopic", "0")
                         	cur.execute("""INSERT INTO alarmaPlaca(placa) VALUES(%s);""",(str(res[1]),))
                         	db.commit()
                      	
     client.loop_stop()
     end = time.time()
     fps = 1 / (end - start)
     cv2.putText(frame, "FPS: {:.2f}".format(fps), (20, 400), 1, 2, (0, 255, 0), 2)
     cv2.imshow('Frame', frame)
     k = cv2.waitKey(1) & 0xFF
     if k == 27:
          break
cap.release()
cv2.destroyAllWindows()    
