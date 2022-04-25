import csv
import json
import random
from directory_names import Folders, Files


def migrate_tickets():
    tickets = {}

    with open('tickets.csv') as file:
        reader = csv.reader(file)
        for line in reader:
            if len(line[0]) < 1:
                continue

            ticket_number = line[0]
            name = line[1]
            period = ""

            if line[3] == "1":
                item_type = "Chocolate"
            elif line[4] == "1":
                item_type = "Rose"
            elif line[5] == "1":
                item_type = "Serenade"
            else:
                continue

            if item_type == "Serenade" and random.random() < 0.1:
                item_type = "Special Serenade"
                period = random.choice([1, 2, 3, 4])

            tickets[ticket_number] = {'Recipient Name': name, 'Item Type': item_type, 'Period': period}

    with open(f'{Folders.tickets}tickets.json', 'w') as file:
        json.dump(tickets, file, indent=4)


def migrate_students():
    students = []

    with open('students.csv') as file:
        reader = csv.reader(file)
        for line in reader:
            student = {'StudentName': line[0], 'P1': line[2], 'P2': line[3], 'P3': line[4], 'P4': line[5]}
            students.append(student)

    with open(Files.student_classes, 'w') as file:
        fieldnames = ["StudentName", "P1", "P2", "P3", "P4"]
        writer = csv.DictWriter(file, fieldnames)
        for student in students:
            writer.writerow(student)


def main():
    migrate_students()
    migrate_tickets()


if __name__ == "__main__":
    main()
