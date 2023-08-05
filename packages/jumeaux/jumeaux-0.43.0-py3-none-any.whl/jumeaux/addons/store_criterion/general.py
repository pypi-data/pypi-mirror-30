# -*- coding:utf-8 -*-

from owlmixin import OwlMixin
from owlmixin.owlcollections import TList

from jumeaux.addons.store_criterion import StoreCriterionExecutor
from jumeaux.logger import Logger
from jumeaux.models import StoreCriterionAddOnPayload, Status

logger: Logger = Logger(__name__)


class Config(OwlMixin):
    statuses: TList[Status]


class Executor(StoreCriterionExecutor):
    def __init__(self, config: dict):
        self.config: Config = Config.from_dict(config or {})

    def exec(self, payload: StoreCriterionAddOnPayload) -> StoreCriterionAddOnPayload:
        if payload.stored:
            return payload

        stored: bool = payload.status in self.config.statuses
        logger.debug(f"Store: {stored}")

        return StoreCriterionAddOnPayload.from_dict({
            "status": payload.status,
            "path": payload.path,
            "qs": payload.qs,
            "headers": payload.headers,
            "res_one": payload.res_one,
            "res_other": payload.res_other,
            "stored": stored
        })
