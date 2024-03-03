import asyncio
import aiohttp
import logging
import functools


def retry_request(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        for retry in range(3):
            try:
                result = await func(*args, **kwargs)

                if 'code' in result:
                    continue
                return result

            except aiohttp.ClientError as e:
                logging.warning(f"Aiohttp error: {e}. {retry} Retryed.")
            except Exception as ex:
                logging.warning(f"Unexpected error: {ex}, {retry} Retryed.")

            await asyncio.sleep(2**retry)

        logging.error(f"Failed after {retry} retries")
        raise ValueError(f"Failed after {retry} retries. {result}")
    return wrapper

