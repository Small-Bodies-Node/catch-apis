"""
...
"""

import typing
from enum import Enum, auto
# from sqlalchemy import Column, String, Integer, Enum as SQALEnum
# from sqlalchemy.ext.declarative import declarative_base


class EBodyType(Enum):
    """ Enum possible types of body for name_search """
    asteroid = auto()
    comet = auto()
    interstellar_object = auto()
    unknown = auto()
