import re
import csv
import json
import random
import sys
from directory_names import Folders, Examples


def generate_names(num_names: int):
    names = []

    with open(f'{Folders.static}last_names.json') as file:
        last_names = json.load(file)
    with open(f'{Folders.static}first_names.json') as file:
        first_names = json.load(file)

    grades = [7, 8, 9, 10, 11, 12]
    class_letters = "ABCDEFGHIJKLMNOPQRST"

    for i in range(num_names):
        name = f"{random.choice(first_names)} {random.choice(last_names)} " \
               f"[{random.choice(grades)}{random.choice(class_letters)}]"
        names.append(name)

    with open(examples.student_names, 'w') as file:
        json.dump(names, file, indent=4)


def generate_timetables():
    def generate_classroom():
        return f"{random.choice(blocks)}{random.choice(floors)}.{str(random.choice(classes)).zfill(2)}"

    def generate_class(year: str, letter: str):
        return f"{''.join(random.choices(letters, k=3))}{year.zfill(2)}1{letter}"

    def generate_teacher():
        return "".join(random.choices(letters, k=6))

    with open(examples.student_names) as file:
        names = json.load(file)

    blocks = "ABCDEFGIJP"
    floors = "G12"
    classes = range(1, 10)
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    with open(f'{Folders.timetables}{examples.timetables}', 'w') as file:
        writer = csv.writer(file)
        for name in names:
            first_name = name.split(' ')[0]
            last_name = name.split(' ')[1]
            grade = re.search(r"\[(\d\d?)", name).group(1)
            class_letter = re.search(r"([A-Z])]", name).group(1)
            arc_class = f"{grade}{class_letter}"
            writer.writerow([f"{last_name}, {first_name}, , Year {grade}, {arc_class}",
                             f"{generate_class(grade, class_letter)}\n{generate_teacher()} {generate_classroom()}", "",
                             f"{generate_class(grade, class_letter)}\n{generate_teacher()} {generate_classroom()}", "",
                             f"{generate_class(grade, class_letter)}\n{generate_teacher()} {generate_classroom()}", "",
                             f"{generate_class(grade, class_letter)}\n{generate_teacher()} {generate_classroom()}"])


def generate_tickets():
    items = ['Chocolate', 'Rose', 'Serenade', 'Special Serenade']
    periods = [1, 2, 3, 4]

    tickets = {}
    with open(examples.student_names) as file:
        names = json.load(file)
        for number, name in enumerate(names):
            if random.random() < 0.5:
                item_type = random.choices(items, weights=[5, 5, 10, 2])[0]
                if item_type == "Special Serenade":
                    chosen_period = random.choice(periods)
                else:
                    chosen_period = ""
                tickets[number] = {"Recipient Name": name, "Item Type": item_type, "Period": chosen_period}

    with open(f'{Folders.tickets}{examples.tickets}', 'w') as file:
        json.dump(tickets, file, indent=4)


def main():
    generate_names(500)
    generate_timetables()
    generate_tickets()


if __name__ == "__main__":
    seed = random.randrange(sys.maxsize)
    checksum = str(hex(seed))[2:6].upper()
    examples = Examples(checksum)
    main()
