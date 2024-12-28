import os
import tempfile
from os import mkdir

from builders import Profile
from external.kcc.kindlecomicconverter.comic2ebook import main as make_ebook
from domain.models import Manga, Volume

class KccEpubBuilder:
    def __init__(self, manga: Manga, volumes: list[Volume]):
        self.manga = manga
        self.volumes = volumes

    def build(self, profile: Profile, output_path: str):
        for volume in self.volumes:
            print("Volume: ", volume.number, "Cover:", bool(volume.cover))
            workdir = tempfile.mkdtemp(suffix=f"_{volume.number}" , prefix=f"manga_build_{self.manga.id}")

            if volume.cover:
                volume.cover.write(workdir, "cover.png")
            else:
                if volume.chapters and volume.chapters[0].pages:
                    volume.chapters[0].pages[0].write(workdir, "cover.png")
                else:
                    continue

            for chapter in volume.chapters:
                if chapter.title:
                    chapter_path = os.path.join(workdir, f"{chapter.get_number()} - {chapter.title}")
                else:
                    chapter_path = os.path.join(workdir, str(chapter.get_number()))

                mkdir(chapter_path)
                for page in chapter.pages:
                    page.write(chapter_path)

            make_ebook([
                "--profile", profile.value,
                "--hq",
                "--upscale",
                "--title", f"{self.manga.title} - {volume.number}",
                "--author", self.manga.author,
                "--format", "EPUB",
                "--output", os.path.join(output_path, f"{self.manga.title}, Vol. {volume.number}.epub"),
                workdir,
            ])
