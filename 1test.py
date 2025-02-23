import math
import os
import time

width = 160
height = 44
background_ascii_code = '.'
distance_from_cam = 100
k1 = 40
increment_speed = 0.6

def calculate_x(i, j, k, a, b, c):
    return j * math.sin(a) * math.sin(b) * math.cos(c) - k * math.cos(a) * math.sin(b) * math.cos(c) + \
           j * math.cos(a) * math.sin(c) + k * math.sin(a) * math.sin(c) + i * math.cos(b) * math.cos(c)

def calculate_y(i, j, k, a, b, c):
    return j * math.cos(a) * math.cos(c) + k * math.sin(a) * math.cos(c) - \
           j * math.sin(a) * math.sin(b) * math.sin(c) + k * math.cos(a) * math.sin(b) * math.sin(c) - \
           i * math.cos(b) * math.sin(c)

def calculate_z(i, j, k, a, b):
    return k * math.cos(a) * math.cos(b) - j * math.sin(a) * math.cos(b) + i * math.sin(b)

def calculate_for_surface(cube_x, cube_y, cube_z, ch, a, b, c, z_buffer, buffer):
    x = calculate_x(cube_x, cube_y, cube_z, a, b, c)
    y = calculate_y(cube_x, cube_y, cube_z, a, b, c)
    z = calculate_z(cube_x, cube_y, cube_z, a, b) + distance_from_cam

    ooz = 1 / z

    xp = int(width / 2 + horizontal_offset + k1 * ooz * x * 2)
    yp = int(height / 2 + k1 * ooz * y)

    idx = xp + yp * width
    if 0 <= idx < width * height:
        if ooz > z_buffer[idx]:
            z_buffer[idx] = ooz
            buffer[idx] = ch

a = 0.0
b = 0.0
c = 0.0

while True:
    buffer = [background_ascii_code] * (width * height)
    z_buffer = [0.0] * (width * height)

    for cube_width, horizontal_offset in [(20, -40), (10, 10), (5, 40)]:
        for cube_x in range(int(-cube_width * 10), int(cube_width * 10) + 1, int(increment_speed * 10)):
            cube_x /= 10.0  # Scale back to float
            for cube_y in range(int(-cube_width * 10), int(cube_width * 10) + 1, int(increment_speed * 10)):
                cube_y /= 10.0  # Scale back to float
                calculate_for_surface(cube_x, cube_y, -cube_width, '@', a, b, c, z_buffer, buffer)
                calculate_for_surface(cube_width, cube_y, cube_x, '$', a, b, c, z_buffer, buffer)
                calculate_for_surface(-cube_width, cube_y, -cube_x, '~', a, b, c, z_buffer, buffer)
                calculate_for_surface(-cube_x, cube_y, cube_width, '#', a, b, c, z_buffer, buffer)
                calculate_for_surface(cube_x, -cube_width, -cube_y, ';', a, b, c, z_buffer, buffer)
                calculate_for_surface(cube_x, cube_width, cube_y, '+', a, b, c, z_buffer, buffer)


    os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console
    for k in range(width * height):
        print(buffer[k] if k % width else '\n', end='')

    a += 0.05
    b += 0.05
    c += 0.01