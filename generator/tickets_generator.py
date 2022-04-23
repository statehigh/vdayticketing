import json
import random

items = ['Chocolate', 'Rose', 'Serenade', 'Special Serenade']
periods = [1, 2, 3, 4]

# requires CWD to be in the parent

tickets = {}
with open("student_names.json") as file:
    names = json.load(file)
    for number, name in enumerate(names):
        if random.random() < 0.5:
            item_type = random.choices(items, weights=[5, 5, 10, 2])[0]
            if item_type == "Special Serenade":
                chosen_period = random.choice(periods)
            else:
                chosen_period = ""
            tickets[number] = {"Recipient Name": name, "Item Type": item_type, "Period": chosen_period}

with open('tickets/EXAMPLE Tickets.json', 'w') as file:
    json.dump(tickets, file)
