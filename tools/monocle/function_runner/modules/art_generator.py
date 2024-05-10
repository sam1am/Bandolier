import display
import random
import time
import math

def random_color():
    return random.randint(0, 0xFFFFFF)

def random_point():
    return (random.randint(0, display.WIDTH - 1), random.randint(0, display.HEIGHT - 1))

def random_polygon(num_points):
    points = []
    for _ in range(num_points):
        x, y = random_point()
        points.append(x)
        points.append(y)
    return display.Polygon(points, random_color())


def random_circle(radius):
    center = random_point()
    points = []
    for i in range(0, 360, 10):
        x = int(center[0] + radius * math.cos(math.radians(i)))
        y = int(center[1] + radius * math.sin(math.radians(i)))
        points.append(x)
        points.append(y)
    return display.Polygon(points, random_color())

def random_line():
    start = random_point()
    end = random_point()
    return display.Line(start[0], start[1], end[0], end[1], random_color(), random.randint(1, 5))

def random_text():
    text = ''
    for _ in range(random.randint(1, 8)):
        text += chr(random.randint(65, 90))  # Generate random uppercase letter (ASCII code 65-90)
    position = random_point()
    return display.Text(text, position[0], position[1], random_color(), justify=random.choice(
        [display.TOP_LEFT, display.TOP_CENTER, display.TOP_RIGHT,
         display.MIDDLE_LEFT, display.MIDDLE_CENTER, display.MIDDLE_RIGHT,
         display.BOTTOM_LEFT, display.BOTTOM_CENTER, display.BOTTOM_RIGHT]))



def generate_art():
    display.clear()
    elements = []
    # get a random number between 5 and 10
    num_elements = random.randint(53 8)
    print(f"Generating {num_elements} elements")
    
    for _ in range(num_elements):
        element_type = random.choice(['polygon', 'circle', 'line', 'text'])
        if element_type == 'polygon':
            elements.append(random_polygon(random.randint(3, 8)))
        elif element_type == 'circle':
            elements.append(random_circle(random.randint(10, 100)))
        elif element_type == 'line':
            elements.append(random_line())
        else:
            elements.append(random_text())
    
    display.show(elements)

while True:
    generate_art()
    time.sleep(5)
