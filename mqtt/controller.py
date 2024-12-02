import paho.mqtt.client as mqtt
import sqlite3
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # для импорта config
from config import *

class LightController:
    def __init__(self):
        self.client = mqtt.Client("light_controller")
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.connect(MQTT_BROKER, MQTT_PORT)
        
        # Подписываемся на топик с данными датчика
        self.client.on_message = self.on_message
        self.client.subscribe(MQTT_TOPIC_SENSOR)
        
        self.current_light_level = None
        self.client.loop_start()

    def get_settings(self):
        """Получение настроек из БД"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT min_light, max_light FROM light_settings WHERE id = 1")
        settings = c.fetchone()
        conn.close()
        return settings if settings else (300, 500)
    
    def on_message(self, client, userdata, msg):
        """Обработка входящих сообщений"""
        try:
            if msg.topic == MQTT_TOPIC_SENSOR:
                # Получили новые данные от датчика
                self.current_light_level = float(msg.payload.decode())
                self.check_and_control()
                
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def check_and_control(self):
        """Проверка условий и управление светильником"""
        if self.current_light_level is None:
            return
            
        min_light, max_light = self.get_settings()
       
        # Определяем нужное состояние светильника
        if self.current_light_level < min_light:
            light_status = 'ON'
        elif self.current_light_level > max_light:
            light_status = 'OFF'
        else:
            light_status = 'OFF'

        print(f"Текущая освещенность: {self.current_light_level}, " + 
                  f"мин: {min_light}, макс: {max_light}, " + 
                  f"светильник: {light_status}")
        
        self.client.publish(MQTT_TOPIC_LIGHT, light_status)

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == "__main__":
    controller = LightController()
    try:
        print("Контроллер запущен")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nКонтроллер остановлен")
    finally:
        controller.stop()