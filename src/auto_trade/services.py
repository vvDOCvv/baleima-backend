import asyncio
import aiohttp
import logging
import functools


def retry_request(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        for retry in range(1, 4):
            try:
                result = await func(*args, **kwargs)

                if 'code' in result:
                    if result['code'] == 30004:
                        return result
                    continue
                return result

            except aiohttp.ClientError as e:
                logging.error(f"Aiohttp error: {e}. {retry} Retryed.")
            except Exception as ex:
                logging.error(f"Unexpected error: {ex}, {retry} Retryed.")

            await asyncio.sleep(2**retry)
        raise ValueError(f"Failed after {retry} retries. {result}")
    return wrapper

