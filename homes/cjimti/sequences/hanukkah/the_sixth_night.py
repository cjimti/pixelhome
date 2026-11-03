"""The Sixth Night: the candle-lighting show for the sixth night of Hanukkah.

The house dims to a low blue. The shamash kindles in the middle of Porch Front, then lights the six rightmost lights,
kindled left to right, newest first: its flame is carried along the porch to each one, landing on the first six
phrases of Ma'oz Tzur. The rest of the hymn lets the glow spread. When the lights are lit, a warm glow spreads from
the porch out along Left and Right, and the flames settle and stay.

The show is built by pixelhome.hanukkah.Night, which every night shares: the places on Porch Front, the flames, and
the hymn's traditional melody (from the Union Hymnal, 1897) on an oboe over plain strings."""
from pixelhome.hanukkah import Night

CODE = 'HN06'
TITLE = 'The Sixth Night'
KIND = 'show'
DESCRIPTION = ('The shamash kindles on the porch and lights six lights for the sixth night of Hanukkah, '
               'one on each phrase of Ma\'oz Tzur, and a warm glow spreads over the house.')

NIGHT = Night(6, __file__)


def render(G, seed=6):
    return NIGHT.render(G, seed)


def score(M, G):
    NIGHT.score(M, G)
