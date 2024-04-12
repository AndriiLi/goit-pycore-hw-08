import pickle
from pathlib import Path

from chatbot.classes import AddressBook, Record, Name, Phone
from chatbot.constants import DB_PATH, LEVEL_WARNING
from chatbot.decorators import check_edit_phone_error, \
    check_empty_contacts_error, check_file_exists, check_add_contacts_error, check_show_phone_error, \
    check_delete_contact_error, check_search_contact_error, check_search_email_error, check_search_birthday_error, \
    check_add_email_error, check_add_birthday_error


@check_add_contacts_error
def add_contact(args: tuple[str, str], address_book: AddressBook) -> str:
    record = Record(args[0].strip())
    phone = args[1].strip()

    is_exists = address_book.data.get(record.name.value)
    if is_exists is not None:
        record = is_exists

    record.add_phone(phone)
    address_book.add_record(record)
    return "Contact added."


@check_empty_contacts_error
def all_contacts(address_book: AddressBook) -> str:
    return address_book.print_all() if len(address_book) else 'Address book is empty'


@check_search_contact_error
def find_contact_by_name(args: tuple[str], address_book: AddressBook) -> str:
    name = args[0].strip().capitalize()
    record = address_book.find_record_by_name(name)
    return f"{record.name} phone(s): [ {record.get_phones()} ]"


@check_show_phone_error
def find_contact_by_phone(args: tuple[str], address_book: AddressBook) -> str:
    phone = args[0].strip()
    record = address_book.find_record_by_phone(phone)
    return f"{record.name} phone(s): [ {record.get_phones()} ]"


@check_delete_contact_error
def delete_contact(args: tuple[str], address_book: AddressBook) -> str:
    name = args[0].strip()
    address_book.delete_record(name)
    return "Contact has been deleted."


@check_edit_phone_error
def change_phone(args: tuple[str, str, str], address_book: AddressBook) -> str:
    name = args[0].strip()
    record = address_book.find_record_by_name(name)
    record.edit_phone(args[1].strip(), args[2].strip())

    return "Contact updated."


@check_add_contacts_error
def add_phone(args: tuple[str, str], address_book: AddressBook) -> str:
    name = args[0].strip()
    phone = args[1].strip()
    record = address_book.find_record_by_name(name)

    if record.is_exists(Phone(phone)):
        raise ValueError(LEVEL_WARNING + ' Contact already has this phone number')

    record.add_phone(phone)
    return "Phone added."


@check_add_contacts_error
def del_phone(args: tuple[str, str], address_book: AddressBook) -> str:
    name = Name(args[0].strip())
    phone = Phone(args[1].strip())
    record = address_book.find_record_by_name(name.value)

    if record.is_exists(phone) is False:
        raise ValueError(LEVEL_WARNING + " Contact doesn't have this phone number")

    record.remove_phone(phone)
    address_book.data[name.value] = record

    return "Phone deleted."


@check_add_birthday_error
def add_birthday(args: tuple[str, str], address_book: AddressBook) -> str:
    address_book.add_birthdays(*args)
    return "Date of birth is set for the contact."


@check_search_contact_error
def show_birthday(args: tuple[str], address_book: AddressBook) -> str:
    record = address_book.find_record_by_name(args[0])
    if record is None or not record.birthday:
        return "Date of birth is undefined for the contact."

    return f"{record.name.value} birthday {record.birthday.value}"


@check_empty_contacts_error
def birthdays(address_book: AddressBook) -> str:
    birthday_list = address_book.get_upcoming_birthdays()

    if not len(birthday_list):
        return 'There are no birthdays this week'

    return f"List of birthdays this week\n{'-' * 70}\n{address_book.get_upcoming_birthdays()}"


@check_add_email_error
def add_email(args: tuple[str, str], address_book: AddressBook) -> str:
    address_book.add_email(*args)
    return "Email is set for the contact."


@check_search_email_error
def find_by_email(args: tuple[str,], address_book: AddressBook) -> str:
    records = address_book.find_record_by_email(args[0].strip())
    res = ''
    for r in records:
        res += f"{r.name.value} email: {r.email.value}\n"

    return res or f"Contact with email {args[0].strip()} not found"


@check_search_birthday_error
def find_by_birthday(args: tuple[str,], address_book: AddressBook) -> str:
    records = address_book.find_record_by_birthday(args[0].strip())
    res = ''
    for r in records:
        res += f"{r.name.value} email: {r.birthday.value}\n"

    return res or f"Contact with birthday {args[0].strip()} not found"


@check_file_exists
def save_data(address_book: AddressBook, filename=DB_PATH) -> str:
    with open(Path(filename).absolute(), 'wb') as f:
        pickle.dump(address_book, f)
    return "Contacts saved into file."


@check_file_exists
def load_data(filename=DB_PATH) -> AddressBook:
    try:
        with open(Path(filename).absolute(), 'rb') as file:
            return pickle.load(file)
    except (OSError, pickle.UnpicklingError):
        return AddressBook()


