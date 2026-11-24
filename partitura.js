/* Ingroup · grabado de partituras en páginas A4 (SVG) y exportación a PDF.
   Notación con la tipografía Leland (SMuFL, la de MuseScore) y textos con Edwin. Ambas SIL OFL 1.1.
   Uso: Partitura.render({title, composer, sub, meter, beat, bpm, bars, len, ferm, footer, staves:[{name, short, notes:[{t,d,m}]}]})
   - t, d en fusas (1/8 de negra); m = altura escrita (MIDI) o 0 para silencio.
   Cada nota lleva la clase "pn pn-<pentagrama>-<t>" para resaltarla. */
(function () {
  const PW = 595, PH = 842, ML = 44, MR = 40, SP = 8, HS = SP / 2, INK = '#111', FS = SP * 4;
  const MUS = "Leland", TXT = "Edwin,Georgia,'Times New Roman',serif";
  const G = { gClef: '', fClef: '', breve: '', whole: '', half: '', black: '',
    sharp: '', flat: '', natural: '', rWhole: '', rHalf: '', rQuarter: '', r8: '', r16: '',
    f8u: '', f8d: '', f16u: '', f16d: '', ferm: '', dot: '', mQ: '', mH: '', mDot: '' };
  const ts = n => String(n).split('').map(c => String.fromCharCode(0xE080 + +c)).join('');
  const VALS = [64, 48, 32, 24, 16, 12, 8, 6, 4, 3, 2, 1];
  const SPELL = [[0, 0], [0, 1], [1, 0], [2, -1], [2, 0], [3, 0], [3, 1], [4, 0], [5, -1], [5, 0], [6, -1], [6, 0]];
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const mus = (ch, x, y, size = FS, extra = '', fill = INK) => `<text x="${(+x).toFixed(2)}" y="${(+y).toFixed(2)}" font-family="${MUS}" font-size="${size}" fill="${fill}"${extra}>${ch}</text>`;
  const txt = (s, x, y, size, extra = '', fill = INK) => `<text x="${x}" y="${y}" font-family="${TXT}" font-size="${size}" fill="${fill}"${extra}>${esc(s)}</text>`;

  function decompose(d) { const out = []; while (d > 0) { const v = VALS.find(x => x <= d); out.push(v); d -= v; } return out; }

  /* Divide notas en compases y valores escribibles; marca ligaduras y calderones. */
  function events(notes, bars, ferm) {
    const fset = new Set(ferm), ev = [];
    for (const n of notes) {
      let d = n.d; const hasF = fset.has(n.t + n.d) && n.d > 8;
      if (hasF) d -= 8;
      const end = n.t + d, cuts = [n.t, ...bars.filter(b => b > n.t && b < end), end], pieces = [];
      for (let i = 0; i + 1 < cuts.length; i++) { let t = cuts[i]; for (const v of decompose(cuts[i + 1] - cuts[i])) { pieces.push({ t, d: v, m: n.m, src: n.t }); t += v; } }
      pieces.forEach((p, i) => { p.tie = !!n.m && i < pieces.length - 1; p.ferm = hasF && i === pieces.length - 1; });
      ev.push(...pieces);
    }
    return ev;
  }
  const diat = m => { const [st, ac] = SPELL[((m % 12) + 12) % 12]; return { d: (Math.floor(m / 12) - 1) * 7 + st, ac }; };
  const baseOf = d => d === 64 ? 64 : d >= 32 ? 32 : d >= 16 ? 16 : d >= 8 ? 8 : d >= 4 ? 4 : d >= 2 ? 2 : 1;
  const dotted = d => [48, 24, 12, 6, 3].includes(d);

  function restGlyph(d, x, y0) {
    const b = baseOf(d);
    let g = b >= 64 ? `<rect x="${x - 2}" y="${y0 + 8}" width="4" height="8" fill="${INK}"/>`
      : b === 32 ? mus(G.rWhole, x - 5.2, y0 + 8) : b === 16 ? mus(G.rHalf, x - 5.2, y0 + 16)
      : b === 8 ? mus(G.rQuarter, x - 3.8, y0 + 16) : b === 4 ? mus(G.r8, x - 4.4, y0 + 16) : mus(G.r16, x - 5.5, y0 + 16);
    if (dotted(d)) g += mus(G.dot, x + 7, y0 + 12);
    return g;
  }

  function render(o) {
    const nS = o.staves.length, multi = nS > 1;
    const bounds = [0, ...o.bars.filter(b => b > 0 && b < o.len), o.len];
    const evs = o.staves.map(s => events(s.notes, bounds.slice(1, -1), o.ferm || []));
    const measures = [];
    for (let i = 0; i + 1 < bounds.length; i++) {
      const a = bounds[i], b = bounds[i + 1], on = new Set([a]);
      evs.forEach(ev => ev.forEach(e => { if (e.t >= a && e.t < b) on.add(e.t); }));
      const tl = [...on].sort((x, y) => x - y), cols = [];
      tl.forEach((t, k) => {
        const nx = k + 1 < tl.length ? tl[k + 1] : b, dt = nx - t;
        let acc = false; evs.forEach(ev => ev.forEach(e => { if (e.t === t && e.m && SPELL[((e.m % 12) + 12) % 12][1]) acc = true; }));
        cols.push({ t, w: 11 + 7 * Math.log2(dt + 1) + (acc ? 8 : 0), acc });
      });
      measures.push({ a, b, cols, w: cols.reduce((s, c) => s + c.w, 0) + 10 });
    }
    const labelW = multi ? 34 : 0, avail0 = PW - ML - MR - labelW, LEAD0 = 64, LEAD = 36;
    const systems = []; let cur = [], used = 0;
    measures.forEach(m => {
      const av = avail0 - (systems.length === 0 ? LEAD0 : LEAD);
      if (cur.length && used + m.w > av) { systems.push(cur); cur = []; used = 0; }
      cur.push(m); used += m.w;
    });
    if (cur.length) systems.push(cur);
    const staffGap = 64, sysH = (nS - 1) * staffGap + 32, sysGap = multi ? 50 : 42;
    const pages = [], idx = []; let page = [], y = 0, pg = 0;
    const header = () => txt(o.title, PW / 2, 60, 22, ' text-anchor="middle" font-weight="bold"')
      + txt(o.composer, PW - MR, 88, 12, ' text-anchor="end"') + txt(o.sub, ML, 88, 12, ' font-style="italic"');
    const footer = n => txt((o.footer ? o.footer + ' · ' : '') + n, PW / 2, PH - 24, 8, ' text-anchor="middle"', '#777');
    const newPage = () => { if (page.length) pages.push(page); page = []; y = pages.length === 0 ? 140 : 60; pg++; if (pg === 1) page.push(header()); };
    newPage();
    systems.forEach((ms, si) => {
      if (y + sysH > PH - 56) { page.push(footer(pg)); newPage(); }
      const lead = si === 0 ? LEAD0 : LEAD, x0 = ML + labelW, av = avail0 - lead, nat = ms.reduce((s, m) => s + m.w, 0);
      const last = si === systems.length - 1, sc = last && nat / av < .62 ? 1 : av / nat;
      const tops = o.staves.map((_, k) => y + k * staffGap), xEnd = x0 + lead + nat * sc;
      let g = '';
      tops.forEach((y0, k) => {
        for (let i = 0; i < 5; i++) g += `<line x1="${x0}" x2="${xEnd}" y1="${y0 + i * SP}" y2="${y0 + i * SP}" stroke="${INK}" stroke-width=".9"/>`;
        g += mus(G.gClef, x0 + 6, y0 + 24);
        if (si === 0) { const [n, d] = o.meter.split('/'); g += mus(ts(n), x0 + 38, y0 + 8) + mus(ts(d), x0 + 38, y0 + 24); }
        if (multi) g += txt(o.staves[k].short || o.staves[k].name, x0 - 6, y0 + 19, 10, ' text-anchor="end"');
      });
      if (multi) g += `<line x1="${x0}" x2="${x0}" y1="${tops[0]}" y2="${tops[nS - 1] + 32}" stroke="${INK}" stroke-width="1.3"/>`;
      if (si === 0) g += mus(o.beat === 2 ? G.mH : G.mQ, x0 + 6, y - 22, 22) + (o.beat === 1.5 ? mus(G.mDot, x0 + 17, y - 22, 22) : '')
        + txt(`= ${o.bpm}`, x0 + (o.beat === 1.5 ? 24 : 20), y - 22, 12, ' font-weight="bold"');
      let mx = x0 + lead;
      ms.forEach((m, mi) => {
        const colX = {}; let cx = mx + 7 * sc;
        m.cols.forEach(c => { colX[c.t] = cx + (c.acc ? 8 * sc : 0) + 5; cx += c.w * sc; });
        const mEnd = mx + m.w * sc;
        o.staves.forEach((st, k) => {
          const y0 = tops[k], bot = y0 + 32, accSt = {}, ev = evs[k].filter(e => e.t >= m.a && e.t < m.b);
          const whole = ev.length === 1 && !ev[0].m;
          ev.forEach(e => {
            const x = colX[e.t];
            if (!e.m) {
              const rx = whole ? (mx + mEnd) / 2 : x;
              g += `<g class="pn pn-${k}-${e.src}">${restGlyph(whole && e.d >= 32 ? 32 : e.d, rx, y0)}</g>`;
              if (e.ferm) g += mus(G.ferm, rx - 10, y0 - 6);
              return;
            }
            const { d, ac } = diat(e.m), yy = bot - (d - 30) * HS, b = baseOf(e.d), up = d < 34;
            let out = '';
            const led = L => `<line x1="${x - 8}" x2="${x + 8}" y1="${bot - (L - 30) * HS}" y2="${bot - (L - 30) * HS}" stroke="${INK}" stroke-width="1.3"/>`;
            for (let L = 28; L >= d; L -= 2) out += led(L);
            for (let L = 40; L <= d; L += 2) out += led(L);
            const prev = accSt[d] ?? 0;
            if (ac !== prev && !e.tied) { out += mus(ac === 1 ? G.sharp : ac === -1 ? G.flat : G.natural, x - 5.2 - (ac === -1 ? 8.4 : 9.4), yy); accSt[d] = ac; }
            const hg = b >= 64 ? G.breve : b === 32 ? G.whole : b === 16 ? G.half : G.black, hw = b >= 64 ? 17.2 : b === 32 ? 11.9 : 10.4;
            out += `<g class="pn pn-${k}-${e.src}">${mus(hg, x - hw / 2, yy)}</g>`;
            if (b < 32) {
              const sx = up ? x + 5.2 - .4 : x - 5.2 + .4, y1 = up ? yy - 1.3 : yy + 1.3, y2 = up ? yy - 28 : yy + 28;
              out += `<line x1="${sx}" x2="${sx}" y1="${y1}" y2="${y2}" stroke="${INK}" stroke-width=".85"/>`;
              if (b <= 4) out += mus(b === 4 ? (up ? G.f8u : G.f8d) : (up ? G.f16u : G.f16d), sx - .4, y2);
            }
            if (dotted(e.d)) out += mus(G.dot, x + hw / 2 + 2.4, (d - 30) % 2 === 0 ? yy - 4 : yy);
            if (e.tie) {
              const i2 = evs[k].indexOf(e) + 1, nxt = evs[k][i2];
              const x2 = nxt && colX[nxt.t] !== undefined ? colX[nxt.t] - 5 : mEnd + 6, dir = up ? 1 : -1, ty = yy + dir * 6;
              out += `<path d="M${x + 4} ${ty}Q${(x + x2) / 2} ${ty + dir * 7} ${x2} ${ty}Q${(x + x2) / 2} ${ty + dir * 5.4} ${x + 4} ${ty}Z" fill="${INK}"/>`;
              if (nxt) nxt.tied = true;
            }
            if (e.ferm) out += mus(G.ferm, x - 10, Math.min(y0 - 6, yy - (up ? 32 : 10)));
            g += out;
          });
          const lastM = si === systems.length - 1 && mi === ms.length - 1;
          g += lastM ? `<line x1="${mEnd - 5.5}" x2="${mEnd - 5.5}" y1="${y0}" y2="${y0 + 32}" stroke="${INK}" stroke-width="1.4"/><line x1="${mEnd - 1.8}" x2="${mEnd - 1.8}" y1="${y0}" y2="${y0 + 32}" stroke="${INK}" stroke-width="4.4"/>`
            : `<line x1="${mEnd}" x2="${mEnd}" y1="${y0}" y2="${y0 + 32}" stroke="${INK}" stroke-width="1.4"/>`;
        });
        idx.push({ page: pages.length, y, a: m.a, b: m.b });
        mx = mEnd;
      });
      page.push(g);
      y += sysH + sysGap + (multi ? 4 : 12);
    });
    page.push(footer(pg));
    pages.push(page);
    return { pages: pages.map((p, i) => `<svg class="sheetpage" viewBox="0 0 ${PW} ${PH}" xmlns="http://www.w3.org/2000/svg" data-page="${i}"><rect width="${PW}" height="${PH}" fill="#fff"/>${p.join('')}</svg>`), idx, W: PW, H: PH };
  }

  /* ---- PDF (escrito a mano, sin librerías): una imagen JPEG por página A4 ---- */
  let fontCss = null;
  async function embeddedFonts() {
    if (fontCss !== null) return fontCss;
    const files = [['Leland', 'fonts/Leland-ingroup.woff', 'normal', 'normal'], ['Edwin', 'fonts/Edwin-Roman.woff', 'normal', 'normal'], ['Edwin', 'fonts/Edwin-Bold.woff', 'bold', 'normal'], ['Edwin', 'fonts/Edwin-Italic.woff', 'normal', 'italic']];
    let css = '';
    for (const [fam, url, w, st] of files) {
      try {
        const buf = new Uint8Array(await (await fetch(url)).arrayBuffer());
        let bin = ''; for (let i = 0; i < buf.length; i += 0x8000) bin += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
        css += `@font-face{font-family:${fam};font-weight:${w};font-style:${st};src:url(data:font/woff;base64,${btoa(bin)}) format('woff')}`;
      } catch (e) { /* sin la fuente, el PDF usa la del sistema */ }
    }
    fontCss = css;
    return css;
  }
  function svgToJpeg(svg, scale, css) {
    return new Promise((res, rej) => {
      const img = new Image();
      img.onload = () => {
        const c = document.createElement('canvas'); c.width = Math.round(PW * scale); c.height = Math.round(PH * scale);
        const x = c.getContext('2d'); x.fillStyle = '#fff'; x.fillRect(0, 0, c.width, c.height); x.drawImage(img, 0, 0, c.width, c.height);
        const u = c.toDataURL('image/jpeg', .9), b = atob(u.split(',')[1]), a = new Uint8Array(b.length);
        for (let i = 0; i < b.length; i++) a[i] = b.charCodeAt(i);
        URL.revokeObjectURL(img.src);
        res({ bytes: a, w: c.width, h: c.height });
      };
      img.onerror = () => rej(new Error('No se pudo dibujar la página'));
      const s = svg.replace(/ class="pn[^"]*"/g, '').replace(/(<svg[^>]*>)/, `$1<style>${css}</style>`);
      img.src = URL.createObjectURL(new Blob([s], { type: 'image/svg+xml' }));
    });
  }
  async function pdfBlob(pages) {
    const css = await embeddedFonts(), imgs = [];
    for (const p of pages) imgs.push(await svgToJpeg(p, 2.6, css));
    const enc = new TextEncoder(), parts = [], offs = []; let len = 0;
    const put = x => { const u = typeof x === 'string' ? enc.encode(x) : x; parts.push(u); len += u.length; };
    const obj = (n, ...body) => { offs[n] = len; put(`${n} 0 obj\n`); body.forEach(put); put('\nendobj\n'); };
    put('%PDF-1.4\n'); put(new Uint8Array([37, 226, 227, 207, 211, 10]));
    const N = pages.length, kids = [];
    for (let i = 0; i < N; i++) kids.push(`${3 + i * 3} 0 R`);
    obj(1, '<< /Type /Catalog /Pages 2 0 R >>');
    obj(2, `<< /Type /Pages /Kids [${kids.join(' ')}] /Count ${N} >>`);
    imgs.forEach((im, i) => {
      const pn = 3 + i * 3, cn = pn + 1, inum = pn + 2, cs = `q ${PW} 0 0 ${PH} 0 0 cm /Im0 Do Q`;
      obj(pn, `<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ${PW} ${PH}] /Resources << /XObject << /Im0 ${inum} 0 R >> >> /Contents ${cn} 0 R >>`);
      obj(cn, `<< /Length ${cs.length} >>\nstream\n${cs}\nendstream`);
      obj(inum, `<< /Type /XObject /Subtype /Image /Width ${im.w} /Height ${im.h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length ${im.bytes.length} >>\nstream\n`, im.bytes, '\nendstream');
    });
    const total = 3 + N * 3, xref = len;
    let x = `xref\n0 ${total}\n0000000000 65535 f \n`;
    for (let n = 1; n < total; n++) x += String(offs[n]).padStart(10, '0') + ' 00000 n \n';
    put(x + `trailer\n<< /Size ${total} /Root 1 0 R >>\nstartxref\n${xref}\n%%EOF\n`);
    return new Blob(parts, { type: 'application/pdf' });
  }
  async function pdf(pages, filename) {
    const blob = await pdfBlob(pages);
    try {
      const f = new File([blob], filename, { type: 'application/pdf' });
      if (navigator.canShare && navigator.canShare({ files: [f] }) && /iPhone|iPad|Android/i.test(navigator.userAgent)) { await navigator.share({ files: [f], title: filename }); return; }
    } catch (e) { if (e && e.name === 'AbortError') return; }
    const url = URL.createObjectURL(blob), a = document.createElement('a');
    a.href = url; a.download = filename; document.body.appendChild(a); a.click();
    setTimeout(() => { URL.revokeObjectURL(url); a.remove(); }, 5000);
  }

  window.Partitura = { render, pdf, pdfBlob, G, mus, ts };
})();
