import csv
import json
import random


def generate_classroom():
    return f"{random.choice(blocks)}{random.choice(floors)}.{str(random.choice(classes)).zfill(2)}"


def generate_class(year: str, letter: str):
    return f"{''.join(random.choices(letters, k=3))}{year.zfill(2)}1{letter}"


def generate_teacher():
    return "".join(random.choices(letters, k=6))


with open('example_names.json') as file:
    names = json.load(file)

blocks = "ABCDEFGIJP"
floors = "G12"
classes = range(1, 10)
grades = [7, 8, 9, 10, 11, 12]
arc_classes = "ABCDEFGHIJKLMNOPQRST"
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

with open('EXAMPLE Timetable.csv', 'w') as file:
    writer = csv.writer(file)
    for name in names:
        first_name = name.split(' ')[0]
        last_name = name.split(' ')[1]
        year = str(random.choice(grades))
        letter = random.choice(arc_classes)
        arc_class = f"{year}{letter}"
        writer.writerow([f"{last_name}, {first_name}, , Year {year}, {arc_class}",
                         f"{generate_class(year, letter)}\n{generate_teacher()} {generate_classroom()}", "",
                         f"{generate_class(year, letter)}\n{generate_teacher()} {generate_classroom()}", "",
                         f"{generate_class(year, letter)}\n{generate_teacher()} {generate_classroom()}", "",
                         f"{generate_class(year, letter)}\n{generate_teacher()} {generate_classroom()}"])
