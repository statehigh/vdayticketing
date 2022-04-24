import csv
import json
import random
from directory_names import Folders, Examples

grades = [7, 8, 9, 10, 11, 12]
class_letters = "ABCDEFGHIJKLMNOPQRST"


def generate_names(num_names: int):
    names = []

    with open(f'{Folders.static}last_names.json') as file:
        last_names = json.load(file)
    with open(f'{Folders.static}first_names.json') as file:
        first_names = json.load(file)

    for i in range(num_names):
        name = f"{random.choice(first_names)} {random.choice(last_names)} " \
               f"[{random.choice(grades)}{random.choice(class_letters)}]"
        names.append(name)

    with open(Examples.student_names, 'w') as file:
        json.dump(names, file)


def generate_timetables():
    def generate_classroom():
        return f"{random.choice(blocks)}{random.choice(floors)}.{str(random.choice(classes)).zfill(2)}"

    def generate_class(year: str, letter: str):
        return f"{''.join(random.choices(letters, k=3))}{year.zfill(2)}1{letter}"

    def generate_teacher():
        return "".join(random.choices(letters, k=6))

    with open(Examples.student_names) as file:
        names = json.load(file)

    blocks = "ABCDEFGIJP"
    floors = "G12"
    classes = range(1, 10)
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    with open(f'{Folders.timetables}{Examples.timetables}', 'w') as file:
        writer = csv.writer(file)
        for name in names:
            first_name = name.split(' ')[0]
            last_name = name.split(' ')[1]
            year = str(random.choice(grades))
            letter = random.choice(class_letters)
            arc_class = f"{year}{letter}"
            writer.writerow([f"{last_name}, {first_name}, , Year {year}, {arc_class}",
                             f"{generate_class(year, letter)}\n{generate_teacher()} {generate_classroom()}", "",
                             f"{generate_class(year, letter)}\n{generate_teacher()} {generate_classroom()}", "",
                             f"{generate_class(year, letter)}\n{generate_teacher()} {generate_classroom()}", "",
                             f"{generate_class(year, letter)}\n{generate_teacher()} {generate_classroom()}"])


def generate_tickets():
    items = ['Chocolate', 'Rose', 'Serenade', 'Special Serenade']
    periods = [1, 2, 3, 4]

    tickets = {}
    with open(Examples.student_names) as file:
        names = json.load(file)
        for number, name in enumerate(names):
            if random.random() < 0.5:
                item_type = random.choices(items, weights=[5, 5, 10, 2])[0]
                if item_type == "Special Serenade":
                    chosen_period = random.choice(periods)
                else:
                    chosen_period = ""
                tickets[number] = {"Recipient Name": name, "Item Type": item_type, "Period": chosen_period}

    with open(f'{Folders.tickets}{Examples.tickets}', 'w') as file:
        json.dump(tickets, file)


def main():
    generate_names(500)
    generate_timetables()
    generate_tickets()


if __name__ == "__main__":
    main()
