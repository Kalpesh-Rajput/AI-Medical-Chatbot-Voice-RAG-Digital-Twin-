from backend.digital_twin import PatientDigitalTwin
import time

twin = PatientDigitalTwin()

print("Initial:", twin.get_vitals())
time.sleep(2)
print("Updated:", twin.get_vitals())
