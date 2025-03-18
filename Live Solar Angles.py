import pvlib
import pandas as pd
import time
import os
from datetime import datetime

# Set geographic coordinates (example: Tehran)
latitude, longitude = 35.6892, 51.3890
tz = 'Asia/Tehran'

# Function to calculate sun angles
def calculate_solar_angles(latitude, longitude, tz):
    current_time = pd.Timestamp(datetime.now(), tz=tz)
    solar_position = pvlib.solarposition.get_solarposition(current_time, latitude, longitude)

    elevation = solar_position['apparent_elevation'].values[0]
    azimuth = solar_position['azimuth'].values[0]

    return elevation, azimuth, current_time

# Infinite loop to update every 20 seconds
while True:
    elevation, azimuth, current_time = calculate_solar_angles(latitude, longitude, tz)

    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"Real-Time Solar Position (Updated every 20 seconds)\n")
    print(f"Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Location: Latitude {latitude}, Longitude {longitude}\n")
    print(f"Solar Elevation Angle: {elevation:.2f} degrees")
    print(f"Solar Azimuth Angle: {azimuth:.2f} degrees")

    # Pause for 20 seconds
    time.sleep(20)
