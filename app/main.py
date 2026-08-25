from models.request import UserRequest
import services.answer_service as answerService

def main():
    print("Enter an idiom which you want to know the meaning of:")
    userInput = input("You: ")
    request = UserRequest(userInput=userInput)
    answerService.process(request)

if __name__ == "__main__":
    main()