"""Construye corales.js para Ingroup a partir de archivos Humdrum **kern.

Uso: python3 -I build_corales.py RAIZ_BACH RAIZ_POLACOS SALIDA.js
"""
import sys, re, json, os, itertools
from fractions import Fraction as F

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kern import parse_token  # noqa: E402

BACH, PL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]

SEL = [
    # (era, archivo, título, compositor, año, nota)
    ('ren', 'pl-wn/kern/pl-wn--sd-xvi-o-274_waclaw-z-szamotul--kancjonal-zamoyskich-psalm-dawidow-cxvi-laudate-dominum-alleluia-chwalcie-pana-boga.krn', 'Chwalcie Pana Boga (Salmo 117)', 'Wacław z Szamotuł', '~1550', ''),
    ('ren', 'pl-wn/kern/pl-wn--sd-xvi-qu-273--001-005_gomolka-mikolaj--melodiae-na-psalterz-polski-v-przypusc-panie-w-uszy-swoje.krn', 'Przypuść, Panie (Salmo 5)', 'Mikołaj Gomółka', '1580', ''),
    ('ren', 'pl-wn/kern/pl-wn--sd-xvi-qu-273--001-047_gomolka-mikolaj--melodiae-na-psalterz-polski-xlvii-kleszczmy-rekoma-wszyscy-zgodliwie.krn', 'Kleszczmy rękoma (Salmo 47)', 'Mikołaj Gomółka', '1580', ''),
    ('ren', 'pl-wn/kern/pl-wn--sd-xvi-qu-273--001-098_gomolka-mikolaj--melodiae-na-psalterz-polski-xcviii-nowy-monarsze-moznemu.krn', 'Nowy monarsze (Salmo 98)', 'Mikołaj Gomółka', '1580', ''),
    ('ren', 'pl-wn/kern/pl-wn--sd-xvi-qu-273--001-138_gomolka-mikolaj--melodiae-na-psalterz-polski-cxxxviii-ciebie-ja-chwalic-bede-ciebie-przed-moznymi.krn', 'Ciebie ja chwalić będę (Salmo 138)', 'Mikołaj Gomółka', '1580', ''),
    ('ren', 'pl-kk/kern/pl-kk--kk-i-6--026-005_palestrina-giovanni-pierluigi-da--missa-marcelli-papae-agnus-dei.krn', 'Agnus Dei (Missa Papae Marcelli)', 'G. P. da Palestrina', '1567', ''),
    ('ren', 'pl-gd/kern/pl-gd--ee-1638--006-024_marenzio-luca--il-quinto-libro-de-madrigalia-a-cinque-voci-liete-verdi-fiorite.krn', 'Liete verdi fiorite', 'Luca Marenzio', '1585', 'Madrigal'),
    ('ren', 'pl-gd/kern/pl-gd--ee-1638--006-003_marenzio-luca--il-quinto-libro-de-madrigalia-a-cinque-voci-quando-ripenso.krn', 'Quando ripenso', 'Luca Marenzio', '1585', 'Madrigal'),
    ('ren', 'pl-gd/kern/pl-gd--ee-1638--007-001_marenzio-luca--il-terzo-libro-de-madrigalia-a-sei-voci-io-moriro.krn', 'Io morirò', 'Luca Marenzio', '1585', 'Madrigal'),
    ('ren', 'pl-gd/kern/pl-gd--ee-1638--008-012_marenzio-luca--il-quarto-libro-de-madrigalia-a-sei-voci-caro-aminta.krn', 'Caro Aminta', 'Luca Marenzio', '1587', 'Madrigal'),
    ('bar', 'pl-kk/kern/pl-kk--kk-i-6--048_gorczycki-grzegorz-gerwazy--insignis-mater.krn', 'Insignis Mater', 'G. G. Gorczycki', '~1700', ''),
    ('bar', 'pl-kk/kern/pl-kk--kk-i-6--050_gorczycki-grzegorz-gerwazy--omni-die-dic-mariae.krn', 'Omni die dic Mariae (a 3)', 'G. G. Gorczycki', '~1700', ''),
    ('bar', 'pl-kk/kern/pl-kk--kk-i-7--105_gorczycki-grzegorz-gerwazy--omni-die-dic-mariae.krn', 'Omni die dic Mariae (a 4)', 'G. G. Gorczycki', '~1700', ''),
    ('bar', 'pl-kk/kern/pl-kk--kk-i-377--002_rozycki-jacek--o-maria-stella-maris.krn', 'O Maria, stella maris', 'Jacek Różycki', '~1680', ''),
    ('bar', 'pl-kk/kern/pl-kk--kk-i-336--001_gorczycki-grzegorz-gerwazy--ave-hierarchia.krn', 'Ave Hierarchia', 'G. G. Gorczycki', '~1700', ''),
    ('bar', 'BACH:chor032.krn', 'Nun danket alle Gott (BWV 386)', 'J. S. Bach', '', ''),
    ('bar', 'BACH:chor179.krn', 'Wachet auf (BWV 140/7)', 'J. S. Bach', '1731', ''),
    ('bar', 'BACH:chor074.krn', 'O Haupt voll Blut und Wunden (BWV 244/54)', 'J. S. Bach', '1727', ''),
    ('bar', 'BACH:chor020.krn', 'Ein feste Burg ist unser Gott (BWV 302)', 'J. S. Bach', '', ''),
    ('bar', 'BACH:chor138.krn', 'Jesu, meine Freude (BWV 64/8)', 'J. S. Bach', '1723', ''),
    ('bar', 'BACH:chor046.krn', 'Vom Himmel hoch (BWV 248/9)', 'J. S. Bach', '1734', ''),
    ('bar', 'BACH:chor006.krn', 'Christus, der ist mein Leben (BWV 281)', 'J. S. Bach', '', ''),
    ('bar', 'BACH:chor015.krn', 'Christ lag in Todesbanden (BWV 277)', 'J. S. Bach', '', ''),
    ('bar', 'BACH:chor065.krn', 'Was Gott tut, das ist wohlgetan (BWV 144/3)', 'J. S. Bach', '1724', ''),
    ('bar', 'BACH:chor146.krn', 'Wer nur den lieben Gott läßt walten (BWV 434)', 'J. S. Bach', '', ''),
    ('bar', 'BACH:chor270.krn', 'Befiehl du deine Wege (BWV 161/6)', 'J. S. Bach', '1715', ''),
    ('bar', 'BACH:chor216.krn', 'Es ist genug (BWV 60/5)', 'J. S. Bach', '1723', ''),
    ('cla', 'pl-cz/kern/pl-cz--iii-176--001-003_elsner-jozef--hymni-statio-tantum-ergo.krn', 'Tantum ergo', 'Józef Elsner', '~1800', ''),
    ('cla', 'pl-cz/kern/pl-cz--d-ii-31--001-005_elsner-jozef--msza-b-op-80-offertorium.krn', 'Offertorium (Misa op. 80)', 'Józef Elsner', '~1820', ''),
    ('rom', 'pl-wtm/kern/pl-wtm--r-405-m_moniuszko-stanislaw--hymn.krn', 'Hymn', 'Stanisław Moniuszko', '', ''),
    ('rom', 'pl-wtm/kern/pl-wtm--r-882-m--002_moniuszko-stanislaw--powrot-z-paryza-do-sabaudii.krn', 'Powrót z Paryża do Sabaudii', 'Stanisław Moniuszko', '', ''),
    ('rom', 'pl-wtm/kern/pl-wtm--r-882-m--001_moniuszko-stanislaw--chor-sabaudczykow.krn', 'Chór Sabaudczyków', 'Stanisław Moniuszko', '', ''),
    ('rom', 'pl-wn/kern/pl-wn--mus-1100_zelenski-wladyslaw--pije-kuba-do-jakuba.krn', 'Pije Kuba do Jakuba', 'Władysław Żeleński', '', 'Canción popular'),
]

DROP = {'Tantum ergo': ('violone',), 'Ave Hierarchia': ('ripieno',)}
NAMES = [(r'^(cant|disc|sopr)', 'Soprano'), (r'^alt', 'Alto'), (r'^teno', 'Tenor'), (r'^(bas|bass)', 'Bajo'), (r'^(qv|qu)', 'Quinto'), (r'^sest', 'Sexto'), (r'^bari', 'Barítono')]


def nice(raw):
    r = re.sub(r'[\[\]\.]', '', raw).replace('ſ', 's').strip().lower()
    num = re.search(r'([12])\s*(o|do|°|m|d)?\b', r)
    base = next((v for k, v in NAMES if re.search(k, r.split()[-1] if re.match(r'^\d', r) else r)), None)
    if base is None:
        return raw.strip().title() or ''
    extra = ''
    if num:
        extra = ' ' + num.group(1)
    if 'ad lib' in r:
        extra += ' (ad lib.)'
    return base + extra


HOLD = F(1)  # negras añadidas en cada calderón
UNIT = F(1, 8)  # fusa: unidad mínima de duración


def read_full(path):
    with open(path, encoding='utf-8', errors='replace') as fh:
        lines = [l.rstrip('\n') for l in fh]
    meta, header, data = {}, None, []
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
            continue
        data.append(cols)
    kc = [i for i, c in enumerate(header) if c == '**kern']
    W = len(header)
    names = {i: '' for i in kc}
    key = None
    meter = None
    voices = {i: [] for i in kc}
    t = {i: F(0) for i in kc}
    bars, ferm = [], set()
    for cols in data:
        assert len(cols) == W, 'split'
        a = cols[0]
        if a.startswith('*'):
            for i in kc:
                c = cols[i]
                assert c not in ('*^', '*v', '*+', '*x'), 'split'
                if c.startswith('*I"'):
                    names[i] = c[3:]
                if key is None and re.match(r'\*k\[', c):
                    key = c
                if meter is None and re.match(r'\*M\d+/\d+$', c):
                    meter = c[2:]
            continue
        if a.startswith('='):
            tt = max(t.values())
            if tt > 0 and (not bars or bars[-1] != tt):
                bars.append(tt)
            continue
        if a.startswith('!'):
            continue
        for i in kc:
            tok = cols[i]
            p = parse_token(tok)
            if p is None or p[0] == 'grace':
                continue
            dur, midi, ts, te, rest, irr = p
            assert not irr, 'irregular'
            v = voices[i]
            if ';' in tok:
                ferm.add(t[i] + dur)
            if te and v and v[-1][0] == midi and midi is not None:
                v[-1][1] += dur
            else:
                v.append([midi, dur])
            t[i] += dur
    tots = set(t.values())
    assert len(tots) == 1, ('desiguales', tots)
    out = [(names[i], voices[i]) for i in kc]
    return meta, out, key, bars, sorted(ferm), tots.pop(), meter


def stretch(voices, bars, ferm, total):
    fs = [f for f in ferm if f < total] + ([total] if total in ferm else [])

    def m(x):
        return x + HOLD * sum(1 for f in fs if f <= x and f < total) + (HOLD if (x == total and total in ferm) else 0)
    nv = []
    for name, notes in voices:
        t = F(0)
        res = []
        for midi, d in notes:
            a, b = m(t), m(t + d)
            res.append([midi, b - a])
            t += d
        nv.append((name, res))
    return nv, [m(b) for b in bars if b < total], m(total)


def merge_rests(notes):
    out = []
    for midi, d in notes:
        if midi is None and out and out[-1][0] is None:
            out[-1][1] += d
        else:
            out.append([midi, d])
    return out


LO, HI_LEAD, HI = 52, 81, 79  # Sol♯3..La5 escrito aprox. para trompeta en Si♭ (concierto Mi3..La5)


def keysig(key):
    if not key:
        return 0
    s = key[3:-1]
    return s.count('#') - s.count('-')


def fit(voices, key):
    rngs = []
    for _, notes in voices:
        ps = [p for p, _ in notes if p is not None]
        rngs.append((min(ps), max(ps), sum(ps) / len(ps)))
    n = len(voices)
    best = None
    for T in range(-6, 7):
        sig = keysig(key) + 7 * (T + 2)
        sig = ((sig + 6) % 12) - 6
        kp = max(0, abs(sig) - 2) * 3
        for offs in itertools.product((0, 12, 24, -12), repeat=n):
            ok = True
            cost = abs(T) * 0.5 + kp
            for i, (lo, hi, mean) in enumerate(rngs):
                L, H = lo + T + offs[i], hi + T + offs[i]
                top = HI_LEAD if i == 0 else HI
                if L < LO or H > top:
                    ok = False
                    break
                cost += abs(offs[i]) / 12 * 2
            if not ok:
                continue
            means = [rngs[i][2] + T + offs[i] for i in range(n)]
            for i in range(n - 1):
                if means[i] < means[i + 1]:
                    cost += 4 + (means[i + 1] - means[i]) * 0.5
            span = max(r[1] + T + offs[i] for i, r in enumerate(rngs)) - min(r[0] + T + offs[i] for i, r in enumerate(rngs))
            cost += span * 0.05
            if best is None or cost < best[0]:
                best = (cost, T, offs)
    return best


def main():
    out = []
    report = []
    for era, f, title, comp, year, note in SEL:
        path = os.path.join(BACH, f[5:]) if f.startswith('BACH:') else os.path.join(PL, f)
        meta, voices, key, bars, ferm, total, meter = read_full(path)
        num, den = (int(x) for x in (meter or '4/4').split('/'))
        beat = 2 if den in (1, 2) else (1.5 if den == 8 and num % 3 == 0 else 1)
        bpm = 60 if beat != 1 else (66 if f.startswith('BACH:') else 76)
        voices = [(n, merge_rests(v)) for n, v in voices if not any(d in n.lower() for d in DROP.get(title, ()))]
        voices.sort(key=lambda nv: -sum(p for p, _ in nv[1] if p is not None) / max(1, sum(1 for p, _ in nv[1] if p is not None)))
        voices, bars, total = stretch(voices, bars, ferm, total)
        for _, notes in voices:
            assert sum(d for _, d in notes) == total
            for _, d in notes:
                assert (d / UNIT).denominator == 1, ('unit', d)
        fb = fit(voices, key)
        assert fb, ('nofit', title)
        _, T, offs = fb
        nm = [nice(n) or f'Voz {i + 1}' for i, (n, _) in enumerate(voices)]
        enc = [[x for p, d in notes for x in ((p or 0), int(d / UNIT))] for _, notes in voices]
        src = 'bach' if f.startswith('BACH:') else 'pl'
        ident = re.sub(r'[^a-z0-9]+', '-', (comp.split()[-1] + '-' + title).lower()).strip('-')[:48]
        out.append({'id': ident, 'era': era, 't': title, 'c': comp, 'y': year, 'note': note, 'src': src, 'file': os.path.basename(f.replace('BACH:', '')),
                    'v': nm, 'm': meter or '4/4', 'beat': beat, 'bpm': bpm, 'T': T, 'o': list(offs), 'bars': [int(b / UNIT) for b in bars], 'n': enc})
        rng = []
        for i, (_, notes) in enumerate(voices):
            ps = [p for p, _ in notes if p is not None]
            rng.append(f'{min(ps) + T + offs[i]}-{max(ps) + T + offs[i]}')
        report.append(f'{era} {len(voices)}v {title[:34]:34} T{T:+d} o{offs} q{float(total):.0f} {" ".join(rng)}')
    js = '/* Corales de Ingroup. Fuentes: ver créditos en la app.\n   J. S. Bach: edición digital de Craig Stuart Sapp (CC BY-NC-SA 4.0), github.com/craigsapp/bach-370-chorales\n   Resto: Polish Music Heritage in Open Access, Instituto Fryderyk Chopin (CC BY 4.0), github.com/pl-wnifc/humdrum-polish-scores\n   Formato: n = por voz [midi, duración en fusas, ...] con 0 = silencio. T = transporte; o = octava por voz para trompetas. */\n'
    js += 'window.CORALES=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n'
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write(js)
    print('\n'.join(report))
    print('bytes', len(js.encode()))


main()
