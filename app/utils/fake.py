from faker import Faker
from pydantic import BaseModel


class Fake(BaseModel):
    __fake__ = Faker()

    @classmethod
    def date_time_between(cls, json_dict: dict) -> None:
        """This function transform a dict.

        :param json_dict: the dict to transform
        :type json_dict: dict
        :returns: None

        """
        for value in json_dict["fake_date_time_between"]:
            start_date = value["start_date"] if "start_date" in value else "-2y"
            end_date = value["end_date"] if "end_date" in value else "now"
            json_dict[value["key"]] = cls.__fake__.date_time_between(
                start_date=start_date, end_date=end_date
            )
        json_dict.pop("fake_date_time_between")

    @classmethod
    def description(cls, value: str, number: str) -> str:
        """This function transform a string.

        :param value: the str to transform
        :param number: the number of fake
        :type value: str
        :type number: str
        :returns: str

        """
        return value.replace("[FAKE_DESCRIPTION]", cls.__fake__.paragraph())

    @classmethod
    def email_user(cls, value: str, number: str) -> str:
        """This function transform a string.

        :param value: the str to transform
        :param number: the number of fake
        :type value: str
        :type number: str
        :returns: str

        """
        suffix = cls.__fake__.random_element(elements=[".ext", ""])
        return value.replace(
            "[FAKE_EMAIL_USER]",
            f"{cls.__fake__.first_name().lower()}.{cls.__fake__.last_name().lower()}{suffix}",
        )

    @classmethod
    def file_path_json(cls, value: str, number: str) -> str:
        """This function transform a string.

        :param value: the str to transform
        :param number: the number of fake
        :type value: str
        :type number: str
        :returns: str

        """
        return value.replace(
            "[FAKE_FILE_PATH_JSON]", cls.__fake__.file_path(extension="json")
        )

    @classmethod
    def firstname(cls, value: str, number: str) -> str:
        """This function transform a string.

        :param value: the str to transform
        :param number: the number of fake
        :type value: str
        :type number: str
        :returns: str

        """
        return value.replace("[FAKE_FIRSTNAME]", cls.__fake__.first_name())

    @classmethod
    def id_number(cls, value: str, number: str) -> str:
        """This function transform a string.

        :param value: the str to transform
        :param number: the number of fake
        :type value: str
        :type number: str
        :returns: str

        """
        return value.replace("[FAKE_ID_NUMBER]", number)

    @classmethod
    def lastname(cls, value: str, number: str) -> str:
        """This function transform a string.

        :param value: the str to transform
        :param number: the number of fake
        :type value: str
        :type number: str
        :returns: str

        """
        return value.replace("[FAKE_LASTNAME]", cls.__fake__.last_name())

    @classmethod
    def matricule(cls, value: str, number: str) -> str:
        """This function transform a string.

        :param value: the str to transform
        :param number: the number of fake
        :type value: str
        :type number: str
        :returns: str

        """
        alphabet = [chr(letter) for letter in range(ord("a"), ord("z") + 1)]
        numbers = [str(digit) for digit in range(0, 10)]
        matricule = "".join(
            cls.__fake__.random_elements(elements=alphabet + numbers, length=4)
        )
        return value.replace("[FAKE_MATRICULE]", f"d{matricule}{number}")

    @classmethod
    def name(cls, value: str, number: str) -> str:
        """This function transform a string.

        :param value: the str to transform
        :param number: the number of fake
        :type value: str
        :type number: str
        :returns: str

        """
        return value.replace("[FAKE_NAME]", f"{cls.__fake__.unique.name()}{number}")

    @classmethod
    def random_float(cls, json_dict: dict) -> None:
        """This function transform a dict.

        :param json_dict: the dict to transform
        :type json_dict: dict
        :returns: None

        """
        for value in json_dict["fake_random_float"]:
            min_value = value["min"] if "min" in value else 0
            max_value = value["max"] if "max" in value else 999999
            json_dict[value["key"]] = (
                cls.__fake__.random_int(min=min_value, max=max_value) / 100
            )
        json_dict.pop("fake_random_float")

    @classmethod
    def random_int(cls, json_dict: dict) -> None:
        """This function transform a dict.

        :param json_dict: the dict to transform
        :type json_dict: dict
        :returns: None

        """
        for value in json_dict["fake_random_int"]:
            min_value = value["min"] if "min" in value else 0
            max_value = value["max"] if "max" in value else 9999
            json_dict[value["key"]] = cls.__fake__.random_int(
                min=min_value, max=max_value
            )
        json_dict.pop("fake_random_int")

    @classmethod
    def trigram(cls, value: str, number: str) -> str:
        """This function transform a string.

        :param value: the str to transform
        :param number: the number of fake
        :type value: str
        :type number: str
        :returns: str

        """
        return value.replace(
            "[FAKE_TRIGRAM]", "".join(cls.__fake__.random_letters(length=3)).upper()
        )

    @classmethod
    def uuid(cls, value: str, number: str) -> str:
        """This function transform a string.

        :param value: the str to transform
        :param number: the number of fake
        :type value: str
        :type number: str
        :returns: str

        """
        return value.replace("[FAKE_UUID]", cls.__fake__.uuid4())

    @classmethod
    def uuid_upper(cls, value: str, number: str) -> str:
        """This function transform a string.

        :param value: the str to transform
        :param number: the number of fake
        :type value: str
        :type number: str
        :returns: str

        """
        return value.replace("[FAKE_UUID_UPPER]", cls.__fake__.uuid4().upper())

    @classmethod
    def version(cls, value: str, number: str) -> str:
        """This function transform a string.

        :param value: the str to transform
        :param number: the number of fake
        :type value: str
        :type number: str
        :returns: str

        """
        return value.replace("[FAKE_VERSION]", cls.__fake__.bothify(text="?#.#.#"))

    __keys__: dict = {
        "fake_date_time_between": date_time_between,
        "fake_random_float": random_float,
        "fake_random_int": random_int,
    }

    __values__: dict = {
        "[FAKE_DESCRIPTION]": description,
        "[FAKE_EMAIL_USER]": email_user,
        "[FAKE_FILE_PATH_JSON]": file_path_json,
        "[FAKE_FIRSTNAME]": firstname,
        "[FAKE_ID_NUMBER]": id_number,
        "[FAKE_LASTNAME]": lastname,
        "[FAKE_MATRICULE]": matricule,
        "[FAKE_NAME]": name,
        "[FAKE_TRIGRAM]": trigram,
        "[FAKE_UUID]": uuid,
        "[FAKE_UUID_UPPER]": uuid_upper,
        "[FAKE_VERSION]": version,
    }
