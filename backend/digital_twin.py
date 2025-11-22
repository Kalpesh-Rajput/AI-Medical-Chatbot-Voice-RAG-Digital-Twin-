import random
import time
import json

class PatientDigitalTwin:
    def __init__(self):
        # Initialize realistic vitals
        self.heart_rate = random.randint(60, 100)
        self.temperature = round(random.uniform(97.0, 99.5), 1)
        self.systolic = random.randint(110, 130)
        self.diastolic = random.randint(70, 85)
        self.respiration_rate = random.randint(12, 20)
        self.oxygen_saturation = random.randint(95, 100)
        self.last_update = time.time()

    def update_vitals(self):
        """Simulate slight random changes in vitals."""
        self.heart_rate += random.randint(-3, 3)
        self.heart_rate = max(50, min(self.heart_rate, 120))

        self.temperature += round(random.uniform(-0.1, 0.1), 1)
        self.temperature = round(max(96.5, min(self.temperature, 101.0)), 1)

        self.systolic += random.randint(-2, 2)
        self.diastolic += random.randint(-2, 2)

        self.respiration_rate += random.randint(-1, 1)
        self.respiration_rate = max(10, min(self.respiration_rate, 24))

        self.oxygen_saturation += random.randint(-1, 1)
        self.oxygen_saturation = max(92, min(self.oxygen_saturation, 100))

        self.last_update = time.time()

    def get_vitals(self):
        """Return vitals with auto-update if >10 seconds old."""
        if time.time() - self.last_update > 10:
            self.update_vitals()
        return {
            "heart_rate": self.heart_rate,
            "temperature": self.temperature,
            "blood_pressure": f"{self.systolic}/{self.diastolic}",
            "respiration_rate": self.respiration_rate,
            "oxygen_saturation": self.oxygen_saturation
        }

    def get_vitals_json(self):
        """Return vitals as JSON string."""
        return json.dumps(self.get_vitals(), indent=2)
