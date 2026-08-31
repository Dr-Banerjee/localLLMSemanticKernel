from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.ollama import OllamaChatCompletion
from app.filters.prompt_render_filter import PromptRenderFilter
from app.plugins.idiom_plugin import IdiomPlugin
from app.filters.logging_filter import LoggingFilter
from semantic_kernel.filters import FilterTypes
from app.filters.auto_function_filter import AutoFunctionFilter
from app.filters.prompt_render_filter import PromptRenderFilter

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
    kernel.add_filter(filter_type=FilterTypes.FUNCTION_INVOCATION, filter=LoggingFilter().on_functioninvocation,)
    kernel.add_filter(filter_type=FilterTypes.AUTO_FUNCTION_INVOCATION, filter=AutoFunctionFilter().on_auto_function_invocation,)
    kernel.add_filter(filter_type=FilterTypes.PROMPT_RENDERING, filter=PromptRenderFilter().on_prompt_render,)

    return kernel