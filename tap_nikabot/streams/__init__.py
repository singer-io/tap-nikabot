from typing import List, Type

from .projects import Projects
from .records import Records
from .stream import Stream
from .users import Users
from .roles import Roles
from .groups import Groups
from .teams import Teams

all_streams: List[Type[Stream]] = [Users, Roles, Groups, Teams, Projects, Records]


def get(stream_id: str) -> Type[Stream]:
    return next(s for s in all_streams if s.stream_id == stream_id)
