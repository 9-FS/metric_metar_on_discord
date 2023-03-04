import enum


class Doc_Type(enum.Enum):
    """
    Handling which type of document?
    """

    METAR=enum.auto()
    TAF  =enum.auto()