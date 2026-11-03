"""The Eighth Night: the candle-lighting show for the eighth night of Hanukkah.

The house dims to a low blue. The shamash kindles in the middle of Porch Front, then lights the eight rightmost
lights, kindled left to right, newest first: its flame is carried along the porch to each one, landing on the first
eight phrases of Ma'oz Tzur. When the lights are lit, a warm glow spreads from the porch out along Left and Right, and
the flames settle and stay.

The show is built by pixelhome.hanukkah.Night, which every night shares: the places on Porch Front, the flames, and
the hymn's traditional melody (from the Union Hymnal, 1897) on an oboe over plain strings."""
from pixelhome.hanukkah import Night

CODE = 'HN08'
TITLE = 'The Eighth Night'
KIND = 'show'
DESCRIPTION = ('The shamash kindles on the porch and lights eight lights for the eighth night of Hanukkah, '
               'one on each phrase of Ma\'oz Tzur, and a warm glow spreads over the house.')

NIGHT = Night(8, __file__)


def render(G, seed=8):
    return NIGHT.render(G, seed)


def score(M, G):
    NIGHT.score(M, G)
