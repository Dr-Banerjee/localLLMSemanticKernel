from semantic_kernel.filters import FunctionInvocationContext

class LoggingFilter:
    def __init__(self):
        pass
    async def on_functioninvocation(self, context: FunctionInvocationContext, next,):
        print(
              f">>> BEFORE:"
              f"{context.function.plugin_name}."
              f"{context.function.name}"
              )
        
        await next(context)

        print (
              f">>> AFTER:"
              f"{context.function.plugin_name}."
              f"{context.function.name}"
            )