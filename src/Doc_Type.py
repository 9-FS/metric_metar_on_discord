#Copyright (c) 2023 구FS, all rights reserved. Subject to the CC BY-NC-SA 4.0 licence in `licence.md`.
import enum


class Doc_Type(enum.Enum):
    """
    Handling which type of document?
    """

    METAR=enum.auto()
    TAF  =enum.auto()