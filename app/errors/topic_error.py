class CreateTopicError(Exception):
    def __init__(self, subject: str, message: str = "TOPIC NOT CREATED"):
        self.message = message
        self.subject = subject
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} -> SNS coudn't create topic for subject: {self.subject}"
