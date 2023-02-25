class RequiredParametersNotAvialble(Exception):
    """Exception raised for the absence of required parameters"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return repr(self.message)


class MissingInDatabase(Exception):
    """Exception raised for the absence of items from database"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return repr(self.message)


class InvalidParameterValue(Exception):
    """Exception raised for the absence of items from database"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return repr(self.message)


class WrongMethod(Exception):
    """Exception raised for the absence of items from database"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return repr(self.message)
