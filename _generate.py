import os

from api.mangadex import MangaDexApi
from builders import Profile
from builders.epub import KccEpubBuilder

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


def build_manga(manga_id, lang):
    api = MangaDexApi(manga_id, lang)
    print("API", api.manga_id)

    manga = api.get_manga()
    print("Manga", manga.title)

    volumes = api.get_volumes()
    print("Volumes", len(volumes))

    builder = KccEpubBuilder(manga, volumes)
    builder.build(Profile.KindlePaperWhite, OUTPUT)


def get_info(manga_id, lang):
    api = MangaDexApi(manga_id, lang)
    print("API", api.manga_id)

    manga = api.get_manga()
    print("Manga", manga.title)

    volumes_infos = api.get_volumes_info()
    print("Volumes Infos", len(volumes_infos))


if __name__ == "__main__":
    build_manga("d8a959f7-648e-4c8d-8f23-f1f3f8e129f3", "en")
    #get_info("d8a959f7-648e-4c8d-8f23-f1f3f8e129f3", "en")
