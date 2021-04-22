import random
from time import sleep

MAX_RETRY_ATTEMPTS = 10
MAX_RETRY_WAIT = 10

random.seed()

def retry(max_attempts=MAX_RETRY_ATTEMPTS, max_wait=MAX_RETRY_WAIT, log=True):
    def logger(*msgs):
        if log:
            for msg in msgs:
                print(msg)

    def wrapper(func):
        def retryer(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    logger("Exception caught: ", ex)

                    if attempt != max_attempts:
                        secs = random.uniform(0, min(max_wait, 2 ** attempt))
                        msecs = round(secs * 1000)

                        logger(f"Waiting for {msecs}ms")
                        sleep(secs)
                    else:
                        logger(f"{max_attempts} retries failed; aborting")
                        raise

        return retryer

    return wrapper
