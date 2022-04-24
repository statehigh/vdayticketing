import re
import csv
import json
import random
import sys
from directory_names import Folders, Examples


def generate_people(num_people: int) -> list:
    people = []

    with open(f'{Folders.static}last_names.json') as file:
        last_names = json.load(file)
    with open(f'{Folders.static}first_names.json') as file:
        first_names = json.load(file)

    grades = [7, 8, 9, 10, 11, 12]
    class_letters = "ABCDEFGHIJKLMNOPQRST"

    for i in range(num_people):
        person = {"First Name": random.choice(first_names), "Last Name": random.choice(last_names),
                  "ARC": f"{random.choice(grades)}{random.choice(class_letters)}"}
        people.append(person)

    return people


def generate_timetables(people):
    def generate_classroom():
        return f"{random.choice(blocks)}{random.choice(floors)}.{str(random.choice(classes)).zfill(2)}"

    def generate_class(year: str, letter: str):
        return f"{''.join(random.choices(letters, k=3))}{year.zfill(2)}1{letter}"

    def generate_teacher():
        return "".join(random.choices(letters, k=6))

    blocks = "ABCDEFGIJP"
    floors = "G12"
    classes = range(1, 10)
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    with open(f'{Folders.timetables}{examples.timetables}', 'w') as file:
        writer = csv.writer(file)
        for person in people:
            grade = re.search(r"\d\d?", person['ARC']).group(0)
            class_letter = person['ARC'][-1]
            writer.writerow([f"{person['Last Name']}, {person['First Name']}, , Year {grade}, {person['ARC']}",
                             f"{generate_class(grade, class_letter)}\n{generate_teacher()} {generate_classroom()}", "",
                             f"{generate_class(grade, class_letter)}\n{generate_teacher()} {generate_classroom()}", "",
                             f"{generate_class(grade, class_letter)}\n{generate_teacher()} {generate_classroom()}", "",
                             f"{generate_class(grade, class_letter)}\n{generate_teacher()} {generate_classroom()}"])


def generate_tickets(people):
    items = ['Chocolate', 'Rose', 'Serenade', 'Special Serenade']
    periods = [1, 2, 3, 4]

    tickets = {}
    for number, person in enumerate(people):
        if random.random() < 0.5:
            name = f"{person['First Name']} {person['Last Name']} [{person['ARC']}]"
            item_type = random.choices(items, weights=[3, 7, 5, 1])[0]
            if item_type == "Special Serenade":
                chosen_period = random.choice(periods)
            else:
                chosen_period = ""
            tickets[number] = {"Recipient Name": name, "Item Type": item_type, "Period": chosen_period}

    with open(f'{Folders.tickets}{examples.tickets}', 'w') as file:
        json.dump(tickets, file, indent=4)


def main():
    people = generate_people(500)
    generate_timetables(people)
    generate_tickets(people)


if __name__ == "__main__":
    seed = random.randrange(sys.maxsize)
    checksum = str(hex(seed))[2:6].upper()
    examples = Examples(checksum)
    main()
