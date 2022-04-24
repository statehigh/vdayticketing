import os


class Folders:
    static_website_resources = "static/"        # files used for the website. should not be modified
    timetables = "timetables/"                  # list of csv files with timetables of each year level
    tickets = "tickets/"                        # list of csv files representing tickets inputted using the website
    output = "output/"                          # the csv files containing the sorted tickets

    """All methods need to end with __ or else dir(self) will think it's an attribute"""
    def verify_dirs__(self):
        # verifies that every directory listed in DirectoryLocations exists, and creates them if it doesn't
        for attribute in dir(self):
            if not attribute.endswith('__'):   # removes random other attributes
                directory = getattr(self, attribute)
                if not os.path.exists(directory):
                    os.mkdir(directory)


class Files:
    student_names = "student_names.json"        # a list of names which you load into the ticket inputter website
    student_classes = "student_classes.csv"     # the csv file containing the parsed timetables of each year level
    tickets_sorted = "tickets_sorted.csv"       # the master list of all the tickets with their period chosen


Folders().verify_dirs__()
