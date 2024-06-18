import enum


class EnvironmentEnum(str, enum.Enum):
    dev = "dev"
    test = "test"
    preproduction = "preproduction"
    production = "production"
