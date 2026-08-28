from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from plugins.idiom_plugin import IdiomPlugin

def createKernel()-> Kernel:
    kernel = Kernel()
    ollamaService = OllamaChatCompletion(ai_model_id="gpt-oss:20b-cloud",
                                          host="http://localhost:11434",
                                          )   # Replace with your desired model
    kernel.add_service(ollamaService)
    kernel.add_plugin(
        IdiomPlugin(),
        plugin_name="IdiomPlugin",
    )
    return kernel