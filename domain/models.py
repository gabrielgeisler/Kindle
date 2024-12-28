import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ComicImage:
    filename: str
    url: str
    image: Optional[bytes]

    def write(self, path, filename=None):
        with open(os.path.join(path, filename or self.filename), "wb") as f:
            f.write(self.image)

@dataclass
class Manga:
    id: str
    title: str
    description: str
    author: str
    language: str


@dataclass
class Chapter:
    id: str
    title: str
    number: float
    pages: list[ComicImage]

    def get_number(self):
        if self.number.is_integer():
            return int(self.number)
        return self.number


@dataclass
class Volume:
    number: int
    chapters: list[Chapter]
    cover: ComicImage


@dataclass
class VolumeInfo:
    number: int
    chapters_numbers: list[float]
    cover: ComicImage
