"""Folded Flag: The whole roofline is a flag laid out along the path: the union (navy with white
stars) on the porch front, red and white stripes running out to both free ends. Then it is folded,
thirteen times, alternating left and right. Each fold is geometry, not a fade: the free end lifts
and rotates about the fold line, foreshortening as it rises (a bright crease where it stands on
edge), and lands mirrored on top of the strip, so the stripes visibly double back. The last fold on
each side tucks under, leaving only the stars on the porch, and the house warms in gold around it."""
import numpy as np
from pixelhome.fx import DT, hexc, perc, light, keys, smoothstep, Flicker, nframes

CODE = 'VT07'
TITLE = 'Folded Flag'
KIND = 'show'
DESCRIPTION = ('A flag laid out along the whole roof is folded thirteen times, end over end, until only the '
               'stars remain on the porch.')

NAVY = hexc('#1c34ff')
RED = hexc('#ff1410')
WHITE = hexc('#fff0dc')
STAR = hexc('#ffffff')
GOLD = hexc('#ff9a24')


def render(G, seed=27):
    rng = np.random.default_rng(seed)
    D = 72.0
    out = np.zeros((nframes(D), G.N, 3))
    pd = G.pd
    L = G.length
    da = pd[G.path[261]] - 2.0
    db = pd[G.path[331]] + 2.0
    pfc = (da + db) / 2
    twinkle = Flicker(rng, G.N, 0.1, 0.4)
    stars = np.zeros(G.N, bool)
    pf = G.seg['Porch Front']
    order = np.argsort(pd[pf])
    stars[pf[order][2::5]] = True
    stars[pf[order][4::10]] = False

    SW = 66.0

    def flag(o):
        """Colour (N,3) PWM for original flag coordinates o (nan = no cloth)."""
        c = np.zeros((len(o), 3))
        ok = ~np.isnan(o)
        oo = np.where(ok, o, 0)
        union = ok & (oo >= da) & (oo <= db)
        stripe_k = np.floor(np.abs(np.where(oo < pfc, da - oo, oo - db)) / SW).astype(int)
        red = ok & ~union & (stripe_k % 2 == 0)
        white = ok & ~union & ~red
        c[red] = perc(0.62) * RED
        c[white] = perc(0.5) * WHITE
        c[union] = perc(0.4) * NAVY
        return c, union

    # the grid holding, for each place on the roof, which flag coordinate is on top
    dx = 1.0
    grid = np.arange(0, L + dx, dx)
    top = grid.copy()

    # thirteen folds: 7 on the long left side, 6 on the right
    wl, wr = da / 7, (L - db) / 6
    folds = []
    eL, eR = 0.0, L
    sides = ['L', 'R'] * 6 + ['L']
    T0, dur, gap = 8.0, 2.9, 0.55
    nl = nr = 0
    for k, s in enumerate(sides):
        t0 = T0 + k * (dur + gap)
        if s == 'L':
            nl += 1
            f = eL + wl
            folds.append((t0, s, eL, f, nl == 7))
            eL = f
        else:
            nr += 1
            f = eR - wr
            folds.append((t0, s, eR, f, nr == 6))
            eR = f
    t_done = folds[-1][0] + dur

    def lookup(x):
        return np.interp(x, grid, top, left=np.nan, right=np.nan)

    applied = 0
    for fi in range(len(out)):
        t = fi * DT
        fr = out[fi]
        while applied < len(folds) and t >= folds[applied][0] + dur:
            t0, s, e, f, under = folds[applied]
            if s == 'L':
                moving = grid < f
                src = top.copy()
                top[moving] = np.nan
                if not under:
                    land = (grid >= f) & (grid <= 2 * f - e)
                    top[land] = np.interp(2 * f - grid[land], grid, src)
            else:
                moving = grid > f
                src = top.copy()
                top[moving] = np.nan
                if not under:
                    land = (grid <= f) & (grid >= 2 * f - e)
                    top[land] = np.interp(2 * f - grid[land], grid, src)
            applied += 1

        # unfurl: the flag is laid out from the porch outward
        reach = keys(t, [(0.5, 0), (6.5, max(pfc, L - pfc) + 40)])
        laid = smoothstep(-30, 0, reach - np.abs(pd - pfc))
        o = lookup(pd)
        c, union = flag(o)
        wave = 1 + 0.1 * np.sin(2 * np.pi * (pd / 260 - t / 2.4)) * (1 - smoothstep(6, 9, t))
        fr += c * laid[:, None] * wave[:, None]

        # the fold in progress
        cur = [fd for fd in folds if fd[0] <= t < fd[0] + dur]
        if cur:
            t0, s, e, f, under = cur[0]
            th = np.pi * smoothstep(t0, t0 + dur, t)
            ct = np.cos(th)
            sgn = 1 if s == 'L' else -1
            # remove the lifting piece from where it was
            lifted = (pd < f) if s == 'L' else (pd > f)
            fr[lifted] = 0
            if abs(ct) > 1e-3 and not (under and ct < 0):
                xs = f + (pd - f) / ct                  # where on the flat strip each roof point came from
                inside = (xs >= min(e, f)) & (xs <= max(e, f))
                if inside.any():
                    oc, _ = flag(lookup(xs[inside]))
                    shade = 0.45 + 0.55 * abs(ct)
                    fr[inside] = oc * shade
            crease = np.sin(th) * np.exp(-((pd - f) / (6 + 22 * np.sin(th))) ** 2)
            fr += light(WHITE, 0.5 * crease)

        # the night behind where the cloth has gone
        bare = fr.max(1) < perc(0.08)
        fr[bare] += light(NAVY, 0.08 * keys(t, [(0, 0), (2, 1)]) * np.ones(bare.sum()))

        # stars on the union
        st = 0.55 + 0.15 * twinkle(t)
        sel = stars & union
        fr[sel] = np.maximum(fr[sel], light(STAR, st[sel] * laid[sel]))

        # presented: gold gratitude gathers round the stars
        g = keys(t, [(t_done, 0), (t_done + 5, 1), (D - 4, 1), (D, 0)])
        if g > 0:
            empty = np.isnan(o)
            dd = np.abs(pd - pfc)
            glow = 0.22 * np.exp(-(dd / 900) ** 2) + 0.06
            fr[empty] += light(GOLD, g * glow[empty] * (1 + 0.1 * twinkle(t)[empty]))
            fr[sel] += light(STAR, 0.2 * g * np.ones(sel.sum()))
        end = keys(t, [(D - 4, 1), (D, 0)])
        fr *= end
    return out
