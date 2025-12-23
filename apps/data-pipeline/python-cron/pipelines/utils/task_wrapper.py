import time
import logging

from pipelines.classes.abstract_task import AbstractTask
import time
import logging

from pipelines.utils.status_codes import StatusCode

def timed_execute(cls, *args, **kwargs):
    """
    Run any AbstractTask subclass:
    - Instantiates the class
    - Executes it
    - Logs timing, errors, and status codes
    """
    start_time = time.time()
    cls_name = cls.__name__

    if not issubclass(cls, AbstractTask):
        raise TypeError(f"{cls_name} must inherit from AbstractTask")

    try:
        task_instance = cls(*args, **kwargs)
        result = task_instance.execute()
    except Exception as ex:
        logging.error(f"Error during {cls_name}.execute:", exc_info=ex)
        exit(1)

    if result == StatusCode.ERROR:
        logging.error(f"{cls_name}.execute encountered an error.")
        exit(1)

    elapsed_time = time.time() - start_time
    logging.info(f"{cls_name}.execute took {elapsed_time:.6f} seconds")

    if result == StatusCode.NO_DATA:
        logging.info(f"{cls_name}.execute returned status code: {result.name}")
        exit(0)

    return result
