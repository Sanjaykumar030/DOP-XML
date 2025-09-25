async def anext(iterator, default=None):
    """
    Asynchronous version of the built-in next() function.
    This is needed to iterate over the async generator from the chatbot.
    """
    try:
        return await iterator.__anext__()
    except StopAsyncIteration:
        return default
