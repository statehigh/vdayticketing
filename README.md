# Valentine's Day Ticketing System

## Setup
One person needs to be the host, and everyone else is an inputter
- Host: sets up the system and runs the scripts
- Inputter: inputs the tickets into the systems

## Instructions for Host
1. Download this repository
2. Install [Python 3.8.9](https://www.python.org/downloads/) or newer
3. Download each year level timetable as PDF (will require teacher)
4. Using [Adobe Acrobat](https://www.adobe.com/au/acrobat/online/pdf-to-excel.html), convert PDFs to Excel files
5. Open the files in Excel and [convert them to CSV files](https://support.microsoft.com/en-us/office/import-or-export-text-txt-or-csv-files-5250ac4c-663c-47ce-937b-339e391393ba)
6. Place CSV files in folder called *student_timetables*
7. Run the *student_classes_parser.py* script, which should generate two files: *student_classes.csv* and *student_names.json*
8. Send *student_names.json* to every Inputter and wait for them to return you a tickets list file
9. Place the ticket list files into the folder called *tickets*
10. Run the *ticket_sorter.py* script, which should generate some files inside the *output* folder: *tickets_sorted.csv* and a bunch of CSV files corresponding to each group
11. Sort every (physical) ticket you have into piles using *tickets_sorted.csv*. It contains every ticket and the corresponding group it belongs to in order of ticket number (if the group is a number, it is a serenading group; if it is a letter, it is a non-serenading group). Make sure each pile is labelled with the group it corresponds to.
12. OPTONAL: For each pile, look at the corresponding csv file (e.g., *A.csv*). Sort the tickets into the order shown in the file. It groups tickets by period and sorts them by geographical location, while also prioritising special serenades.
13. Congratulations. You're done.

## Instructions for Inputter
1. The host should have sent you a file called *student_names.json*. Save this file
2. Go to statehigh.github.io/vdayticketing/
3. Load the *student_names.json* file you had just saved
4. Add every ticket you have
5. Press the download button and send the file you downloaded to the host