import csv
from pprint import pprint
import re


def split_full_name(full_name):
    parts = [part.strip() for part in full_name.replace(',', ' ').split()]
    return parts


def format_phone(phone):
    digits = re.sub(r'\D', '', phone)
    formatted_phone = re.sub(r'(\d{1})(\d{3})(\d{3})(\d{2})(\d{2})', r'+7(\2)\3-\4-\5', digits)
    return formatted_phone


def process_phone_with_extension(phone_with_extension):
    match = re.match(r'(.+?)\s*доб\.\s*(\d+)', phone_with_extension)

    if match:
        main_part = match.group(1).strip()
        extension_part = match.group(2).strip()
        main_part = re.sub(r'\W+$', '', main_part)
        formatted_main_part = format_phone(main_part)

        return f"{formatted_main_part} доб.{extension_part}"
    else:
        return format_phone(phone_with_extension)


with open("phonebook_raw.csv") as f:
    rows = csv.reader(f, delimiter=",")
    contacts_list = list(rows)

header = contacts_list[0]

lastname_index = header.index("lastname")
firstname_index = header.index("firstname")
surname_index = header.index("surname")
phone_index = header.index("phone")

unique_records = {}

for contact in contacts_list[1:]:
    full_name_index = None

    for i in [lastname_index, firstname_index, surname_index]:
        if i < len(contact) and (" " in contact[i] or "," in contact[i]):
            full_name_index = i
            break

    if full_name_index is not None and not contact[firstname_index].strip() and not contact[surname_index].strip():
        full_name = contact[full_name_index]
        names = split_full_name(full_name)

        contact[full_name_index] = names[0]
        if len(names) > 1:
            contact[firstname_index] = names[1]
        if len(names) > 2:
            contact[surname_index] = names[2]

    elif firstname_index < len(contact) and " " in contact[firstname_index]:
        names = split_full_name(contact[firstname_index])
        contact[firstname_index] = names[0]
        if len(names) > 1:
            contact[firstname_index + 1] = names[1]

    lastname = contact[lastname_index].strip()
    firstname = contact[firstname_index].strip()
    key = (lastname, firstname)

    if key in unique_records:
        existing_record = unique_records[key]
        for i in range(min(len(existing_record), len(contact))):
            if not existing_record[i].strip() and contact[i].strip():
                existing_record[i] = contact[i]
    else:
        unique_records[key] = contact


for contact in unique_records.values():
    phone = contact[phone_index].strip()
    formatted_phone = process_phone_with_extension(phone)
    contact[phone_index] = formatted_phone


pprint(list(unique_records.values()))


with open("phonebook.csv", "w", newline='') as f:
    datawriter = csv.writer(f, delimiter=',')
    datawriter.writerows([header] + list(unique_records.values()))