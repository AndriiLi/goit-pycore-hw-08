import re
from collections import UserDict
from datetime import datetime, timedelta, date

from chatbot.constants import LEVEL_WARNING, PHONE_WRONG_FORMAT, LEVEL_ERROR, NOT_FOUND, GIVE_PHONE


class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self):
        return self.value


class Name(Field):
    def __init__(self, name: str):
        super().__init__(name.capitalize())


class Birthday(Field):
    def __init__(self, date: str):
        try:
            self.birthday = datetime.strptime(date, '%d.%m.%Y').date()
            super().__init__(date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Email(Field):
    def __init__(self, email: str):
        if not self._is_valid(email):
            raise ValueError("Input email is not valid")

        super().__init__(email)

    def _is_valid(self, email) -> bool:
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if re.match(pattern, email):
            return True

        return False


class Phone(Field):
    def __init__(self, phone: str):
        if self.is_valid_phone(phone):
            super().__init__(self.format_phone(phone))
        else:
            raise ValueError(LEVEL_ERROR + ' ' + PHONE_WRONG_FORMAT)

    def is_valid_phone(self, phone: str) -> bool:
        pattern = r"(^\+38\d{10}$)|(^\d{10}$)"
        if re.search(pattern, phone):
            return True

        return False

    def format_phone(self, phone: str) -> str:
        if not phone.startswith('+38'):
            phone = f"+38{phone}"

        return phone


class Record:
    def __init__(self, name: str) -> None:
        self.name: Name = Name(name)
        self.phones: list[Phone] = []
        self.birthday = None
        self.email = None

    def get_phone_index(self, phone: str) -> int | None:
        search = Phone(phone)
        for idx, p in enumerate(self.phones):
            if p.value == search.value:
                return idx
        return None

    def add_phone(self, phone: str) -> None:
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: Phone) -> None:
        self.phones = [p for p in self.phones if p.value != phone.value]

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        index = self.get_phone_index(old_phone)
        if index is None:
            raise ValueError(f"{LEVEL_WARNING} Contact doesn't have phone number {old_phone},"
                             f" input valid number which you want change")

        self.phones[index] = Phone(new_phone)

    def get_phones(self, separator: str = ', ') -> str:
        return separator.join(p.value for p in self.phones)

    def add_birthday(self, date_birthday: str) -> None:
        self.birthday = Birthday(date_birthday)

    def add_email(self, email: str):
        self.email = Email(email)

    def is_exists(self, phone: Phone) -> bool:
        return phone.value in [p.value for p in self.phones]

    def __str__(self) -> str:
        return (f"Contact name: {self.name.value} phones: {self.get_phones()}"
                f" {'email: ' + self.email.value if self.email else ''}"
                f" {'birthday: ' + self.birthday.value if self.birthday else ''}")


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find_record_by_name(self, name: str) -> Record:
        found = self.data.get(name.capitalize())
        if found is None:
            raise ValueError(LEVEL_ERROR + ' ' + NOT_FOUND)

        return found

    def find_record_by_phone(self, phone: str) -> Record:
        phone = Phone(phone)
        if phone is None:
            raise ValueError(LEVEL_ERROR + ' ' + GIVE_PHONE)

        found = None
        for record in self.data.values():
            if phone.value in [p.value for p in record.phones]:
                found = record

        if not found:
            raise ValueError(LEVEL_ERROR + ' ' + NOT_FOUND)

        return found

    def find_record_by_email(self, email: str) -> list[Record]:
        email = Email(email)
        return filter(lambda record: record.email and record.email.value == email.value, self.data.values())

    def find_record_by_birthday(self, birthday: str) -> list[Record]:
        birthday = Birthday(birthday)
        return filter(lambda record: record.birthday and record.birthday.value == birthday.value, self.data.values())

    def delete_record(self, name: str) -> None:
        record = self.data.get(name.capitalize())
        if record is None:
            raise ValueError(LEVEL_ERROR + ' ' + NOT_FOUND)

        del self.data[name.capitalize()]

    def print_all(self) -> str:
        res = ''
        for rec in self.data.values():
            res += f"{str(rec)}\n"
        return res

    def add_birthdays(self, name: str, date_birthday: str) -> None:
        record = self.find_record_by_name(name)
        record.add_birthday(date_birthday)

    def add_email(self, name: str, email: str) -> None:
        record = self.find_record_by_name(name)
        record.add_email(email)

    def print_birthdays(self) -> str:
        res = ''
        for rec in self.data.values():
            res += f"{rec.name.value} : {rec.birthday or 'undefined'} \n"
        return res

    def __find_next_weekday(self, d: date, weekday: int = 0) -> date:
        days_diff = weekday - d.weekday()
        if days_diff <= 0:
            days_diff += 7

        return d + timedelta(days=days_diff)

    def get_upcoming_birthdays(self) -> str:
        days = 7
        index = 1
        current_date = datetime.now().date()
        congratulation_list = ''

        record: Record
        for record in self.data.values():

            if record.birthday is None:
                continue

            user_birthday_date_this_year = record.birthday.birthday.replace(year=current_date.year)

            if user_birthday_date_this_year < current_date:
                user_birthday_date_this_year = user_birthday_date_this_year.replace(year=current_date.year + 1)

            if 0 <= (user_birthday_date_this_year - current_date).days <= days:
                if user_birthday_date_this_year.weekday() >= 5:
                    user_birthday_date_this_year = self.__find_next_weekday(user_birthday_date_this_year)

                congratulation_list += (f"{index}.  name: {record.name.value}, birthday: {record.birthday.value}, "
                                        f"congratulation_date: {user_birthday_date_this_year.strftime('%d.%m.%Y')} \n")
                index += 1

        return congratulation_list
