class VoteError(Exception):
    pass

class VoteValidationError(VoteError):
    def __init__(self, error_message):
        self.error_message = error_message