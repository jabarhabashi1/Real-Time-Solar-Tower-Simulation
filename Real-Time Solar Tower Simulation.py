import pvlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time
import os
from datetime import datetime

# Central tower coordinates
central_tower = {'lat': 35.6892, 'lon': 51.3890, 'height': 100}
focal_point_height = central_tower['height'] + 5  # 5 meters above the tower

# Mirror configuration
num_mirrors = 20
radius = 200
angles = np.linspace(0, 2 * np.pi, num_mirrors, endpoint=False)
mirrors = []
for angle in angles:
    mirror_lat_offset = radius * np.cos(angle) / 111111
    mirror_lon_offset = radius * np.sin(angle) / (111111 * np.cos(np.radians(central_tower['lat'])))
    mirrors.append({
        'lat': central_tower['lat'] + mirror_lat_offset,
        'lon': central_tower['lon'] + mirror_lon_offset,
        'height': 5
    })

# Calculate solar angles
def calculate_solar_angles(latitude, longitude, tz):
    current_time = pd.Timestamp(datetime.now(), tz=tz)
    solar_position = pvlib.solarposition.get_solarposition(current_time, latitude, longitude)
    elevation = solar_position['apparent_elevation'].values[0]
    azimuth = solar_position['azimuth'].values[0]
    return elevation, azimuth, current_time

# Calculate mirror reflection angles
def calculate_mirror_angles(mirror, tower, solar_elev, solar_az):
    dx = (tower['lon'] - mirror['lon']) * 111111 * np.cos(np.radians(tower['lat']))
    dy = (tower['lat'] - mirror['lat']) * 111111
    dz = focal_point_height - mirror['height']

    target_distance = np.sqrt(dx**2 + dy**2 + dz**2)
    elev_to_target = np.degrees(np.arcsin(dz / target_distance))
    azimuth_to_target = (np.degrees(np.arctan2(dx, dy)) + 360) % 360

    mirror_elevation = (elev_to_target + solar_elev) / 2
    mirror_azimuth = (azimuth_to_target + solar_az) / 2

    return mirror_elevation, mirror_azimuth

# Convert angles to a 3D vector
def angles_to_vector(elev, azim, length=50):
    elev_rad = np.radians(elev)
    azim_rad = np.radians(azim)
    x = length * np.cos(elev_rad) * np.sin(azim_rad)
    y = length * np.cos(elev_rad) * np.cos(azim_rad)
    z = length * np.sin(elev_rad)
    return x, y, z

# 3D Simulation
latitude, longitude, tz = central_tower['lat'], central_tower['lon'], 'Asia/Tehran'

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

while True:
    solar_elev, solar_az, current_time = calculate_solar_angles(latitude, longitude, tz)

    ax.clear()

    # Print solar angles
    print(f"Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Sun Elevation: {solar_elev:.2f}°, Sun Azimuth: {solar_az:.2f}°")

    # Draw tower (grey tower, red top segment)
    ax.plot([0, 0], [0, 0], [0, central_tower['height'] - 5], color='grey', linewidth=10)
    ax.plot([0, 0], [0, 0], [central_tower['height'], focal_point_height], color='red', linewidth=10)

    # Draw mirrors and display angles
    for idx, mirror in enumerate(mirrors):
        dx = (mirror['lon'] - central_tower['lon']) * 111111 * np.cos(np.radians(central_tower['lat']))
        dy = (mirror['lat'] - central_tower['lat']) * 111111
        dz = mirror['height']

        mirror_elev, mirror_azim = calculate_mirror_angles(mirror, central_tower, solar_elev, solar_az)

        # Display mirror angles
        print(f"Mirror {idx + 1}: Elevation = {mirror_elev:.2f}°, Azimuth = {mirror_azim:.2f}°")

        ax.scatter(dx, dy, dz, color='blue')

        # Sun rays to mirror
        sx, sy, sz = angles_to_vector(solar_elev, solar_az, length=50)
        ax.plot([dx, dx - sx], [dy, dy - sy], [dz, dz - sz], color='orange')

        # Reflection from mirror to tower
        ax.plot([dx, 0], [dy, 0], [dz, focal_point_height], color='green')

    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_zlabel('Z (m)')
    ax.set_title(f'Solar Tower Simulation\n{current_time.strftime("%Y-%m-%d %H:%M:%S")}\nSun Elevation: {solar_elev:.2f}°, Azimuth: {solar_az:.2f}°')
    ax.set_xlim(-radius-50, radius+50)
    ax.set_ylim(-radius-50, radius+50)
    ax.set_zlim(0, central_tower['height']+50)

    # Update time of each period
    plt.pause(10)
    os.system('cls' if os.name == 'nt' else 'clear')
