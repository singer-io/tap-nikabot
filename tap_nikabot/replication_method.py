from enum import Enum


class ReplicationMethod(Enum):
    FULL_TABLE = 1
    INCREMENTAL = 2
    LOG_BASED = 3
