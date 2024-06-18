from datetime import datetime

from pydantic import BaseModel

from .fake import Fake


class DictHandler(BaseModel):
    @classmethod
    def parser(cls, json_dict: dict) -> dict:
        """This function parse a dict to change some data.

        :param json_dict: the dict to parse
        :type json_dict: dict
        :returns: dict

        """
        if "number" in json_dict and "values" in json_dict and "others" in json_dict:
            number = json_dict["number"]
            values = json_dict["values"]
            others = json_dict["others"]
            json_dict.pop("number")
            json_dict.pop("values")
            json_dict.pop("others")
            first_dict = [cls.transform(other.copy()) for other in others]
            last_dict = [
                cls.transform(value.copy(), str(i + 1))
                for value in values
                for i in range(number)
            ]
            json_dict = first_dict + last_dict

        if "date" in json_dict:
            for key, value in json_dict["date"].items():
                json_dict[key] = datetime.strptime(value, "%Y-%m-%d")
            json_dict.pop("date")
        return json_dict

    @staticmethod
    def transform(json_dict: dict, number: str = "") -> dict:
        """This function transform a dict by random value.

        :param json_dict: the dict to transform
        :param number: a number for some values
        :type json_dict: dict
        :type number: str
        :returns: dict

        """
        for key, value in json_dict.items():
            if isinstance(value, str):
                for value_fake in Fake.__values__.keys():
                    if value_fake in value:
                        value = Fake.__values__[value_fake].__func__(
                            Fake, value=value, number=number
                        )
                json_dict[key] = value
        for key_fake in Fake.__keys__.keys():
            if key_fake in json_dict:
                Fake.__keys__[key_fake].__func__(Fake, json_dict=json_dict)
        return json_dict
