"""The First Night: the candle-lighting show for the first night of Hanukkah.

The house dims to a low blue. The shamash kindles in the middle of Porch Front, then lights the rightmost light, the
first of the eight: its flame is carried along the porch to each one, landing on the first phrase of Ma'oz Tzur. The
rest of the hymn lets the glow spread. When the lights are lit, a warm glow spreads from the porch out along Left and
Right, and the flames settle and stay.

The show is built by pixelhome.hanukkah.Night, which every night shares: the places on Porch Front, the flames, and
the hymn's traditional melody (from the Union Hymnal, 1897) on an oboe over plain strings."""
from pixelhome.hanukkah import Night

CODE = 'HN01'
TITLE = 'The First Night'
KIND = 'show'
DESCRIPTION = ('The shamash kindles on the porch and lights one light for the first night of Hanukkah, '
               'one on each phrase of Ma\'oz Tzur, and a warm glow spreads over the house.')
VOICEOVER = 'The first night of Hanukkah, the Festival of Lights. One light, and the one that lights it.'

NIGHT = Night(1, __file__)


def render(G, seed=1):
    return NIGHT.render(G, seed)


def score(M, G):
    NIGHT.score(M, G)
