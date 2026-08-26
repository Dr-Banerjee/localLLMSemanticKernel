from models.request import UserRequest
from models.response import ResponseToUserRequest
import services.llm_service as llmService

#function to feed the user input to the LLM service.
def process(request: UserRequest) -> ResponseToUserRequest:
    #Feed the user input to the LLM service and return the generated response
    return llmService.generate_response(request)
    