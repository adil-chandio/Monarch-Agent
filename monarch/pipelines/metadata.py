from monarch.packaging.listing import listing
from monarch.packaging.thumbs import five_variants
from monarch.packaging.titles import titles_from_idea
from monarch.schemas import Channel, Idea, Scene


def package(idea: Idea, scenes: list[Scene], channel: Channel, extras: list[str] | None = None):
    titles = titles_from_idea(idea, extras)
    if not titles:
        raise ValueError("no title passed the gate")
    return {
        "titles": titles,
        "listing": listing(idea, scenes, titles[0]),
        "thumbs": five_variants(idea, channel),
    }
