from models.request import UserRequest
import services.llm_service as llmService

def process(request: UserRequest) -> None:
    #At the moment one just prints the user  input.
    llmService.generate_response(request)
    