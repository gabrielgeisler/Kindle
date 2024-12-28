import time
from itertools import groupby
import requests
from api.base import BaseAPI
from domain.models import Chapter, ComicImage, Manga, Volume, VolumeInfo
from utils import cached, safe
from utils.ducktype import Duck
from utils.parallel import parallel_run
from utils.requester import download_image


class MangaDexApi(BaseAPI):
    HOST = "api.mangadex.org"
    COVER_HOST = "mangadex.org"

    def __init__(self, manga_id, lang):
        self.manga_id = manga_id
        self._manga_url = f"https://{MangaDexApi.HOST}/manga/{manga_id}?includes[]=author&includes[]=cover_art"
        self._feed_url = f"https://{MangaDexApi.HOST}/manga/{manga_id}/feed?limit=500&order[volume]=asc&order[chapter]=asc"
        self._aggregate_url = f"https://{MangaDexApi.HOST}/manga/{manga_id}/aggregate"
        self._covers_url = f"https://{MangaDexApi.HOST}/cover?order[volume]=asc&manga[]={manga_id}&limit=100&offset=0"
        self._lang = lang
    
    def get_manga(self) -> Manga:
        with requests.get(self._manga_url) as res:
            data = self._read(res.json()["data"])

        return Manga(
            id=data.id,
            title=self._fix_titles(data.title, data.altTitles)[self._lang],
            description=data.description[self._lang],
            author=data.author.name,
            language=self._lang,
        )

    def get_volumes_info(self) -> list[VolumeInfo]:
        with requests.get(self._aggregate_url) as res:
            data = self._read(res.json())["volumes"]

        #covers = self._get_covers()

        return sorted([
            VolumeInfo(
                number=safe(int, volume),
                cover=None,#covers.get(safe(int, volume)),
                chapters_numbers=sorted([
                    safe(float, c.chapter)
                    for c in vars(infos.chapters).values()
                ], key=lambda x: x or float('inf')),
            )
            for volume, infos in vars(data).items()
        ], key=lambda x: x.number or float('inf'))
    
    def get_volumes(self) -> list[Volume]:
        with requests.get(self._feed_url) as res:
            data = self._read(res.json()["data"])

        all_chapters = sorted([
            c for c in {
                d.chapter: Duck(dict(
                    id=d.id,
                    chapter=safe(float, d.chapter),
                    volume=safe(int, d.volume),
                    title=d.title,
                ))
                for d in data
                if d.translatedLanguage == self._lang and d.externalUrl is None
            }.values()
        ], key=lambda x: x.chapter)

        covers = self._get_covers()
        volumes = [
            Volume(
                number=number,
                cover=covers.get(number) or covers.get(None),
                chapters=[
                    Chapter(
                        id=chapter.id,
                        title=chapter.title,
                        number=chapter.chapter,
                        pages=self.get_pages(number, chapter.chapter, chapter.id)
                    )
                    for chapter in chapters
                ]
            )
            for number, chapters in groupby(all_chapters, lambda x: x.volume)
        ]

        def download(ci: ComicImage):
            ci.image = download_image(ci.url)

        parallel_run(
            [
                page
                for volume in volumes
                for chapter in volume.chapters
                for index, page in enumerate(chapter.pages)
            ],
            download,
            threads=10
        )
        return volumes

    
    def get_pages(self, volume_n, chapter_n, chapter_id) -> list[ComicImage]:
        print("--- get_pages", volume_n, chapter_n, chapter_id)
        chapter_url = f"https://{MangaDexApi.HOST}/at-home/server/{chapter_id}?forcePort443=false"
        with requests.get(chapter_url) as res:
            infos = self._read(res.json())

        if not infos.chapter:
            print("====== rate limited, waiting 30s")
            time.sleep(30)
            return self.get_pages(volume_n, chapter_n, chapter_id)

        return [
            image
            for _, image in sorted([
                (
                    index,
                    ComicImage(
                        filename=filename,
                        url=f"{infos.baseUrl}/data/{infos.chapter.hash}/{filename}",
                        image=None
                    )
                )
                for index, filename in enumerate(infos.chapter.data)
            ])
        ]
    
    def _fix_titles(self, default, alts):
        alts_complete = [d._data for d in list(alts) + [default]]
        return {
            list(a.keys())[0]: list(a.values())[0]
            for a in alts_complete
        }

    @cached
    def _get_covers(self):
        with requests.get(self._covers_url) as res:
            data = self._read(res.json()["data"])
        
        return {
            int(d.volume): ComicImage(
                filename=d.fileName,
                url=f"https://{MangaDexApi.COVER_HOST}/covers/{self.manga_id}/{d.fileName}",
                image=download_image(f"https://{MangaDexApi.COVER_HOST}/covers/{self.manga_id}/{d.fileName}"),
            )
            for d in data
            if safe(int, d.volume)
        }


    def _read(self, data):
        if type(data) is list:
            return [self._read(d) for d in data]
        
        attributes = data.get("attributes")
        if attributes:
            del data["attributes"]
            data.update(attributes)

        relationships = data.get("relationships")
        if relationships:
            del data["relationships"]
            data.update({
                r["type"] + ("_" + r["related"] if "related" in r else ""): self._read(r)
                for r in relationships
            })

        return Duck(data)
