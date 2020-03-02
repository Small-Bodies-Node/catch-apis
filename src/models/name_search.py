
"""
ORM Model for table of object names to be used in word-search service
"""

import typing
from enum import Enum, auto
from sqlalchemy import Column, String, Integer, Enum as SQALEnum
from sqlalchemy.ext.declarative import declarative_base

base: typing.Any = declarative_base()


class EBodyType(Enum):
    """ Enum possible types of body for name_search """
    asteroid = auto()
    comet = auto()
    interstellar_object = auto()
    unknown = auto()


class NameSearch(base):
    """ ORM Class for small-bodies name search"""

    __tablename__ = 'name_search'

    target = Column(String, primary_key=True)
    """
        The `target` property/field is the string that we want to ascertain in order
        to feed to sbsearch (which in turn pings foreign apis). This string needs to be exact.
        The whole point of the name-search functionality is to map the user's fuzzy name searches to this exact text. This field is named here 'target' in order to mirror the term used in sbsearch, but a more thorough label for this property/field might look like `text_that_will_unlock_external_apis`
    """
    comparison_text = Column(String)
    """
        The `comparison_text` is the field in the sql table that will be indexed and used to find an ordered list of closest matches to whatever text the user types in. The user will never see this.
    """

    display_text = Column(String)
    """
        The `displayable_text` is the neat-looking text the user will get shown when potential matches are returned. The user will then click on one of these options to select it. When the user submits a search for that item, a request will be sent with the corresponding `target` to the query route of our api.
    """

    body_type = Column(String)
    """
        Discrete types of body.
    """

    def __init__(self, target: str, comparison_text: str, display_text: str, body_type: str) -> None:
        self.target = target
        self.comparison_text = comparison_text
        self.display_text = display_text
        self.body_type = body_type

    def __repr__(self) -> str:
        return "NameSearch()"

    def __str__(self) -> str:
        return "<Class NameSearch: " + \
            str(self.target) + " " + \
            str(self.comparison_text) + " " + \
            str(self.display_text) + " " + \
            str(self.body_type) + \
            ">"
