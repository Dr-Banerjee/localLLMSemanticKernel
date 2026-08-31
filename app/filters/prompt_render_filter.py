from semantic_kernel.filters import PromptRenderContext

class PromptRenderFilter:

    def __init__(self):
        pass
    
    async def on_prompt_render(
        self,
        context: PromptRenderContext,
        next,
    ):
        print("\n>>> PROMPT RENDER")

        print(">>> RENDERED PROMPT:")
        print(context.rendered_prompt)

        await next(context)

        print(">>> FUNCTION RESULT:")
        print(context.function_result)