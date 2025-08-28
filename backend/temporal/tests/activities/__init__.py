import typing


class AsyncIterator:
    """
    Class for mocking async iterators, namely httpx Request.aiter_bytes()
    """

    def __init__(self, seq: list[typing.Any]) -> None:
        self.iter = iter(seq)

    def __aiter__(self) -> "AsyncIterator":
        return self

    async def __anext__(self) -> typing.Any:
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration
