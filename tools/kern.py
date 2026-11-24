"""Lector mínimo de Humdrum **kern para extraer voces monofónicas.

Devuelve, por cada voz, una lista de (midi|None, duración en negras).
Ignora archivos con divisiones de spine (*^) dentro de las voces **kern,
acordes dentro de una voz y valores irregulares (tresillos), para quedarse
solo con texturas sencillas y fiables.
"""
import re, sys, json, os
from fractions import Fraction as F

STEP = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}


def parse_token(tok):
    """Devuelve (dur Fraction|None, midi|None, tie_start, tie_end, is_rest, irregular)."""
    if tok in ('.', '') or tok.startswith('!') or tok.startswith('*') or tok.startswith('='):
        return None
    if ' ' in tok:
        raise ValueError('chord')
    if 'q' in tok or 'Q' in tok:  # nota de adorno
        return ('grace',)
    m = re.search(r'(\d+)(%\d+)?(\.*)', tok)
    if not m:
        raise ValueError('nodur:' + tok)
    num = int(m.group(1))
    if m.group(2):
        raise ValueError('rational')
    if num == 0:
        base = F(8)  # breve
        if re.search(r'(^|[^\d])00', tok):
            base = F(16)
    else:
        base = F(4, num)
    irregular = num not in (0, 1, 2, 4, 8, 16, 32, 64)
    dots = len(m.group(3))
    dur = base
    add = base
    for _ in range(dots):
        add /= 2
        dur += add
    if 'r' in tok:
        return (dur, None, False, False, True, irregular)
    pm = re.search(r'([a-gA-G])\1*', tok)
    if not pm:
        raise ValueError('nopitch:' + tok)
    letters = pm.group(0)
    ch = letters[0]
    n = len(letters)
    octave = 3 + n if ch.islower() else 4 - n
    step = STEP[ch.lower()]
    acc = 0
    rest_of = tok[pm.end():]
    acc += rest_of.count('#')
    acc -= rest_of.count('-')
    midi = 12 * (octave + 1) + step + acc
    tie_start = '[' in tok
    tie_end = ']' in tok or '_' in tok
    return (dur, midi, tie_start, tie_end, False, irregular)


def read(path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        lines = [l.rstrip('\n') for l in fh]
    meta = {}
    header = None
    kern_cols = []
    data = []
    for l in lines:
        if l.startswith('!!!'):
            k, _, v = l[3:].partition(':')
            meta.setdefault(k.strip(), v.strip())
            continue
        if l.startswith('!!') or not l:
            continue
        cols = l.split('\t')
        if header is None:
            if l.startswith('**'):
                header = cols
                kern_cols = [i for i, c in enumerate(cols) if c == '**kern']
            continue
        data.append(cols)
    if not header:
        raise ValueError('noheader')
    width = len(header)
    names = {i: '' for i in kern_cols}
    voices = {i: [] for i in kern_cols}
    irregular = 0
    measures = 0
    meter = None
    for cols in data:
        if len(cols) != width:
            raise ValueError('split')
        first = cols[0]
        if first.startswith('*'):
            for i in kern_cols:
                c = cols[i]
                if c in ('*^', '*v', '*+', '*x'):
                    raise ValueError('split')
                if c.startswith('*I"'):
                    names[i] = c[3:]
                if c.startswith('*M') and re.match(r'\*M\d+/\d+$', c) and meter is None:
                    meter = c[2:]
            continue
        if first.startswith('='):
            measures += 1
            continue
        if first.startswith('!'):
            continue
        for i in kern_cols:
            p = parse_token(cols[i])
            if p is None:
                continue
            if p[0] == 'grace':
                continue
            dur, midi, ts, te, rest, irr = p
            if irr:
                irregular += 1
            v = voices[i]
            if te and v and v[-1][0] == midi and midi is not None:
                v[-1][1] += dur
                v[-1][2] = ts
            else:
                v.append([midi, dur, ts])
    out = []
    for i in kern_cols:
        out.append({'name': names[i], 'notes': [(m, d) for m, d, _ in voices[i]]})
    # Humdrum lista la voz más grave primero: invertimos para soprano primero
    out.reverse()
    return meta, out, irregular, measures, meter


def stats(voices):
    tot = [sum(d for _, d in v['notes']) for v in voices]
    on = []
    for v in voices:
        t = F(0)
        s = set()
        for m, d in v['notes']:
            if m is not None:
                s.add(t)
            t += d
        on.append(s)
    allon = set().union(*on)
    sync = sum(1 for t in allon if sum(t in s for s in on) >= len(on) - 0) / max(1, len(allon))
    rng = []
    for v in voices:
        ps = [m for m, _ in v['notes'] if m is not None]
        rng.append((min(ps), max(ps)) if ps else (None, None))
    return tot, sync, rng


if __name__ == '__main__':
    res = []
    for p in sys.argv[1:]:
        try:
            meta, vs, irr, meas, meter = read(p)
            tot, sync, rng = stats(vs)
            res.append({'file': p, 'n': len(vs), 'names': [v['name'] for v in vs], 'quarters': float(max(tot)),
                        'equal': len(set(tot)) == 1, 'sync': round(sync, 2), 'rng': rng, 'irr': irr, 'meas': meas, 'meter': meter,
                        'com': meta.get('COM', ''), 'otl': meta.get('OTL', '') or meta.get('OTL@@LA', ''), 'cdt': meta.get('CDT', '')})
        except Exception as e:
            res.append({'file': p, 'err': str(e)[:40]})
    for x in res: print(json.dumps(x, ensure_ascii=False))
