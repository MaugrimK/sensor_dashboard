import logging
import random

try:
    import Adafruit_DHT
except:
    pass

logger = logging.getLogger(__name__)


class TempSensor:
    def __init__(self, pin, fake_measurements):
        self.pin = pin
        self.fake_measurements = fake_measurements

    def get_real_measurement_from_sensor(self):
        try:
            humidity, temperature = Adafruit_DHT.read_retry(
                sensor=Adafruit_DHT.DHT22,
                pin=self.pin,
                retries=15,  # default
                delay_seconds=2  # default
                )
            assert humidity
        except Exception:
            logger.exception('Error when taking a reading from DHT11')
            return None, None

        return humidity, temperature

    def get_fake_measurement_from_sensor(self):
        return random.randint(30, 50), random.randint(20, 25)

    def get_measuremet_from_sensor(self):
        if self.fake_measurements:
            return self.get_fake_measurement_from_sensor()
        else:
            return self.get_real_measurement_from_sensor()
