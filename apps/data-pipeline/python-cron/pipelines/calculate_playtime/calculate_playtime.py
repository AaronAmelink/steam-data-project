import logging

from pipelines.calculate_playtime.tasks.get_playtime import GetPlaytime
from pipelines.calculate_playtime.tasks.import_user_data import ImportUserData
from pipelines.calculate_playtime.tasks.remove_old_playtime import RemoveOldPlaytime
from pipelines.utils.log_helper import configure_logger
from pipelines.utils.task_wrapper import timed_execute
from azure.azure_sql_client import AzureSQLClient

def main():
    configure_logger()

    logging.info("Starting Job")
    with AzureSQLClient() as sql:
        timed_execute(ImportUserData, sql)
        timed_execute(GetPlaytime, sql)
        timed_execute(RemoveOldPlaytime, sql)
    logging.info("Job Completed")

if __name__ == '__main__':
    main()
