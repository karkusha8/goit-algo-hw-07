from collections import UserDict
from datetime import datetime, date, timedelta


class Field:
    """Базовий клас для полів контакту"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Клас для імені контакту"""
    pass


class Phone(Field):
    """Клас для номера телефону з перевіркою формату (10 цифр)"""
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Номер телефону повинен містити рівно 10 цифр.")
        super().__init__(value)


class Birthday(Field):
    """Клас для дня народження у форматі DD.MM.YYYY"""
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Невірний формат дати. Використовуйте DD.MM.YYYY")
        self.value = value



class Record:
    """Клас для одного контакту: ім'я + телефони + день народження"""
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if any(p.value == phone for p in self.phones):
            raise ValueError(f"Номер {phone} вже існує у контакті {self.name.value}.")
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        phone_obj = self.find_phone(phone)
        if phone_obj:
            self.phones.remove(phone_obj)

    def edit_phone(self, old_phone, new_phone):
        phone_obj = self.find_phone(old_phone)
        if not phone_obj:
            raise ValueError(f"Старий номер {old_phone} не знайдено.")
        new_phone_obj = Phone(new_phone)
        self.phones.remove(phone_obj)
        self.phones.append(new_phone_obj)

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday_str):
        self.birthday = Birthday(birthday_str)

    def __str__(self):
        phones_list = ", ".join(p.value for p in self.phones) if self.phones else "немає номерів"
        bday_str = self.birthday.value if self.birthday else "немає"
        return f"{self.name.value}: {phones_list}, день народження: {bday_str}"


class AddressBook(UserDict):
    """Клас для зберігання всіх контактів"""

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        upcoming = []
        today = date.today()

        for record in self.data.values():
            if record.birthday:
                bday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
                bday_this_year = bday_date.replace(year=today.year)

                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)

                if bday_this_year.weekday() == 5:
                    bday_this_year += timedelta(days=2)
                elif bday_this_year.weekday() == 6:
                    bday_this_year += timedelta(days=1)

                if 0 <= (bday_this_year - today).days <= days:
                    upcoming.append({
                        "name": record.name.value,
                        "birthday": bday_this_year.strftime("%d.%m.%Y")
                    })

        return upcoming

    def __str__(self):
        if not self.data:
            return "Список контактів порожній."
        return "\n".join(str(record) for record in self.data.values())


def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Контакт не знайдено."
        except ValueError as e:
            return str(e)
        except IndexError:
            return "Введіть команду та аргументи."
    return wrapper


@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    if not record:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return f"Контакт {name} додано з номером {phone}."
    else:
        record.add_phone(phone)
        return f"До контакту {name} додано номер {phone}."

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"У контакті {name} номер {old_phone} замінено на {new_phone}."
    else:
        raise KeyError

@input_error
def show_phone(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return ", ".join(p.value for p in record.phones)
    else:
        raise KeyError

@input_error
def delete_contact(args, book: AddressBook):
    name = args[0]
    if book.find(name):
        book.delete(name)
        return f"Контакт {name} видалено."
    else:
        raise KeyError

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_str = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(birthday_str)
    return f"День народження для контакту {name} встановлено: {birthday_str}"


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.birthday:
        raise ValueError("День народження не встановлено.")
    return record.birthday.value

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "Найближчих днів народження немає."
    return "\n".join(f"{item['name']} — {item['birthday']}" for item in upcoming)

def show_all(book: AddressBook):
    return str(book)


def parse_input(user_input):
    command, *args = user_input.split()
    return command.strip().lower(), args

def main():
    book = AddressBook()
    print("Ласкаво просимо до вашого асистента! 😊")

    while True:
        user_input = input("Введіть команду: ")
        if not user_input.strip():
            print("Будь ласка, введіть команду.")
            continue

        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("До побачення! 👋")
            break
        elif command == "hello":
            print("Привіт! Чим можу допомогти? 🖐️")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "delete":
            print(delete_contact(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Невідома команда. Спробуйте: add, change, phone, delete, all, add-birthday, show-birthday, birthdays, hello, exit.")

if __name__ == "__main__":
    main()