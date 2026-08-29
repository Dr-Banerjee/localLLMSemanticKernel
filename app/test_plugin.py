import asyncio

from semantic_kernel.functions import KernelArguments

from kernel.kernel import createKernel


async def main():
    kernel = createKernel()

    result = await kernel.invoke(
        kernel.plugins["IdiomPlugin"]["getIdiomHint"],
        arguments=KernelArguments(
            idiom="to perform a moonraker's errand"
        ),
    )

    print(result)


asyncio.run(main())