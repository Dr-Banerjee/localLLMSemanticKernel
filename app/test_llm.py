import asyncio

from services.llm_service import generate_response

async def main():
    answer = await generate_response("to perform a moonraker's errand")

    print(answer)


asyncio.run(main())