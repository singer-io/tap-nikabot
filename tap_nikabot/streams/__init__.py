from typing import List, Type

from .stream import Stream
from .users import Users
from .roles import Roles

all_streams: List[Type[Stream]] = [Users, Roles]
