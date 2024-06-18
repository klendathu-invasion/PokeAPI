class ColumnsError(Exception):
    def __init__(
        self, tablename: str, columns: list[str], message: str = "Wrong column name"
    ):
        self.tablename = tablename
        self.columns = columns
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} -> The table '{self.tablename}' doesn't contain the column(s) : {', '.join(self.columns)}"
