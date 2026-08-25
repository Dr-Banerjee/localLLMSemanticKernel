from models.request import UserRequest
from models.response import UserResponse
import services.llm_service as llmService

def process(request: UserRequest) -> UserResponse:
    #Feed the user input to the LLM service and return the generated response
    return llmService.generate_response(request)
    