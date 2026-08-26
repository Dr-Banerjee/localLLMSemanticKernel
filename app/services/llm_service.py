from models.request import UserRequest
from models.response import UserResponse
import requests

#function to generate response from the LLM
def generate_response(request: UserRequest) -> UserResponse:
    # Raw LLM response from the LLM service
    response = requests.post("http://localhost:11434/api/generate", 
                             json = {"model": "lfm2.5-thinking:1.2b", #replace with a model of your choice
                                      "prompt": request.userInput ,
                                      "stream": False,
                                    },
                            )
    response.raise_for_status()
    data = response.json()
    userResponse = data["response"]
    return UserResponse(userResponse=userResponse)