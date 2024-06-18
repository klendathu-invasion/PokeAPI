from ..test_main import fake


class SwitchFake:
    @classmethod
    def fake(cls, attribute_type: str):
        method = f"fake_{attribute_type}"
        if method in dir(cls):
            return getattr(cls, method)()
        return None

    @staticmethod
    def fake_bool():
        return fake.pybool()

    @staticmethod
    def fake_date_time():
        return fake.date_time()

    @staticmethod
    def fake_date_time_str():
        return fake.date_time().isoformat(timespec="seconds")

    @staticmethod
    def fake_float():
        return fake.pyfloat(min_value=0.01)

    @staticmethod
    def fake_id():
        return 0

    @staticmethod
    def fake_int():
        return fake.pyint()

    @staticmethod
    def fake_name():
        return fake.name()

    @staticmethod
    def fake_str():
        return fake.pystr()

    @staticmethod
    def fake_trigram():
        return "".join(fake.random_letters(length=3)).upper()
