import json
import gspread
import numpy
import string
import datetime
from oauth2client.service_account import ServiceAccountCredentials
#-------------------------------------------------------------------------------
# What week is now? (1/2/3/4) (for deciding which menu to use)
d = datetime.date.today()
current_week = d.isocalendar()[1] - datetime.date(d.year,d.month,1).isocalendar()[1] + 2

#-------------------------------------------------------------------------------
# Get sheets
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://spreadsheets.google.com/feeds",
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(creds)

# gc = gspread.oauth()
sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1JwWYMajEwihR8-xIfa9aZ7e4WrBuUEdEGDJH2aAj78g")
weekly = sh.worksheet("Main Menu")
additionals = sh.worksheet("Extras")



weekly_grid = numpy.array(weekly.get_all_values())
additionals_grid = numpy.array(additionals.get_all_values())

#-------------------------------------------------------------------------------
# number of coloumns for each meal
breakfast = weekly.find("Breakfast").col
lunch = weekly.find("Lunch").col
snacks = weekly.find("Snacks").col
dinner = weekly.find("Dinner").col

space={"Breakfast":lunch-breakfast,"Lunch":snacks-lunch,"Snacks":dinner-snacks,"Dinner":weekly_grid.shape[1]-snacks}

total_space = sum(space.values())

#-------------------------------------------------------------------------------
# Build object structure

days = ["Sunday", "Monday", "Tuesday",
        "Wednesday", "Thursday", "Friday", "Saturday"]
meals = ["Breakfast", "Lunch", "Snacks", "Dinner"]


regular_items = {day:{meal:[] for meal in meals} for day in days}
extra_items = {day:{meal:[] for meal in meals} for day in days}
daily_items = {meal:[] for meal in meals}


def clean(text: str):
    return text.strip().lower().capitalize()

#-------------------------------------------------------------------------------
# Takes contents of a cell and splits it into multiple
def parse_cell_items(text: str):
    
    # Check for empty input
    if text.strip() == "":
        return []

    # Numbered list
    if text.lstrip().startswith("1."):
        # No other delimiters
        items = []
        for line in text.split("\n"):
            spl = line.lstrip().split(".", 1)
            if len(spl) > 1 and spl[0].isdigit():
                # New item
                if (spl[1].find(',')!=-1):
                    if (spl[1].find('(')!=-1 and spl[1].index('(')<spl[1].index(',')<spl[1].index(')')):
                        pass
                    else:
                        for a in spl[1].split(','):
                            items.append(clean(a))
                else:
                    items.append(clean(spl[1]))
            else:
                # There's a \n in the middle of an item :facepalm:
                # Append it to the previous item
                if spl[0].strip() == "":
                    # Its an empty line in the middle of a numbered list..., double facepalm
                    continue
                items[-1] += " " + clean(spl[0]).replace('\n','')
        return items

    items = []
    delims = ",+\n"
    for delim in delims:
        if delim in text:
            if (text.find('(')!=-1):
                if (text.index('(')<text.index(delim)<text.index(')')):
                    continue
            for item in text.split(delim):
                if item.strip() == "":
                    continue
                items.append(clean(item).replace('\n',''))
            # Assumption: only one delimiter per cell
            break
    else:
        # Single item
        items.append(clean(text).replace('\n',''))
    return items

#-------------------------------------------------------------------------------
# skips empty cells and parses each non-empty cell
def format(item: list):
    l=[]
    for i in item:
        if i == '':
            pass
        else:
            l.extend(parse_cell_items(i))
    return l

#-------------------------------------------------------------------------------
# Fill in the regular_items dict
def parse_regular():

    # BUG:
    #  Lunch doesn't include drinks
    #  Snacks given in Sunday only (handled)

    # if odd week, use top menu, else use bottom menu
    is_even_week = (current_week + 1) % 2

    daily_item_cell = weekly.findall("Daily")[is_even_week]
    daily_items_list = weekly.row_values(daily_item_cell.row)
    #-------------------------------------------------------------------------------
    # mapping daily items to meals (spaces kept in mind)
    daily_items[meals[0]].extend(parse_cell_items(daily_items_list[1]))
    daily_items[meals[1]].extend(parse_cell_items(daily_items_list[1+space[meals[0]]]))
    daily_items[meals[3]].extend(parse_cell_items(daily_items_list[1+space[meals[0]]+space[meals[1]]+space[meals[2]]]))
    #-------------------------------------------------------------------------------
    # extracting items data from sheet according to week
    cell = weekly.findall("Sunday")[is_even_week]
    start_cell = f"{string.ascii_uppercase[cell.col - 1]}{cell.row}"
    end_cell = f"{string.ascii_uppercase[cell.col + total_space -1]}{cell.row + 6}"
    items_grid = numpy.array(weekly.get(f"{start_cell}:{end_cell}"))

    #-------------------------------------------------------------------------------
    snacks = []
    for day_num in range(len(items_grid)):
        day = items_grid[day_num][0]
        index = 1
        for meal in meals:
            item_list = items_grid[day_num][index:index+space[meal]]
            if meal == 'Snacks' and day_num == 0:
                # Snacks present only for Sunday
                snacks.extend(item_list)
            regular_items[day][meal].extend(format(item_list))
            index += space[meal]
        if day_num != 0:
            # Filling up Snacks in rest of the days
            regular_items[day]["Snacks"].extend(format(snacks))

#-------------------------------------------------------------------------------
# Fill in the extra_items dict
def parse_extras():
    for row in range(1, len(additionals_grid)):
        day = additionals_grid[row][0]
        if day not in days:
            # skip other columns
            continue
        for col in range(1, len(additionals_grid[0])):
            meal = additionals_grid[0][col]
            parsed = parse_cell_items(additionals_grid[row][col])
            extra_items[day][meal].extend(parsed)

#-------------------------------------------------------------------------------
parse_regular()
parse_extras()

#-------------------------------------------------------------------------------
# Write final json

for day in regular_items.keys():
    for meal in regular_items[day].keys():
        regular_items[day][meal].extend(daily_items[meal])

json_data = {
    "LDH": regular_items,
    "UDH": regular_items,
    "LDH Additional": extra_items,
    "UDH Additional": extra_items,
}

with open("mess.json", "w") as outfile:
    json.dump(json_data, outfile, indent = 4)
