# Valentine's Day Ticketing System

## Setup
One person needs to be the host, and everyone else is an inputter.
- Host: sets up the system and runs the scripts.
- Inputter: inputs the tickets into the systems.

If you would like to test the system, you can run *generate_dataset.py* to generate a fake dataset of people, timetables and tickets.

## Instructions for Host
1. Download this repository.
2. Install [Python 3.8.9](https://www.python.org/downloads/) or newer.
3. Download each year level timetable as a PDF (will require a teacher).
4. Using [Adobe Acrobat](https://www.adobe.com/au/acrobat/online/pdf-to-excel.html), convert the PDFs to Excel files.
5. Open the files in Excel and [convert them to CSV files](https://support.microsoft.com/en-us/office/import-or-export-text-txt-or-csv-files-5250ac4c-663c-47ce-937b-339e391393ba).
6. Place CSV files in folder called *timetables*.
7. [Run the script](https://pythonbasics.org/execute-python-scripts/) *parse_classes.py*, which should generate two files: *student_classes.csv* and *student_names.json*.
8. Send *student_names.json* to every Inputter and wait for them to return you a tickets list file.
9. Place the ticket list files into the folder called *tickets*.
10. Run the script *sort_tickets.py*. [See below](#settings-in-sort_ticketspy) for explanation on what the questions mean.
 - It should generate some files inside the *output* folder: *tickets_sorted.csv* and a bunch of CSV files corresponding to each group 
   - Groups are numbered, with serenading and non-serenading groups numbered independently.
   - Serenading groups have the prefix *S*.
   - Non-serenading groups have the prefix *N*.
   - Example: *S1.csv*
12. Using *tickets_sorted.csv*, go through every ticket, writing down the chosen period and sorting it into a pile which corresponds to the group it is allocated to. 
 - The file contains every ticket and the corresponding group it belongs to in order of ticket number.
 - Make sure each pile is labelled with the group it corresponds to.
13. For each pile, look at the corresponding CSV file (e.g., *A.csv*) and sort the tickets into the order shown in the file. 
 - The tickets are grouped by period and sorted by geographical location, with special serenades placed first.

## Instructions for Inputter
1. The host should have sent you a file called *student_names.json*. Save this file.
2. Go to https://statehigh.github.io/vdayticketing/
3. Load the *student_names.json* file you had just saved.
4. Add every ticket you have.
5. Press the download button and send the file you downloaded to the host.

## An Explanation of *sort_tickets.py*
The ticket sorting algorithm attempts to maximise efficiency by grouping tickets together by class - this minimises the number of classroom visits required (a more technical explanation of how can be found inside the script file). However, maximising efficiency at all costs can result in some classes receiving 20+ tickets at once. Therefore, some limitations were put in place to more evenly distribute the tickets. The limitations are a compromise a more even distribution is less efficient. Hence, they can be adjusted with settings to reach a balance. These settings can be found below.

## Settings in *sort_tickets.py*
1. Number of serenading groups
 - The number of groups which can distribute tickets who can also do serenades.
3. Number of non-serenading groups
 - The number of groups which can distribute tickets but cannot do serenades.
5. Maximum number of serenades per class 
 - Limits the number of serenades which occur in a given class. 
 - Setting this too low will be inefficient but setting it too high may diminish the specialness of a serenade (e.g. if 10 people are being serenaded all at once).
7. Maximum number of non-serenades per class 
 - Limits the number of non-serenade tickets in a given class. 
 - The limit is only enforced if the class has at least one serenade (i.e. only for serenading groups). 
 - Lowering this value will reduce the workload of serenading groups and will increase the workload of non-serenading groups, and vice versa. 
 - It may be worth rerunning the script and tweaking this value until the workload is evenly distributed (based on the number of serenading and non-serenading groups).
9. Prevent special serenades from being grouped with regular serenades
 - If a class has a special serenade, the algorithm will attempt to stop regular serenades from being added to that class. 
 - If a regular serenade has no other class it can go to, it will remain. 
 - If there are other special serenades in that class, they cannot be changed and will remain. 
 - In most circumstances, the special serenade will be the only serenade, hence making it *extra special*.
