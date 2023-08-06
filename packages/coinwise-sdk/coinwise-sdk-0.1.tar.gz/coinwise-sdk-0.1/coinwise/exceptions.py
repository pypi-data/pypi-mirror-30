class CoinWiseInvalidUserException(Exception):
    def __init__(self):
        self.message = 'Invalid username or password'


class CoinWiseException(Exception):
    def __init__(self, message):
        self.message = message
