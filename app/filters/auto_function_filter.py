from semantic_kernel.filters import AutoFunctionInvocationContext


class AutoFunctionFilter:
    
    def __init__(self):
        pass

    async def on_auto_function_invocation(
        self,
        context: AutoFunctionInvocationContext,
        next,
    ):
        print("\n>>> AUTO FUNCTION INVOCATION")

        print(
            f">>> Function call: "
            f"{context.function_call_content}"
        )

        await next(context)

        print(
            f">>> Function result: "
            f"{context.function_result}"
        )

        print(
            f">>> Request sequence: "
            f"{context.request_sequence_index}"
        )

        print(
            f">>> Function sequence: "
            f"{context.function_sequence_index}"
        )

        print(
            f">>> Function count: "
            f"{context.function_count}"
        )
        
        print(
            f">>> Terminate: "
            f"{context.terminate}"
        )