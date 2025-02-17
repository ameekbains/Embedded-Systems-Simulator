"""
embedded_simulator.py
A single-file embedded systems simulator with GPIO, ADC, UART, and virtual time
"""

import argparse
import time
from typing import Dict, List

# ----------------- Hardware Abstraction Layer -----------------
class VirtualGPIO:
    def __init__(self):
        self.pins: Dict[int, int] = {}
    
    def write(self, pin: int, value: int):
        self.pins[pin] = value
        print(f"GPIO {pin} set to {value}")

    def read(self, pin: int) -> int:
        return self.pins.get(pin, 0)

class VirtualADC:
    def __init__(self):
        self.sensors: Dict[int, float] = {0: 25.0}  # Default sensor data
    
    def read(self, channel: int) -> float:
        return self.sensors.get(channel, 0.0)

class VirtualUART:
    def __init__(self):
        self.buffer: List[str] = []
    
    def send(self, data: str):
        self.buffer.append(f"[UART TX]: {data}")
        print(self.buffer[-1])
    
    def receive(self) -> str:
        return "SIM_ACK" if self.buffer else ""

# ----------------- Simulation Engine -----------------
class EmbeddedSimulator:
    def __init__(self, timeout=10.0, time_scale=1.0):
        self.hal = {
            'gpio': VirtualGPIO(),
            'adc': VirtualADC(),
            'uart': VirtualUART()
        }
        self.timeout = timeout
        self.time_scale = time_scale
        self.virtual_time = 0.0
        self.running = False

    def run(self, user_setup, user_loop):
        self.running = True
        start_time = time.monotonic()
        
        # Hardware initialization
        user_setup()
        
        while self.running and self.virtual_time < self.timeout:
            # Execute user code
            user_loop()
            
            # Update virtual time
            elapsed = (time.monotonic() - start_time) * self.time_scale
            self.virtual_time = elapsed
            
            # Simulation heartbeat
            print(f"\nVirtual Time: {self.virtual_time:.2f}s")
            time.sleep(0.1 * self.time_scale)  # Throttle execution
            
            if self.virtual_time >= self.timeout:
                self.stop()
    
    def stop(self):
        self.running = False
        print("\nSimulation stopped")

# ----------------- Example User Firmware -----------------
def user_setup():
    """User-defined initialization"""
    global gpio, adc, uart  # Access HAL components
    gpio.write(13, 0)      # Initialize LED pin
    uart.send("SYSTEM BOOT")

def user_loop():
    """User-defined main loop"""
    global gpio, adc, uart
    
    # Read simulated temperature
    temp = adc.read(0)
    print(f"Temperature: {temp}°C")
    
    # Control logic
    if temp > 30.0:
        gpio.write(13, 1)
        uart.send("COOLING ON")
    else:
        gpio.write(13, 0)
    
    # Simulate sensor temperature increase
    adc.sensors[0] += 0.5

# ----------------- Main Execution -----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embedded System Simulator")
    parser.add_argument("--timeout", type=float, default=10.0,
                      help="Simulation duration in virtual seconds")
    parser.add_argument("--speed", type=float, default=1.0,
                      help="Time acceleration factor (e.g., 2.0 for 2x speed)")
    args = parser.parse_args()

    # Initialize simulator and HAL
    sim = EmbeddedSimulator(timeout=args.timeout, time_scale=args.speed)
    gpio = sim.hal['gpio']
    adc = sim.hal['adc']
    uart = sim.hal['uart']

    print("=== Starting Embedded System Simulation ===")
    try:
        sim.run(user_setup, user_loop)
    except KeyboardInterrupt:
        sim.stop()
    print("=== Simulation Complete ===")
    print("Final GPIO States:", gpio.pins)