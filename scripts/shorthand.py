"""Shorthand transcription -> MusicXML (partwise 4.0), checking every bar adds up in every staff and voice.

    uv run python scripts/shorthand.py notes.py out.musicxml

The notes file is Python that defines:

  TITLE  'Elijah, No. 16: ...'
  SOURCE 'Novello, Ewer and Co. octavo vocal score (London, 1870)'   optional, the printing read, for <rights>
  COMPOSER, LYRICIST                               optional; default Mendelssohn and Bartholomew
  PARTS  [(pid, name, abbr, [staff, ...]), ...]   e.g. ('P5', 'Piano', 'Pno.', ['RH', 'LH'])
  CLEFS  {staff: ('G', 2, 0)}                      optional; defaults: names starting T -> treble 8vb, B/LH -> bass
  KEY    {bar: fifths}                             key signature from that bar on (bar 1 required)
  METER  {bar: (beats, beat_type)}                 time signature from that bar on (bar 1 required)
  TEMPO  {bar: (bpm, 'words')} or {bar: [(at, bpm, 'words'), ...]}   bpm in quarter notes a minute, at in sixteenths
  BARS   {bar: dict(staff='tokens', ...)}          a staff left out of a bar rests the whole bar

Pitches are as they SOUND (write the tenor an octave below its treble-clef notation). Durations are in sixteenths
(a 4/4 bar is 16, a 6/8 bar 12); a fraction is fine for triplets and 32nds (4/3 is a triplet sixteenth, 8/3 a triplet eighth, 1/2 a 32nd).
Token: PITCH[+PITCH...]:DUR[flags]["lyric"], or r:DUR for a rest. Flags: ~ tie to the next note of the same pitch,
. staccato, > accent, ^ fermata. A word !ff (any dynamic: pp p mp mf f ff fff sf sfz fz fp) sets the dynamic before
the next note. '|' separates voices on one staff. A lyric starting or ending with '-' joins its neighbours.
A staff string of just 'R' is a whole-bar rest.
"""
import re
import runpy
import sys
from fractions import Fraction as Fr
from xml.sax.saxutils import escape

DIV = 24                                            # divisions per quarter: 6 per sixteenth, so triplets and 32nds fit
PER16 = DIV // 4
TOK = re.compile(r'^(?P<p>r|[A-G](?:##|bb|#|b|n)?-?\d(?:\+[A-G](?:##|bb|#|b|n)?-?\d)*):(?P<d>\d+(?:/\d+)?)'
                 r'(?P<f>[~.>^]*)(?:"(?P<l>[^"]*)")?$')
TYPES = [(Fr(32), 'whole', 0), (Fr(24), 'half', 1), (Fr(16), 'half', 0), (Fr(12), 'quarter', 1), (Fr(8), 'quarter', 0),
         (Fr(6), 'eighth', 1), (Fr(4), 'eighth', 0), (Fr(3), '16th', 1), (Fr(2), '16th', 0), (Fr(1), '32nd', 0)]
# durations above are in 32nds; tokens are in sixteenths and doubled before lookup
DYNS = {'pppp', 'ppp', 'pp', 'p', 'mp', 'mf', 'f', 'ff', 'fff', 'sf', 'sfz', 'sffz', 'fz', 'fp', 'sfp', 'rf', 'rfz'}


def tokens(s):
    return [re.findall(r'!\w+|[^\s"]+(?:"[^"]*")?', v) for v in s.split('|')]


def pitch_xml(p):
    m = re.match(r'^([A-G])(##|bb|#|b|n)?(-?\d)$', p)
    step, acc, octv = m.group(1), m.group(2) or '', int(m.group(3))
    alt = {'#': 1, '##': 2, 'b': -1, 'bb': -2}.get(acc, 0)
    a = f'<alter>{alt}</alter>' if alt else ''
    return f'<pitch><step>{step}</step>{a}<octave>{octv}</octave></pitch>'


def note_type(d16):
    """(type, dots, tuplet) for a duration in sixteenths."""
    d32 = d16 * 2
    for v, t, dots in TYPES:
        if d32 == v:
            return t, dots, None
    for v, t, dots in TYPES:                         # a triplet: 2/3 of a plain value
        if dots == 0 and d32 * 3 == v * 2:
            return t, 0, (3, 2)
    for v, t, dots in TYPES:
        if d32 >= v:
            return t, dots, None
    return '32nd', 0, None


def syllabic(l):
    b, e = l.startswith('-'), l.endswith('-')
    return ('middle' if b and e else 'end' if b else 'begin' if e else 'single'), l.strip('-')


def default_clef(staff):
    if staff.startswith('T'):
        return ('G', 2, -1)
    if staff.startswith('B') or staff in ('LH', 'Bass'):
        return ('F', 4, 0)
    return ('G', 2, 0)


def at(table, bar):
    return table[max(k for k in table if k <= bar)]


def main(src, out):
    ns = runpy.run_path(src)
    BARS, PARTS, KEY, METER = ns['BARS'], ns['PARTS'], ns['KEY'], ns['METER']
    TEMPO, CLEFS, TITLE = ns.get('TEMPO', {}), ns.get('CLEFS', {}), ns.get('TITLE', '')
    SOURCE = ns.get('SOURCE', 'Novello, Ewer and Co. octavo vocal score (London, 1881)')
    COMPOSER = ns.get('COMPOSER', 'Felix Mendelssohn Bartholdy')
    LYRICIST = ns.get('LYRICIST', 'William Bartholomew (English version)')
    last = max(BARS)
    errors, open_ties = [], {}
    xml = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" '
           '"http://www.musicxml.org/dtds/partwise.dtd">',
           '<score-partwise version="4.0">',
           f'<work><work-title>{escape(TITLE)}</work-title></work>',
           f'<identification><creator type="composer">{escape(COMPOSER)}</creator>'
           f'<creator type="lyricist">{escape(LYRICIST)}</creator>'
           f'<rights>Transcribed from the {escape(SOURCE)}, public domain</rights>'
           '<encoding><software>pixelhome</software></encoding></identification>',
           '<part-list>']
    for pid, name, abbr, _ in PARTS:
        xml.append(f'<score-part id="{pid}"><part-name>{escape(name)}</part-name>'
                   f'<part-abbreviation>{escape(abbr)}</part-abbreviation></score-part>')
    xml.append('</part-list>')
    for pi, (pid, name, abbr, staves) in enumerate(PARTS):
        xml.append(f'<part id="{pid}">')
        for bar in range(1, last + 1):
            xml.append(f'<measure number="{bar}">')
            beats, btype = at(METER, bar)
            length = Fr(16 * beats, btype)                  # sixteenths in the bar
            attrs = []
            if bar == 1:
                attrs.append(f'<divisions>{DIV}</divisions>')
            if bar in KEY:
                attrs.append(f'<key><fifths>{KEY[bar]}</fifths></key>')
            if bar in METER:
                attrs.append(f'<time><beats>{beats}</beats><beat-type>{btype}</beat-type></time>')
            if bar == 1:
                if len(staves) > 1:
                    attrs.append(f'<staves>{len(staves)}</staves>')
                for i, s in enumerate(staves):
                    c = CLEFS.get(s, default_clef(s))
                    attrs.append(f'<clef number="{i + 1}"><sign>{c[0]}</sign><line>{c[1]}</line>'
                                 + (f'<clef-octave-change>{c[2]}</clef-octave-change>' if c[2] else '') + '</clef>')
            if attrs:
                xml.append('<attributes>' + ''.join(attrs) + '</attributes>')
            if pi == 0 and bar in TEMPO:
                tl = TEMPO[bar] if isinstance(TEMPO[bar], list) else [(0,) + tuple(TEMPO[bar])]
                for off, bpm, words in tl:
                    o = f'<offset>{int(Fr(off) * PER16)}</offset>' if off else ''
                    w = f'<direction-type><words font-weight="bold">{escape(words)}</words></direction-type>' if words else ''
                    xml.append(f'<direction placement="above">{w or "<direction-type><words/></direction-type>"}'
                               f'{o}<sound tempo="{bpm:g}"/></direction>')
            first = True
            for si, staff in enumerate(staves):
                text = BARS[bar].get(staff, 'R') if bar in BARS else 'R'
                if text.strip() == 'R':
                    text = f'r:{length}' if length.denominator == 1 else f'r:{length.numerator}/{length.denominator}'
                    whole = True
                else:
                    whole = False
                for vi, voice in enumerate(tokens(text)):
                    if not first:
                        xml.append(f'<backup><duration>{int(length * PER16)}</duration></backup>')
                    first = False
                    vnum = si * 4 + vi + 1
                    total = Fr(0)
                    for t in voice:
                        if t.startswith('!'):
                            if t[1:] not in DYNS:
                                errors.append(f'bar {bar} {staff}: unknown dynamic {t}')
                                continue
                            sn = f'<staff>{si + 1}</staff>' if len(staves) > 1 else ''
                            xml.append(f'<direction placement="below"><direction-type><dynamics><{t[1:]}/>'
                                       f'</dynamics></direction-type>{sn}</direction>')
                            continue
                        m = TOK.match(t)
                        if not m:
                            errors.append(f'bar {bar} {staff}: bad token {t!r}')
                            continue
                        d = Fr(m['d'])
                        if (d * PER16).denominator != 1:
                            errors.append(f'bar {bar} {staff}: duration {d} does not fit the divisions')
                            continue
                        total += d
                        typ, dots, tup = note_type(d)
                        flags = m['f']
                        ps = [] if m['p'] == 'r' else m['p'].split('+')
                        for k, p in enumerate(ps or [None]):
                            body = ['<note>']
                            if k:
                                body.append('<chord/>')
                            body.append(('<rest measure="yes"/>' if whole else '<rest/>') if p is None else pitch_xml(p))
                            body.append(f'<duration>{int(d * PER16)}</duration>')
                            key = (pid, staff, vi, p)
                            ties = []
                            if p is not None and key in open_ties:
                                ties.append('stop')
                                del open_ties[key]
                            if p is not None and '~' in flags:
                                ties.append('start')
                                open_ties[key] = bar
                            body += [f'<tie type="{x}"/>' for x in ties]
                            body.append(f'<voice>{vnum}</voice><type>{typ}</type>' + '<dot/>' * dots)
                            if tup:
                                body.append(f'<time-modification><actual-notes>{tup[0]}</actual-notes>'
                                            f'<normal-notes>{tup[1]}</normal-notes></time-modification>')
                            if len(staves) > 1:
                                body.append(f'<staff>{si + 1}</staff>')
                            nota = [f'<tied type="{x}"/>' for x in ties]
                            if '^' in flags and k == 0:
                                nota.append('<fermata type="upright"/>')
                            arts = ('<staccato/>' if '.' in flags else '') + ('<accent/>' if '>' in flags else '')
                            if arts:
                                nota.append(f'<articulations>{arts}</articulations>')
                            if nota:
                                body.append('<notations>' + ''.join(nota) + '</notations>')
                            if m['l'] and k == 0 and p is not None:
                                syl, txt = syllabic(m['l'])
                                body.append(f'<lyric number="1"><syllabic>{syl}</syllabic>'
                                            f'<text>{escape(txt)}</text></lyric>')
                            body.append('</note>')
                            xml.append(''.join(body))
                    if total != length:
                        errors.append(f'bar {bar} {staff} voice {vi + 1}: {total} sixteenths, not {length}')
            xml.append('</measure>')
        xml.append('</part>')
    xml.append('</score-partwise>')
    for k, b in open_ties.items():
        errors.append(f'tie from bar {b} never closed: {k}')
    if errors:
        print('\n'.join(errors))
        sys.exit(1)
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml) + '\n')
    print(f'wrote {out}: {last} bars')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
