from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion

def createKernel()-> Kernel:
    kernel = Kernel()
    ollamaService = OllamaChatCompletion(ai_model_id="lfm2.5-thinking:1.2b",
                                          host="http://localhost:11434",
                                          )   # Replace with your desired model
    kernel.add_service(ollamaService)
    return kernel