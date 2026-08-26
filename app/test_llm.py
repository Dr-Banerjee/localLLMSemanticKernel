import asyncio

from services.llm_service import generate_response

async def main():
    answer = await generate_response("There's many a twixt between the cup and the lip.")

    print(answer)


asyncio.run(main())