# Jeffar - Generate Mock Data
# Description - Generates a mock CSV file for realistic sensitive data.
# Created - 2026-07-20
# Last updated - 2026-07-21

# Modules
from faker import Faker     # for generating fake data
import random               # for generating random numbers
import csv                  # for csv exporting

# Main function
def main():
    data = generate()
    write_csv(data)

# Functions
def generate():
    """
    generate - generates a 100-row csv file of fake data
    """
    fake = Faker("en_CA")   # instantiator for Canadian data
    rows = []               # holds rows

    for _ in range(100):
        # contains:
        row = {
            "name": fake.name(),
            "email": fake.email() if random.random() < 0.9 else "",
            "phone": fake.phone_number() if random.random() < 0.9 else "",
            "DOB": fake.date_of_birth(minimum_age=18, maximum_age=100),
            "SIN": fake.numerify(text="#########"),
            "address": fake.address()
        }

        rows.append(row)
    
    return rows

def write_csv(rows, filename="mock_pii.csv"):
    """
    write_csv - writes the data list to a CSV file

    rows - list of row dicts (name, email, phone, DOB, SIN, address)

    filename - saved file with dir and extension
    """
    with open(filename, "w", newline="", encoding="utf-8") as file:     # writes to savepath in utf-8 without automatic \n and create object file
        writer = csv.DictWriter(
            file,                                                       # write to file object
            fieldnames=rows[0].keys()                                   # CSV column are based on list
            )
        
        # write the list
        writer.writeheader()
        writer.writerows(rows)

# dunder name guard
if __name__ == "__main__":
    main()