from random import choice
from string import ascii_letters, digits

from recipes.models import ShortLink


def create_short_link(recipe):
    try:
        return ShortLink.objects.get(recipe_id=recipe).link
    except ShortLink.DoesNotExist:
        chars = ascii_letters + digits
        links = list(ShortLink.objects.values("link"))
        link = "".join([choice(chars) for _ in range(5)])
        while link in links:
            link = "".join([choice(chars) for _ in range(5)])
        ShortLink.objects.create(recipe_id=recipe, link=link)
        return link
