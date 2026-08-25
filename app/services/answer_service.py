from models.request import UserRequest

def process(request: UserRequest) -> None:
    #At the moment one just prints the user  input.
    print(f"User input: {request.userInput}")
    