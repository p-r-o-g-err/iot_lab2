from flask import Flask, request, jsonify
import random
import time
import threading

app_sensor = Flask(__name__)
app_light = Flask(__name__)

class LightSensor:
    def __init__(self):
        self.current_light_level = 400.0
        self.light_is_active = False

    def simulate(self):
        # Симуляция изменения освещенности
        self.current_light_level += random.uniform(-30, 100) if self.light_is_active else random.uniform(-100, 30)

        # natural_change = random.uniform(-100, 50)
        # light_effect = random.uniform(0, 70) if self.light_is_active else 0
        # self.current_light_level += natural_change + light_effect
        
        self.current_light_level = max(0, min(1000, self.current_light_level))
        
        return round(self.current_light_level, 1)

@app_sensor.route('/light', methods=['GET'])
def get_light():
    global sensor
    return jsonify({
        'light_level': sensor.simulate(),
        'light_status': 'ON' if sensor.light_is_active else 'OFF'
    })

@app_sensor.route('/light_status', methods=['POST'])
def set_light_status():
    global sensor
    sensor.light_is_active = request.json.get('status', False)
    return jsonify({'status': 'success'})

@app_light.route('/control', methods=['POST'])
def control_light():
    status = request.json.get('status', 'OFF')
    return jsonify({'status': status})

def run_sensor_app():
    app_sensor.run(port=5001)

def run_light_app():
    app_light.run(port=5002)

if __name__ == "__main__":
    sensor = LightSensor()
    
    # Запуск серверов в отдельных потоках
    sensor_thread = threading.Thread(target=run_sensor_app)
    light_thread = threading.Thread(target=run_light_app)
    sensor_thread.start()
    light_thread.start()

    sensor_thread.join()
    light_thread.join()

    print("Запущены симуляторы устройств")