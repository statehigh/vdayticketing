import json
import random

names = []

with open('last_names.json') as file:
    last_names = json.load(file)

with open('first_names.json') as file:
    first_names = json.load(file)

numbers = [7, 8, 9, 10, 11, 12]
letters = "ABCDEFGHIJKLMNOPQRST"

for i in range(500):
    name = f"{random.choice(first_names)} {random.choice(last_names)} " \
           f"[{random.choice(numbers)}{random.choice(letters)}]"
    names.append(name)

with open("example_names.json", 'w') as file:
    json.dump(names, file)
