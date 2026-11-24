"""Prepara las muestras de Ingroup: mono, recorte, fundido, MP3 y medición de afinación.

Uso: python3 -I build_samples.py SALIDA_DIR
Escribe SALIDA_DIR/<instrumento>/<midi>.mp3 y SALIDA_DIR/samples.json con la frecuencia real medida.
"""
import sys, os, re, json, subprocess, glob
import numpy as np

OUT = sys.argv[1]
SR = 44100
SETS = {
    'trompeta': sorted(glob.glob('/tmp/dl/VSCO-2-CE/Brass/Trumpet/sus/*_v1_rr1.wav')),
    'trombon': sorted(glob.glob('/tmp/dl/VSCO-2-CE/Brass/Tenor Trombone/sus/*_v2_1.wav')),
    'trompa': sorted(glob.glob('/tmp/dl/VSCO-2-CE/Brass/F Horn/sus/*_v2_1.wav') + glob.glob('/tmp/dl/VSCO-2-CE/Brass/F Horn/sus/*[DF]4_v1_1.wav')),
    'coro': sorted(glob.glob('/tmp/dl/sso/Sonatina Symphonic Orchestra/Samples-looped/Chorus/*.wav')),
}
KEEP = {'trompeta': 4.0, 'trombon': 4.0, 'trompa': 4.0, 'coro': 5.0}


def decode(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def yin(x, fmin=55, fmax=1500, W=2048):
    maxL = int(SR / fmin)
    d = np.array([np.sum((x[:W] - x[l:l + W]) ** 2) for l in range(1, maxL + 2)])
    run = np.cumsum(d)
    cm = d * np.arange(1, len(d) + 1) / np.maximum(run, 1e-12)
    minL = int(SR / fmax)
    tau = None
    for l in range(minL, maxL):
        if cm[l] < .15:
            while l + 1 < maxL and cm[l + 1] < cm[l]:
                l += 1
            tau = l
            break
    if tau is None:
        tau = minL + int(np.argmin(cm[minL:maxL]))
    a, b, c = cm[tau - 1], cm[tau], cm[tau + 1]
    den = a + c - 2 * b
    sh = (a - c) / (2 * den) if den else 0
    return SR / (tau + 1 + sh)


def pitch(x):
    """Mediana de la altura en la parte estable (entre 25 % y 75 %)."""
    n = len(x)
    fs = []
    for s in np.linspace(int(n * .25), int(n * .75) - 6000, 15).astype(int):
        seg = x[s:s + 6000]
        if np.sqrt(np.mean(seg ** 2)) < 1e-3:
            continue
        fs.append(yin(seg))
    fs = np.array(fs)
    med = np.median(fs)
    # descartar errores de octava
    fs = fs[np.abs(1200 * np.log2(fs / med)) < 50]
    return float(np.median(fs)), float(np.std(1200 * np.log2(fs / np.median(fs))))


man = {}
for inst, files in SETS.items():
    os.makedirs(os.path.join(OUT, inst), exist_ok=True)
    man[inst] = []
    for f in files:
        x = decode(f)
        start = int(np.argmax(np.abs(x) > 0.02 * np.max(np.abs(x))))
        start = max(0, start - int(.004 * SR))
        x = x[start:]
        keep = int(KEEP[inst] * SR)
        if len(x) > keep:
            x = x[:keep]
        fade = int(.08 * SR)
        x[-fade:] *= np.linspace(1, 0, fade)
        x = x / (np.max(np.abs(x)) + 1e-9) * .89
        f0, spread = pitch(x)
        midi = 69 + 12 * np.log2(f0 / 440)
        m = int(round(midi))
        dst = os.path.join(OUT, inst, f'{m}.mp3')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '96k', dst], input=x.astype(np.float32).tobytes(), check=True)
        # medir de nuevo sobre el MP3 final
        y = decode(dst)
        f1, sp1 = pitch(y)
        man[inst].append({'m': m, 'f': round(f1, 3), 'dur': round(len(y) / SR, 2), 'src': os.path.basename(f)})
        print(f'{inst:9} {os.path.basename(f)[:34]:34} -> {m} {f1:8.2f} Hz  {1200 * np.log2(f1 / (440 * 2 ** ((m - 69) / 12))):+6.1f} c  vib±{sp1:4.1f}c  {os.path.getsize(dst) // 1024} KB')
    man[inst].sort(key=lambda r: r['m'])
with open(os.path.join(OUT, 'samples.json'), 'w') as fh:
    json.dump(man, fh, separators=(',', ':'))
print('total KB', sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(OUT) for f in fs) // 1024)
