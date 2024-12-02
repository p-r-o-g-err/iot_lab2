import time
import random
import paho.mqtt.client as mqtt
import threading
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # для импорта config
from config import *

class LightSensor:
    """Симулятор датчика освещенности"""
    def __init__(self):
        self.client = mqtt.Client("light_sensor")
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.current_light_level = 400.0
        
        # Подписываемся на состояние светильника
        self.client.on_message = self.on_message
        self.client.subscribe(MQTT_TOPIC_LIGHT)
        
        self.light_is_active = False
        self.client.loop_start()

    def on_message(self, client, userdata, msg):
        """Отслеживаем состояние светильника"""
        command = msg.payload.decode()
        self.light_is_active = (command == "ON")

    def simulate(self):
        """Одно измерение освещенности"""
        self.current_light_level += random.uniform(-30, 100) if self.light_is_active else random.uniform(-100, 30)

        # natural_change = random.uniform(-100, 50)
        # light_effect = random.uniform(0, 70) if self.light_is_active else 0
        # self.current_light_level += natural_change + light_effect

        self.current_light_level = max(0, min(1000, self.current_light_level))
        
        # Публикация значения освещенности
        self.client.publish(MQTT_TOPIC_SENSOR, f"{self.current_light_level:.1f}")
        print(f"Текущая освещенность: {self.current_light_level:.1f} люкс " + 
                f"(Светильник: {'Вкл' if self.light_is_active else 'Выкл'})")
        # time.sleep(2)

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

class LightControl:
    """Симулятор светильника"""
    def __init__(self):
        self.client = mqtt.Client("light_control")
        self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.is_active = False
        
        # Подписка на команды управления
        self.client.on_message = self.on_message
        self.client.subscribe(MQTT_TOPIC_LIGHT)
        self.client.loop_start()
    
    def on_message(self, client, userdata, msg):
        """Обработка команд включения/выключения"""
        command = msg.payload.decode()
        self.is_active = (command == "ON")
        print(f"Состояние светильника изменено на: {'ON' if self.is_active else 'OFF'}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

def run_sensor(sensor):
    try:
        print("Запуск симуляции датчика освещенности")
        while True:
            sensor.simulate()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nОстановка симуляции датчика освещенности")
        sensor.stop()

def run_control(control):
    try:
        print("Запуск симулятора светильника")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nОстановка симулятора светильника")
        control.stop()

if __name__ == "__main__":
    sensor = LightSensor()
    fan = LightControl()
    
    # Запуск в отдельных потоках
    sensor_thread = threading.Thread(target=run_sensor, args=(sensor,))
    fan_thread = threading.Thread(target=run_control, args=(fan,))
    
    sensor_thread.start()
    fan_thread.start()

    try:
        sensor_thread.join()
        fan_thread.join()
    except KeyboardInterrupt:
        print("\nОстановка симуляции")