
class ProfileError(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)


class HistoryError(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)


class ModelNumberError(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)


class BadPathError(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)


class UnknownFileTypeError(Exception):

    def __init__(self, msg):
        Exception.__init__(self, msg)