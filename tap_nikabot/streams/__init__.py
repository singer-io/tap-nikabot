from typing import List, Type

from .groups import Groups
from .projects import Projects
from .records import Records
from .roles import Roles
from .stream import Stream
from .teams import Teams
from .users import Users

all_streams: List[Type[Stream]] = [Users, Roles, Groups, Teams, Projects, Records]


def get(stream_id: str) -> Type[Stream]:
    return next(s for s in all_streams if s.stream_id == stream_id)
