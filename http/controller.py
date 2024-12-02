import requests
import time
import sqlite3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # для импорта config
from config import *
from database import save_light_data
from datetime import datetime

class LightController:
    def __init__(self):
        self.current_light_level = None
    
    def get_settings(self):
        """Получение настроек из БД"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT min_light, max_light FROM light_settings WHERE id = 1")
        settings = c.fetchone()
        conn.close()
        return settings if settings else (300, 500)
        
    def check_and_control(self):
        """Проверка условий и управление светильником"""
        try:
            # Получаем данные о освещенности
            response = requests.get(f"{SENSOR_URL}/light")
            sensor_data = response.json()
            self.current_light_level = sensor_data['light_level']
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
             # Сохраняем данные в БД
            save_light_data(timestamp, self.current_light_level)

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

            # Обновляем статус на датчике
            requests.post(f"{SENSOR_URL}/light_status", json={'status': light_status == 'ON'})
            
            # Отправляем команду на управление светильником
            requests.post(f"{LIGHT_URL}/control", json={'status': light_status})
            
        except Exception as e:
            print(f"Ошибка в контроллере: {e}")


if __name__ == "__main__":
    controller = LightController()
    try:
        print("Контроллер запущен")
        while True:
            controller.check_and_control()
            # time.sleep(1)
    except KeyboardInterrupt:
        print("\nКонтроллер остановлен")