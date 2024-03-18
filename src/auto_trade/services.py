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
                    if result['code'] == 30004:
                        return result
                    continue
                return result

            except aiohttp.ClientError as e:
                logging.warning(f"Aiohttp error: {e}. {retry + 1} Retryed.")
            except Exception as ex:
                logging.warning(f"Unexpected error: {ex}, {retry + 1} Retryed.")

            await asyncio.sleep(2**retry)
        raise ValueError(f"Failed after {retry + 1} retries. {result}")
    return wrapper

