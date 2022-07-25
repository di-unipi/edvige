import gspread
import csv

if __name__ == '__main__':
    gc = gspread.service_account(filename='credentials.json')
    # Access to the google spreadSheet named "Eventi e news"
    spreadsheet = gc.open("Eventi e news")

    # Access to the sheet named "Eventi"
    wks = spreadsheet.worksheet("Eventi")

    # Writes each row of the sheet into a csv file named "events.csv"
    filename = "events.csv"
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(wks.get_all_values())
