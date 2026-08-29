import asyncio

from app.services.single_chat_service import generate_response

async def main():
    answer = await generate_response("to perform a moonraker's errand")

    print(answer)


asyncio.run(main())