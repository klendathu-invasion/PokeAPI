class NoAccountUserError(Exception):
    def __init__(
        self, attr: str, message: str = "This user seems to don't have any account"
    ):
        self.message = message
        self.attr = attr
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} -> the user with attribute(s) {self.attr} doesn't have an account on OneSPC"
