from models.request import UserRequest
from models.response import UserResponse
import requests

def generate_response(request: UserRequest) -> UserResponse:
    # Placeholder for generating a response based on the user input.
    # In a real implementation, this would involve calling an LLM or other processing logic.
    response = requests.post("http://localhost:11434/api/generate", 
                             json = {"model": "lfm2.5-thinking:1.2b",
                                      "prompt": request.userInput ,
                                      "stream": False,
                                    },
                            )
    response.raise_for_status()
    data = response.json()
    userResponse = data["response"]
    return UserResponse(userResponse=userResponse)