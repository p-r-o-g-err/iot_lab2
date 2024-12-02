DB_NAME = "light_control.db"
SECRET_KEY = "secret-key"
# Настройки для MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_USERNAME = "test_username"
MQTT_PASSWORD = "test_password"
MQTT_TOPIC_SENSOR = "room/sensor"
MQTT_TOPIC_LIGHT = "room/light"
# Настройки для HTTP
SENSOR_URL = "http://localhost:5001"  # URL симулятора датчика света
LIGHT_URL = "http://localhost:5002"   # URL симулятора светильника