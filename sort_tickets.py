import re
import os
import csv
import json
from glob import glob
from itertools import groupby
from directory_names import Folders, Files


class Ticket:
    def __init__(self, ticket_number: int, recipient_name, item_type: str, p1: str, p2: str, p3: str, p4: str):
        # ticket info
        self.ticket_number = ticket_number
        self.recipient_name = recipient_name
        self.item_type = item_type
        self.group = None

        # where the recipient's classes are for each period don't rename or else setattr() will break
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4

        # whether the algorithm has chosen this period. don't rename or else setattr() will break
        self.is_p1 = True
        self.is_p2 = True
        self.is_p3 = True
        self.is_p4 = True

    @property
    def chosen_period(self) -> int:
        # if a ticket only has 1 period it can go to, return what it is
        if self.has_no_choice():
            for period in range(1, 5):
                if getattr(self, f"is_p{period}"):
                    return period
        else:
            raise Exception(f"Tried to get only_period when there were multiple periods possible {self}")

    @property
    def chosen_classroom(self):
        if self.has_no_choice():
            return getattr(self, f"p{self.chosen_period}")

    def choose_period(self, chosen_period: int):  # takes period as a number (1, 2, 3, 4) not as p1, p2, p3, p4
        for period in range(1, 5):  # generates 1, 2, 3, 4 (corresponding to period numbers)
            if period is not chosen_period:  # set every period to false except the chosen one
                setattr(self, f'is_p{period}', False)
        setattr(self, f'is_p{chosen_period}', True)  # sets chosen period as true

    def has_no_choice(self) -> bool:
        has_one_choice = False
        for period in range(1, 5):
            if getattr(self, f'is_p{period}'):
                if has_one_choice:
                    return False
                else:
                    has_one_choice = True
        return True

    def as_dict(self):
        return {"Ticket Number": self.ticket_number, "Recipient Name": self.recipient_name,
                "Chosen Period": self.chosen_period, "Chosen Classroom": self.chosen_classroom,
                "Item Type": self.item_type, "Group": self.group,
                "P1": self.p1, "P2": self.p2, "P3": self.p3, "P4": self.p4}

    def __repr__(self):
        # for dev purposes only
        p1 = '' if self.is_p1 else '\''
        p2 = '' if self.is_p2 else '\''
        p3 = '' if self.is_p3 else '\''
        p4 = '' if self.is_p4 else '\''
        item = "SS" if self.item_type == "Special Serenade" else self.item_type[0]
        return f"<{self.ticket_number}: {self.recipient_name} {self.p1}{p1} {self.p2}{p2} {self.p3}{p3} {self.p4}{p4} {item}>"
        # return f"<{self.chosen_period}-{self.chosen_classroom} {special}>"


class TicketList(list):
    def has_item_type(self, items=None) -> bool:
        # checks if a list of tickets contains any ticket with a given item type(s)
        for ticket in self:
            if ticket.item_type in items:
                return True
        return False

    @property
    def has_serenades(self):
        return self.has_item_type(('Serenade', 'Special Serenade'))

    @property
    def has_non_serenades(self):
        return self.has_item_type(('Chocolate', 'Rose'))

    def num_items(self, items: tuple) -> int:
        # returns the number of serenades (including special) in a list of tickets
        count = 0
        for ticket in self:
            if ticket.item_type in items:
                count += 1
        return count

    @property
    def num_serenades(self):
        return self.num_items(("Serenade", "Special Serenade"))

    def sort_by_person(self):
        self.sort(key=lambda ticket: ticket.item_type)
        self.sort(key=lambda ticket: ticket.recipient_name)


class Classroom:
    # the REGEX used to determine what is a valid classroom name
    # if invalid, classroom will not be visited
    classroom_pattern = r"[A-Z]\d{3}"

    # Lookup dict used to substitute names when cleaning
    SUBSTITUTIONS = {
        'LIBA': 'B101',
        'LIBB': 'B102',
        'LIBC': 'B103',
        'LIBD': 'B104'
    }

    def __init__(self, orignal_name: str, period: int):
        """Variables"""
        self.tickets = TicketList()

        self.period = period

        self.original_name = orignal_name       # the name as it appears on the timetable
        self.clean_name = self.get_clean_name()
        self.extended_name = f"{self.period}-{self.clean_name}"

        self.is_valid = self.verify_classroom_name()

    def __repr__(self):
        return self.extended_name

    def get_clean_name(self):
        if self.original_name in self.SUBSTITUTIONS:
            clean_name = self.SUBSTITUTIONS[self.original_name]
        else:
            dotless_name = self.original_name.replace('.', '')
            clean_name = re.sub("([A-Z])G", r"\g<1>0", dotless_name)
        return clean_name

    def verify_classroom_name(self):
        return re.match(self.classroom_pattern, self.clean_name) is not None

    def choose(self):
        """Make every ticket in this classroom pick this classroom"""
        for ticket in self.tickets:
            ticket.choose_classroom(self)

    @property
    def is_upper_campus(self):
        block = self.clean_name[0]
        return ord(block.upper()) <= ord('G')

    @property
    def must_keep(self):
        for ticket in self.tickets:
            if ticket.has_no_choice():
                return True
        return False


class ClassroomList(list):
    def __contains__(self, classroom: Classroom) -> bool:
        return classroom.original_name in map(lambda existing_classroom: existing_classroom.original_name, self)

    def __init__(self, *args):
        tickets = TicketList(*args)
        self.generate_classrooms(tickets)
        super().__init__(self)

    def generate_classrooms(self, tickets: TicketList):
        for ticket in tickets:
            for period in range(1, 5):
                classroom_name = getattr(ticket, f"p{period}")
                new_classroom = Classroom(classroom_name, period)
                if new_classroom.is_valid:
                    if new_classroom in self:
                        existing_classroom = self.get_classroom(new_classroom)
                        existing_classroom.tickets.append(ticket)
                        setattr(ticket, f"p{period}", existing_classroom)
                    else:
                        new_classroom.tickets.append(ticket)
                        setattr(ticket, f"p{period}", new_classroom)
                        self.append(new_classroom)

    def get_classroom(self, new_classroom: Classroom):
        for classroom in self:
            if classroom.original_name == new_classroom.original_name:
                return classroom
        raise KeyError("Classroom not found.")

    @property
    def sorted_by_length(self) -> list:
        return sorted(self, key=lambda classroom: len(classroom.tickets))

    @property
    def with_serenades(self) -> list:
        # classrooms that contain at least one serenade
        return [classroom for classroom in self if classroom.has_serenades()]

    @property
    def without_serenades(self) -> list:
        # classrooms that contain ZERO serenades
        return [classroom for classroom in self if not classroom.has_serenades()]

    @property
    def grouped_by_length(self) -> dict:
        """
        Key: number of tickets in a given classroom
        Value: list of classrooms with that many tickets
        E.g. {0: ["1-A204", "3-I115"], 1: ["1-F101", "2-G101"]}
        """
        classrooms_by_length = {}
        for classroom in self:
            tickets = classroom.tickets
            length = len(tickets)
            if length in classrooms_by_length:
                classrooms_by_length[length].append(classroom)
            else:
                classrooms_by_length[length] = [classroom]
        return classrooms_by_length

    @staticmethod
    def split(a, n):
        k, m = divmod(len(a), n)
        return list((a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)))


class Group:
    def __init__(self, number: int, is_serenaders: bool):
        self.is_serenaders = is_serenaders
        self.number = number
        self.tickets = TicketList()

    @property
    def name(self):
        initial = "S" if self.is_serenaders else "N"
        return f"{initial}{self.number}"


class TicketSorter:
    def __init__(self, tickets: list, serenading_groups: int, non_serenading_groups: int,
                 max_serenades_per_class: int = 5, max_non_serenades_per_serenading_class: int = 0,
                 extra_special_serenades: bool = True, no_free_loaders: bool = True):
        """Options"""
        # if true, special serenades will not be grouped with regular serenades (ignores non-serenades)
        # if true, more classes need to be visited (not significantly) but periods are more evenly distributed (usually)
        # not guaranteed. sometimes there is no choice
        self.EXTRA_SPECIAL_SERENADES = extra_special_serenades

        # increasing these values increases the efficiency (decreases class visits required)
        # however, too a high a value make class visits fat (more than 20 items to hand out per class)
        # the max number of serenades in a class (ignores non-serenades)
        self.MAX_SERENADES_PER_CLASS = max_serenades_per_class

        # the max number of non-serenade items in a class (only for classes with at least one serenade)
        # if too much work for serenading groups, and not enough for non-serenading groups decrease this number
        # and vice versa
        self.MAX_NON_SERENADES_PER_SERENADING_CLASS = max_non_serenades_per_serenading_class

        # if a classroom has a serenade, kick out anyone who only receives non-serenades
        # lightens the load on serenading groups
        # decreases efficiency if enabled
        self.NO_FREELOADERS_IN_SERENADING_CLASS = no_free_loaders

        """Constants"""
        # these two are mutually exclusive (you cannot be both a serenading group AND a non-serenading group)
        self.NUM_SERENADING_GROUPS = serenading_groups  # the number of serenading groups
        self.NUM_NON_SERENADING_GROUPS = non_serenading_groups  # the number of groups which are NOT serenading

        """Variables"""
        # List of every ticket
        self.tickets = TicketList(tickets)
        # Key: every classroom separate by the period (e.g. 1-I1.17)
        # Value: a list of every Ticket object in that classroom
        self.classrooms = ClassroomList(self.tickets)
        # tickets which have been moved in self.distribute_doubleups()
        # keeps track to prevent them from being moved again in self.balance_periods()
        self.distributed_tickets = []
        # dicts with period as key and values are list of tickets by grouped
        self.non_serenading_groups_per_period = {}
        self.serenading_groups_per_period = {}

        """Output"""
        # a list where each element represents a group
        # each group is a list of tickets in order
        self.output_serenading_groups_tickets = []
        self.output_non_serenading_groups_tickets = []

        """Utility"""
        self.kicked_freeloaders = 0
        self.non_kicked_freeloaders = 0

        """Methods"""
        # Critical methods must be kept or else the algorithm will fail
        # Important methods improve the algorithm but you could live without them
        # Recommended methods don't have a meaningful impact but are nice to have
        # Optional methods usually reduce efficiency but make it better for the recipients and delivery groups
        # You may turn off optional methods if you wish to improve efficiency
        """self.get_all_classrooms()                               # critical
        if self.EXTRA_SPECIAL_SERENADES:
            self.make_special_serenades_extra_special()         # optional
        self.limit_serenades_per_class()                        # optional
        self.limit_non_serenades_per_serenading_class()         # optional
        self.eliminate_classrooms_with_serenades()              # critical
        self.eliminate_classrooms_without_serenades()           # critical
        self.distribute_doubleups()                             # optional
        self.balance_periods()                                  # optional
        self.assign_tickets_to_groups()                         # important"""

        # print(f"Kicked: {self.kicked_freeloaders} Not Kicked: {self.non_kicked_freeloaders}")

        """
        How the algorithm works
        1. Assume that classes in different periods are just completely different classes
           (i.e. flatten temporal dimension into spatial dimension)
        2. Assume that every person is at all four of their classes at once (at every period simultaneously)
        3. Sort the classes by the number of tickets in that class
        4. For each class, starting from those with the least tickets, do one of two things:
           LOCK: If there is a ticket in this class that has no other choice (e.g. special serenade), it must be 
                 visited. Therefore, every other ticket in that class should stay there. Delete every other class for 
                 these people.
           DELETE: If there is a class where everyone inside could be in a different class, delete this classroom and
                   move on.
        5. As step 4 continues for more classes, the number of choices decreases until everyone is only at one class.
        
        Note: There are also additional steps like limiting serenades per class, enabling extra special serenades and 
            period balancing
        
        
        Strengths:
        -Minimises the number of class visits required
        -Each class is interrupted max 1 time per period
        -Fairly even distribution of items between periods (<5% disparity between emptiest and fullest period)
        
        Weaknesses:
        -For people who receive multiple items, about 40% receive all of them at once, 
            and about 50% receive them across 2 periods.
        -Each class visit is very big, averaging about 6 items per class
        -Most of the handing out is done by serenading groups
        
        Note: numbers were based on 2022 practice dataset of 931 tickets
        
        Possible Future Improvements:
        -limit_serenades_per_class, limit_non_serenades_per_serenading_class, and balance_periods are arbitrary in the
            order that they go through the tickets. this could be made less intelligent by doing it in an order which
            ensures a more balanced distribution or more efficiency
        -the additional steps (distribute_doubleups, limit_serenades_per_class, 
            limit_non_serenades_per_serenading_class, and balance_periods) are all done separately and could be more 
            efficient if a more holistic approach is used, which lets them communicate which each other
        """

    def get_all_classrooms(self):
        """
        Goes through every ticket and adds its classrooms to a dict
        Key: classroom_name
        Value: list of tickets that have that classroom
        E.g. {"1-F101": [TICKET, TICKET, TICKET]}
        """
        # first sort the tickets by the recipient's ID
        # self.tickets.sort(key=lambda a: a.recipient_id)

        for ticket in self.tickets:
            for period in range(1, 5):
                is_period = getattr(ticket, f'is_p{period}')
                classroom = getattr(ticket, f'p{period}')
                if is_period:
                    if classroom not in self.classrooms:
                        self.classrooms[classroom] = [ticket]
                    else:
                        self.classrooms[classroom].append(ticket)
                else:
                    if classroom not in self.classrooms:
                        self.classrooms[classroom] = []

    def make_special_serenades_extra_special(self):
        # ensures that special serenades are not grouped with regular serenades
        for ticket in self.tickets:
            if ticket.item_type == "Special Serenade":
                classroom = getattr(ticket, f"p{ticket.chosen_period}")
                for other_ticket in self.classrooms[classroom][:]:
                    if other_ticket.item_type == "Serenade":
                        if not other_ticket.has_no_choice():
                            setattr(other_ticket, f"is_p{ticket.chosen_period}", False)
                            self.classrooms[classroom].remove(other_ticket)
                        else:
                            # print(f"{ticket.recipient} cannot have an extra special serenade :(")
                            pass

    def limit_serenades_per_class(self):
        # ensures that each class doesn't have more than x number of serenades
        classrooms = reversed(self.classrooms_sorted_by_length)
        for classroom in classrooms:
            period = int(classroom[0])
            tickets = self.classrooms[classroom]
            serenade_count = self.items_per_classroom(tickets, ['Serenade', 'Special Serenade'])
            if serenade_count > self.MAX_SERENADES_PER_CLASS:
                for ticket in tickets:
                    if ticket.item_type == "Serenade":
                        if not ticket.has_no_choice():
                            setattr(ticket, f"is_p{period}", False)
                            self.classrooms[classroom].remove(ticket)
                            serenade_count -= 1
                            if serenade_count <= self.MAX_SERENADES_PER_CLASS:
                                break

    def limit_non_serenades_per_serenading_class(self):
        # only happens if a class has serenades (unlimited non-serenades per class for non-serenading groups)
        # limits the number of non-serenading items in these classes
        classrooms = reversed(self.classrooms_sorted_by_length)
        for classroom in classrooms:
            period = int(classroom[0])
            tickets = self.classrooms[classroom]
            if self.has_item_type(tickets, ['Serenade', 'Special Serenade']):
                non_serenade_count = self.items_per_classroom(tickets, ['Chocolate', 'Rose'])
                if non_serenade_count > self.MAX_NON_SERENADES_PER_SERENADING_CLASS:
                    for ticket in tickets:
                        if ticket.item_type in ['Chocolate', 'Rose']:
                            if not ticket.has_no_choice():
                                setattr(ticket, f"is_p{period}", False)
                                self.classrooms[classroom].remove(ticket)
                                non_serenade_count -= 1
                                if non_serenade_count <= self.MAX_NON_SERENADES_PER_SERENADING_CLASS:
                                    break

    def eliminate_classrooms_with_serenades(self):
        self.eliminate_classrooms(self.classrooms_with_serenades, True)

    def eliminate_classrooms_without_serenades(self):
        self.eliminate_classrooms(self.classrooms_without_serenades, False)

    def eliminate_classrooms(self, all_classrooms: dict, are_serenading_classes: bool):
        for length, classrooms in self.group_classrooms_by_length(all_classrooms).items():
            # ensures that if classrooms have equal length, the classrooms in full periods are removed first
            classrooms_sorted_by_period_serenades = \
                sorted(classrooms,
                       key=lambda class_room: self.get_items_per_period(['Serenade', 'Special Serenade'])
                       [int(class_room[0])], reverse=True)

            # first remove freeloaders
            if self.NO_FREELOADERS_IN_SERENADING_CLASS and are_serenading_classes:
                # only need to ban freeloaders if serenading and enabled

                for classroom in classrooms_sorted_by_period_serenades:
                    period = int(classroom[0])
                    tickets = self.classrooms[classroom]

                    people_with_serenades = {ticket.recipient_name for ticket in tickets
                                             if ticket.item_type in ['Serenade', 'Special Serenade']}
                    for ticket in tickets[:]:
                        if ticket.recipient_name in people_with_serenades:
                            # if person has a serenade, they stay in the class
                            ticket.choose_period(period)
                            self.choose_classroom(ticket, classroom)
                        else:
                            if not ticket.has_no_choice():
                                self.kicked_freeloaders += 1
                                # if a person has no serenades, they are a freeloader. KICK EM OUT
                                setattr(ticket, f'is_p{period}', False)
                                tickets.remove(ticket)
                            else:
                                self.non_kicked_freeloaders += 1

            # systematically removes tickets from classes, starting from the emptiest classes first
            for classroom in classrooms_sorted_by_period_serenades:
                period = int(classroom[0])
                tickets = self.classrooms[classroom]

                # determines if at least one ticket in this class must be at this classroom
                must_keep_classroom = self.must_keep_classroom(tickets)

                if must_keep_classroom:
                    # if classroom must be kept, make every other ticket stay in this class
                    for ticket in tickets:
                        ticket.choose_period(period)
                        self.choose_classroom(ticket, classroom)
                else:
                    # if classroom can be destroyed, remove tickets associated with it
                    # (destroy the actual classroom later)
                    for ticket in tickets[:]:
                        setattr(ticket, f'is_p{period}', False)
                        tickets.remove(ticket)

        self.cleanup_classrooms()

    def cleanup_classrooms(self):
        # delete empty classrooms from the dict
        for classroom in self.classrooms_sorted_by_length[:]:
            if len(self.classrooms[classroom]) < 1:
                del (self.classrooms[classroom])

    def sort_tickets_within_classroom_by_person(self):
        # ensures that within a classroom, the tickets are sorted
        # sorts by person, then by item type if same person
        for tickets in self.classrooms.values():
            # sort by person, then item type if same person
            tickets.sort(key=lambda a: a.item_type)
            tickets.sort(key=lambda a: a.recipient_name)

    def distribute_doubleups(self):
        # if a person is getting multiple things at once,
        # try to distribute their items WITHOUT increasing the number of classrooms to visit

        self.sort_tickets_within_classroom_by_person()
        for classroom in self.classrooms_sorted_by_length:
            tickets = self.classrooms[classroom]
            # group tickets based on the person
            # requires that the tickets be in order first (tickets of the same people are consecutive)
            for person, same_person in groupby(tickets, lambda a: a.recipient_name):
                tickets_of_same_person = list(same_person)
                if len(tickets_of_same_person) > 1:  # if someone is receiving more than 1 ticket
                    # group the person's tickets based on their item type
                    tickets_of_same_person.sort(key=lambda a: a.item_type)
                    # get all the possible classrooms that the person could be at
                    possible_classrooms = self.get_possible_classrooms(tickets_of_same_person[0])

                    # if there are valid alternative classrooms, move some tickets there
                    if len(possible_classrooms) > 1:
                        for ticket_num, ticket in enumerate(tickets_of_same_person):
                            # loops through the possible classrooms and evenly distributes among them
                            original_classroom = ticket.chosen_classroom
                            chosen_classroom = possible_classrooms[(ticket_num % len(possible_classrooms))]
                            if chosen_classroom != original_classroom:  # if not the same class
                                # change the period of the ticket
                                chosen_period = int(chosen_classroom[0])
                                ticket.choose_period(chosen_period)
                                # change the class of the ticket
                                self.classrooms[chosen_classroom].append(ticket)
                                self.classrooms[original_classroom].remove(ticket)
                                self.distributed_tickets.append(ticket)
                                # print(f"Distributed {ticket} from {original_classroom} to {chosen_classroom}")
        # do this again because distributing probs messed it up
        self.sort_tickets_within_classroom_by_person()

    def get_possible_classrooms(self, ticket: Ticket):
        # gets all the classrooms that the ticket has that are also still available (haven't been deleted)
        possible_classrooms = []
        for period in range(1, 5):
            possible_classroom = getattr(ticket, f"p{period}")
            if possible_classroom in self.classrooms_sorted_by_length:
                possible_classrooms.append(possible_classroom)
        # random.shuffle(possible_classrooms)
        return possible_classrooms

    def get_items_per_period(self, items=None):
        """
        Gets the number of a given item per period
        E.g. items = ["Serenades", "Special Serenades"] and function returns how many of those items per period
        Key: period
        Value: number of that given item(s)
        """
        if items is None:
            items = ['Chocolate', 'Rose', 'Serenade', 'Special Serenade']  # default to all of them

        items_per_period = {1: 0, 2: 0, 3: 0, 4: 0}
        for classroom, tickets in self.classrooms.items():
            period = int(classroom[0])
            for ticket in tickets:
                if ticket.item_type in items:
                    items_per_period[period] += 1
        # sorts in ascending order
        items_per_period = {period: items_per_period[period] for period in
                            sorted(items_per_period.keys(), key=lambda a: items_per_period[a])}
        return items_per_period

    def balance_periods(self):
        # first balance by serenades
        items = ['Serenade', 'Special Serenade']
        while True:
            original_period_sizes = self.get_items_per_period(items)
            self.balance_periods_by_items(items, items)
            new_period_sizes = self.get_items_per_period(items)
            # repeat until there is no change
            if original_period_sizes == new_period_sizes:
                break

        # do the same but for non-serenades
        items = ['Chocolate', 'Rose', 'Serenade', 'Special Serenade']
        while True:
            original_period_sizes = self.get_items_per_period(items)
            self.balance_periods_by_items(['Chocolate', 'Rose'], items)
            new_period_sizes = self.get_items_per_period(items)
            # print(original_period_sizes)
            # repeat until there is no change
            if original_period_sizes == new_period_sizes:
                break

        self.sort_tickets_within_classroom_by_person()

    def balance_periods_by_items(self, items_to_move: list, items_to_count: list):
        # items to move: which items can be moved
        # items to count: which items are considered when determining the fullest period
        period_sizes = self.get_items_per_period(items_to_count)
        # reversed so people are moved from the fullest classes first
        classrooms_sorted = reversed(self.classrooms_sorted_by_length)

        # fix the disparity
        for classroom in classrooms_sorted:
            # calculate how much disparity there is between periods, and break if there is none
            period_sizes = self.get_items_per_period(items_to_count)
            fullest_period = max(period_sizes, key=lambda a: period_sizes[a])
            emptiest_period = min(period_sizes, key=lambda a: period_sizes[a])
            difference = period_sizes[fullest_period] - period_sizes[emptiest_period]
            if difference <= 1:
                break

            emptier_periods = []
            for period, period_size in period_sizes.items():
                if period_size < period_sizes[fullest_period]:
                    emptier_periods.append(period)

            fullest_periods = []
            for period, period_size in period_sizes.items():
                if period_size >= period_sizes[fullest_period]:
                    fullest_periods.append(period)

            period = int(classroom[0])
            if period in fullest_periods:
                # if the fullest period, take from that one, otherwise don't
                tickets = self.classrooms[classroom]
                for ticket in tickets:  # for every ticket that is in the fullest period
                    if ticket.item_type in items_to_move:  # if ticket is specified item
                        if ticket not in self.distributed_tickets:  # don't touch already moved tickets
                            # if the ticket can be moved
                            possible_classrooms = self.get_possible_classrooms(ticket)
                            if len(possible_classrooms) > 1:
                                # get a list of possible periods the ticket could be moved to (Um9iIDIwMjI=)
                                possible_periods = {int(a[0]): a for a in possible_classrooms}
                                # try moving the ticket to the emptiest periods first
                                for emptier_period in emptier_periods:
                                    if emptier_period in possible_periods:
                                        new_classroom = possible_periods[emptier_period]

                                        if self.EXTRA_SPECIAL_SERENADES and \
                                                ticket.item_type == "Serenade" and self.has_item_type(
                                                self.classrooms[new_classroom], ['Special Serenade']):
                                            continue   # don't allow serenades to be moved into special serenade classes

                                        # move the ticket
                                        original_classroom = ticket.chosen_classroom
                                        ticket.choose_period(emptier_period)
                                        self.classrooms[original_classroom].remove(ticket)
                                        self.classrooms[new_classroom].append(ticket)
                                        # print(f"Moved {ticket} from {original_classroom} to {new_classroom}")
                                        break
                    if not self.is_biggest_period(fullest_period, items_to_count):
                        break

        self.cleanup_classrooms()

    def is_biggest_period(self, biggest_period: int, items: list = None) -> bool:
        # determines if the given period has more items than every other period

        # items defines which items are counted when determining the biggest period
        if items is None:
            items = ['Chocolate', 'Rose', 'Serenade', 'Special Serenade']

        period_sizes = self.get_items_per_period(items)
        for period in period_sizes:
            if period != biggest_period:
                if period_sizes[period] >= period_sizes[biggest_period]:
                    return False
        return True

    def assign_tickets_to_groups(self):  # sort by special serenades, then alphabetically
        # sort by whether a class has any serenades or not
        classrooms_sorted_by_has_serenade = \
            sorted(self.classrooms_sorted_by_length,
                   key=lambda class_room: not self.has_item_type(self.classrooms[class_room]))

        # keeps track of at what point the serenades stop
        no_serenade_index = 0
        for classroom in classrooms_sorted_by_has_serenade:
            if not self.has_item_type(self.classrooms[classroom], ['Serenade', 'Special Serenade']):
                break
            no_serenade_index += 1

        # Divides the classrooms into categories: whether a classroom has serenades or not
        classrooms_with_serenades = classrooms_sorted_by_has_serenade[:no_serenade_index]
        classrooms_without_serenades = classrooms_sorted_by_has_serenade[no_serenade_index:]
        self.serenading_groups_per_period = self.get_distributed_classrooms_by_period(classrooms_with_serenades, True)
        self.non_serenading_groups_per_period = \
            self.get_distributed_classrooms_by_period(classrooms_without_serenades, False)

        # gives each group a set of classrooms from each period
        self.output_serenading_groups_tickets = \
            self.assign_tickets_to_groups_by_period(self.serenading_groups_per_period, self.NUM_SERENADING_GROUPS)
        self.output_non_serenading_groups_tickets = \
            self.assign_tickets_to_groups_by_period(self.non_serenading_groups_per_period,
                                                    self.NUM_NON_SERENADING_GROUPS)

    def get_distributed_classrooms_by_period(self, classrooms: list, has_serenades: bool) -> dict:
        classrooms = sorted(classrooms)
        num_groups = self.NUM_SERENADING_GROUPS if has_serenades else self.NUM_NON_SERENADING_GROUPS
        # tickets = [ticket for classroom in classrooms for ticket in self.classrooms[classroom]]

        groups_per_period = {1: [], 2: [], 3: [], 4: []}

        # for each period
        for period, (key, classrooms_in_period) in enumerate(groupby(classrooms, key=lambda classroom: classroom[0])):
            period = period + 1
            classrooms_in_period = list(classrooms_in_period)
            num_tickets_in_period = len(
                    [ticket for classroom in classrooms_in_period for ticket in self.classrooms[classroom]])

            # splits the classrooms into two groups based on if they are upper or lower campus
            # index = 0 is upper campus, index = 1 is lower campus
            classrooms_per_campus = [list(classrooms_in_campus) for key, classrooms_in_campus in
                                     groupby(classrooms_in_period, key=lambda classroom:
                                     ord(classroom[2].upper()) > self.LAST_UPPER_CAMPUS_BLOCK_ASCII_CODE)]
            num_tickets_per_campus = []
            num_groups_per_campus = []

            if len(classrooms_per_campus) > 1:
                for classrooms_in_campus in classrooms_per_campus:
                    # gets the number of tickets in this campus
                    num_tickets_in_campus = len(
                        [ticket for classroom in classrooms_in_campus for ticket in self.classrooms[classroom]])
                    num_tickets_per_campus.append(num_tickets_in_campus)

                    # allocates a number of groups to this campus based on the number of tickets
                    num_groups_in_campus = round(num_tickets_in_campus / num_tickets_in_period * num_groups)
                    # ensures that each campus has at least 1 group even if it was rounded to 0
                    num_groups_in_campus = min(num_groups_in_campus, num_groups - 1)
                    num_groups_in_campus = max(num_groups_in_campus, 1)

                    num_groups_per_campus.append(num_groups_in_campus)

                # fixes rounding issues
                if num_groups_per_campus[0] + num_groups_per_campus[1] < num_groups:
                    campus_with_least_groups = min(range(len(num_groups_per_campus)),
                                                   key=num_groups_per_campus.__getitem__)
                    num_groups_per_campus[campus_with_least_groups] += 1
                if num_groups_per_campus[0] + num_groups_per_campus[1] > num_groups:
                    campus_with_least_groups = max(range(len(num_groups_per_campus)),
                                                   key=num_groups_per_campus.__getitem__)
                    num_groups_per_campus[campus_with_least_groups] -= 1

                """This part is highly inefficient because it evenly splits the classrooms without considering how many
                tickets are inside it"""
                groups_per_period[period].extend(self.split(classrooms_per_campus[0], num_groups_per_campus[0]))
                groups_per_period[period].extend(self.split(classrooms_per_campus[1], num_groups_per_campus[1]))
            else:
                groups_per_period[period].extend(self.split(classrooms_per_campus[0], num_groups_per_campus[0]))

        return groups_per_period

    def assign_tickets_to_groups_by_period(self, groups_per_period: dict, num_groups: int):
        # assign classes to groups by randomly picking a set of classes from each period
        groups_tickets = []
        groups_classrooms = []

        # for period 1, it doesn't matter how it's chosen so just copy it over
        groups_classrooms.extend(groups_per_period[1])

        # for periods 2-4, give the emptiest group the biggest sets
        for period in range(2, 5):
            for group_index in range(num_groups):
                emptiest_existing_group = min(groups_classrooms, key=lambda a: self.get_group_size(a))
                fullest_possible_group = max(groups_per_period[period], key=lambda a: self.get_group_size(a))
                emptiest_existing_group.extend(fullest_possible_group)
                groups_per_period[period].remove(fullest_possible_group)

        # convert classrooms into tickets
        for group in groups_classrooms:
            group_tickets = []
            for classroom in group:
                group_tickets.extend([ticket for ticket in self.classrooms[classroom]])
            groups_tickets.append(group_tickets)

        return groups_tickets


def get_int(prompt: str) -> int:
    while True:
        try:
            answer = int(input(prompt))
            return answer
        except ValueError:
            print("Please input an integer.")


def get_bool(prompt: str) -> bool:
    while True:
        answer = input(prompt)
        if answer.upper() in ["Y", "YES", "1"]:
            return True
        elif answer.upper() in ["N", "NO", "0"]:
            return False
        else:
            print("Please enter 'yes' or 'no'.")


def load_tickets() -> dict:
    file_names = glob(f'{Folders.tickets}*.json')
    if len(file_names) < 1:
        print("ERROR: No ticket files detected.")
        input("Press enter to acknowledge...")

    tickets_json = {}
    for file_name in file_names:
        with open(file_name) as file:
            new_tickets = json.load(file)
            for key in new_tickets:
                if key in tickets_json.keys():
                    print(f"WARNING: When loading {file_name}, "
                          f"ticket number {key} ({new_tickets[key]['Recipient Name']}) already existed. "
                          f"The ticket will be overwritten.")
            tickets_json.update(new_tickets)
    return tickets_json


def load_classes() -> dict:
    classes = {}
    if os.path.exists(Files.student_classes):
        with open(Files.student_classes) as file:
            reader = csv.reader(file)
            for line in reader:
                classes[line[0]] = {'P1': line[1], 'P2': line[2], 'P3': line[3], 'P4': line[4]}
        return classes
    else:
        print(f"ERROR: {Files.student_classes} not detected. "
              f"Have you run parse_classes.py yet? You must do so before you run this script.")
        input("Press enter to acknowledge...")


def create_tickets(tickets_json: dict, classes: dict):
    tickets = []
    for ticket_number, values in tickets_json.items():
        recipient_name = values['Recipient Name']
        recipient_classes = classes[recipient_name]
        item_type = values['Item Type']
        ticket = Ticket(ticket_number, recipient_name, item_type, recipient_classes['P1'],
                        recipient_classes['P2'], recipient_classes['P3'], recipient_classes['P4'])
        if item_type == "Special Serenade":
            period = values['Period']
            ticket.choose_period(period)
        tickets.append(ticket)
    return tickets


def write_tickets(tickets: list):
    with open(f"{Folders.output}{Files.tickets_sorted}", 'w') as file:
        fieldnames = ["Ticket Number", "Chosen Period", "Chosen Classroom", "Group"]
        writer = csv.DictWriter(file, fieldnames, extrasaction='ignore')
        writer.writeheader()
        tickets_sorted_by_number = sorted(tickets, key=lambda a: int(a.ticket_number))
        for ticket in tickets_sorted_by_number:
            writer.writerow(ticket.as_dict())


def write_group_tickets(tickets: list, group_prefix: str):
    fieldnames = ["Ticket Number", "Chosen Period", "Chosen Classroom", "Recipient Name",
                  "Item Type", "P1", "P2", "P3", "P4"]
    for number, group in enumerate(tickets):
        group_name = f"{group_prefix}{number + 1}"
        with open(f"{Folders.output}{group_name}.csv", 'w') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            for ticket in group:
                ticket.group = group_name
                writer.writerow(ticket.as_dict())


def print_statistics(ticket_sorter: TicketSorter):
    print("\nNumber of Classroom Visits:")
    classrooms_per_period = {1: 0, 2: 0, 3: 0, 4: 0}
    for classroom in ticket_sorter.classrooms:
        period = int(classroom[0])
        classrooms_per_period[period] += 1
    for period, number in classrooms_per_period.items():
        print(f"\tPeriod {period}: {number}")
    print(f"Total: {len(ticket_sorter.classrooms)}")

    print("\nNumber of Tickets:")
    item_type_distribution = {"Chocolate": 0, "Rose": 0, "Serenade": 0, "Special Serenade": 0}
    for ticket in ticket_sorter.tickets:
        item_type_distribution[ticket.item_type] += 1
    for item_type, number in item_type_distribution.items():
        print(f"\t{item_type}: {number}")
    print(f"Total: {len(ticket_sorter.tickets)}")

    print("\nNumber of items per classroom visit "
          "(left is number of items, right is number of classrooms with that many items):")
    classroom_size_distribution = {size: len(ticket_sorter.classrooms_grouped_by_length[size])
                                   for size in sorted(ticket_sorter.classrooms_grouped_by_length.keys())}
    total = 0
    for size, num_classrooms in classroom_size_distribution.items():
        print(f"\t{size}: {num_classrooms}")
        total += size * num_classrooms
    average_classroom_size = round(total / len(ticket_sorter.classrooms), 3)
    print(f"Average: {average_classroom_size}")

    print("\nTickets per serenading group:")
    for group in ticket_sorter.output_serenading_groups_tickets:
        num_serenades = 0
        num_non_serenades = 0
        for ticket in group:
            if ticket.item_type == "Serenade" or ticket.item_type == "Special Serenade":
                num_serenades += 1
            else:
                num_non_serenades += 1
        num_classrooms = len([classrooms for key, classrooms in groupby(group, key=lambda a: a.chosen_classroom)])
        print(f"\tClassrooms: {num_classrooms} || Serenades: {num_serenades} + Non-serenades: {num_non_serenades}")

    print("\nTickets per non-serenading group:")
    for group in ticket_sorter.output_non_serenading_groups_tickets:
        num_classrooms = len([classrooms for key, classrooms in groupby(group, key=lambda a: a.chosen_classroom)])
        print(f"\tClassrooms: {num_classrooms} || Non-serenades: {len(group)}")


def main():
    # load data
    tickets_json = load_tickets()
    classes = load_classes()
    tickets = create_tickets(tickets_json, classes)

    # get options
    """num_serenading_groups = get_int("Number of Serenading Groups: ")
    num_non_serenading_groups = get_int("Number of Non-Serenading Groups: ")
    max_serenades_per_class = get_int("Maximum number of serenades per class: ")
    # max_non_serenades_per_class = get_int("Maximum number of non-serenades per class "
    #                                       "(only if class has at least one serenade): ")
    max_non_serenades_per_class = 0
    extra_special_serenades = get_bool("Prevent special serenades from being grouped with regular serenades? (Y/N): ")

    # sort the tickets
    ticket_sorter = TicketSorter(tickets, num_serenading_groups, num_non_serenading_groups, max_serenades_per_class,
                                 max_non_serenades_per_class, extra_special_serenades)"""

    ticket_sorter = TicketSorter(tickets, 10, 10)

    # delete existing tickets if they already exist
    files = [f for f in os.listdir(Folders.output) if os.path.isfile(os.path.join(Folders.output, f))]
    if len(files) > 0:
        print("WARNING: Residue output files have been detected (likely from a previous run). "
              "These files will be deleted if you continue. Stop the script now if you would like to keep them.")
        input("\nPress enter to continue...")
        for file in files:
            if file.endswith(".csv"):
                os.remove(f"{Folders.output}{file}")

    # write tickets
    write_group_tickets(ticket_sorter.output_serenading_groups_tickets, 'S')
    write_group_tickets(ticket_sorter.output_non_serenading_groups_tickets, 'N')
    write_tickets(ticket_sorter.tickets)

    # print statistics
    print_statistics(ticket_sorter)

    input("\nPress enter to exit...")


if __name__ == "__main__":
    main()
