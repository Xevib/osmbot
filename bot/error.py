class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class OSMError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression=None, message=None):
        self.expression = expression
        self.message = message
