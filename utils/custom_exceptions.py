class NonUint8(Exception):
    """Exception is raised if a function is given an  incompatible int argument where an uint8 is expected."""
    def __init__(self, *args):
        """if argument are passed, the first is assumed to be the value passed and the second is the error message"""
        if args:
            self.value = args[0]
        else:
            self.value = None
        if len(args) > 1:
            self.message = args[1]
        else:
            self.message = "Value is not uint8"
        super().__init__(self.message)
