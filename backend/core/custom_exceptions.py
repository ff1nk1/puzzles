class BusinessError(Exception):
    pass



class UserAlreadyExistsError(BusinessError):
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        super().__init__(f"{field} '{value}' already exists")

class UserNotFoundError(BusinessError):
    def __init__(self, username):
        super().__init__(f"there is no user with nickname - '{username}'")


class WrongPasswordError(BusinessError):
    def __init__(self):
        super().__init__(f"Password is incorrect")

class  RefreshTokenNotFoundError(BusinessError):
    def __init__(self):
        super().__init__(f"Refresh token is not found")
class RefreshTokenExpiredError(BusinessError):
    def __init__(self):
        super().__init__(f"Refresh token is expired")




#=========================PUZZLE-ERRORS====================================
class PuzzleNotFoundError(BusinessError):
    def __init__(self):
        super().__init__(f"Puzzle is not found")

class TestNotFoundError(BusinessError):
    def __init__(self):
        super().__init__(f"Test is not found")



#=====================-SUBMISSION-ERROR-======================================
class SubmissionNotFoundError(BusinessError):
    def __init__(self):
        super().__init__(f"Submission is not found")
