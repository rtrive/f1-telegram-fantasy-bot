import logging

from adapters.persistence.jobstore import PTBSQLAlchemyJobStore
from core.configuration import DatabaseConfig

from telegram.ext import Updater

logger = logging.getLogger(name=__name__)
logger.setLevel(level="DEBUG")


class Bot:
    def __init__(self, api_key: str, db_config: DatabaseConfig):
        try:
            self.application = Updater(token=api_key)
            self.dispatcher = self.application.dispatcher
            self.dispatcher.job_queue.scheduler.add_jobstore(
                PTBSQLAlchemyJobStore(
                    dispatcher=self.dispatcher,
                    url=f"postgresql://{db_config.username}:{db_config.password}@{db_config.hostname}:{db_config.port}/{db_config.db_name}",  # noqa: E501
                )
            )
        except Exception as e:
            logger.error(e)

    def start_bot(self):
        try:
            self.application.start_polling()
            self.application.idle()
        except Exception as e:
            logger.error(e)
