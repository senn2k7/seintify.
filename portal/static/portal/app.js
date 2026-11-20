/* Interaksi & animasi Portal Prediksi Nilai */
(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fmt = function (n, d) { return n.toLocaleString('id-ID', { minimumFractionDigits: d, maximumFractionDigits: d }); };
  var easeOut = function (t) { return 1 - Math.pow(1 - t, 4); };

  /* ---- Progress scroll + bayangan navbar ---- */
  var prog = $('#progress'), atas = $('.atas');
  function onScroll() {
    var h = document.documentElement, max = h.scrollHeight - h.clientHeight;
    if (prog) prog.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + '%';
    if (atas) atas.classList.toggle('scrolled', h.scrollTop > 8);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---- Menu seluler ---- */
  var burger = $('.burger');
  if (burger && atas) {
    burger.addEventListener('click', function () {
      var buka = atas.classList.toggle('buka');
      burger.setAttribute('aria-expanded', buka ? 'true' : 'false');
    });
    $$('.menu a').forEach(function (a) { a.addEventListener('click', function () { atas.classList.remove('buka'); }); });
  }

  /* ---- Hitung naik angka ---- */
  function countUp(el) {
    var target = parseFloat(el.getAttribute('data-count'));
    var dec = parseInt(el.getAttribute('data-dec') || '0', 10);
    if (isNaN(target)) return;
    if (reduce) { el.textContent = fmt(target, dec); return; }
    var dur = 1500, t0 = null;
    function step(ts) {
      if (t0 === null) t0 = ts;
      var p = Math.min((ts - t0) / dur, 1);
      el.textContent = fmt(target * easeOut(p), dec);
      if (p < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }

  /* ---- Bar koefisien (relatif terhadap yang terbesar) ---- */
  var koefAll = $$('[data-koef]');
  var koefMax = koefAll.reduce(function (m, el) { return Math.max(m, parseFloat(el.getAttribute('data-koef')) || 0); }, 0) || 1;
  koefAll.forEach(function (el) {
    el.style.setProperty('--w', ((parseFloat(el.getAttribute('data-koef')) / koefMax) * 100).toFixed(1) + '%');
  });

  /* ---- Grafik batang: skala sumbu-Y yang jujur ---- */
  var chart = $('.chart');
  if (chart) {
    var kols = $$('.batang-kolom', chart);
    var vals = kols.map(function (k) { return parseFloat(k.getAttribute('data-val')); });
    var mn = Math.min.apply(null, vals), mx = Math.max.apply(null, vals), rg = Math.max(mx - mn, 1);
    var step = rg > 12 ? 5 : 2;
    var lo = Math.max(0, Math.floor((mn - rg * 0.6) / step) * step);
    var hi = Math.min(100, Math.ceil((mx + rg * 0.18) / step) * step);
    if (hi <= lo) hi = lo + step;
    var grid = $('.ygrid', chart), html = '';
    for (var t = lo; t <= hi; t += step) {
      html += '<i style="bottom:' + ((t - lo) / (hi - lo) * 100) + '%"><span>' + t + '</span></i>';
    }
    if (grid) grid.innerHTML = html;
    kols.forEach(function (k, i) {
      var p = Math.max(2, (vals[i] - lo) / (hi - lo) * 100);
      var b = $('.batang', k);
      b.style.setProperty('--h', p + '%');
      b.style.setProperty('--k', i);
      k.style.setProperty('--tinggi', p + '%');
    });
    var cat = $('#sumbu-catatan');
    if (cat && lo > 0) cat.textContent = 'Catatan: sumbu vertikal dimulai dari ' + lo + ' (bukan 0) agar selisih antar kelompok terlihat jelas.';
  }

  /* ---- Reveal & pemicu animasi saat terlihat ---- */
  $$('.stagger').forEach(function (g) {
    $$(':scope > .reveal', g).forEach(function (el, i) { el.style.setProperty('--i', i); });
  });
  $$('.hero-teks .reveal, .judul-halaman .reveal').forEach(function (el, i) { el.style.setProperty('--i', i); });
  $$('.alur .langkah').forEach(function (el, i) { el.style.setProperty('--i', i); });

  function trigger(el) {
    if (el.classList.contains('reveal')) el.classList.add('in');
    if (el.hasAttribute('data-anim')) {
      el.classList.add('go');
      $$('[data-count]', el).forEach(countUp);
    }
  }
  var targets = $$('.reveal, [data-anim]');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { trigger(e.target); io.unobserve(e.target); }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
    targets.forEach(function (t) { io.observe(t); });
  } else {
    targets.forEach(trigger);
  }

  /* ---- Cahaya mengikuti kursor pada kartu ---- */
  $$('.card').forEach(function (c) {
    c.addEventListener('pointermove', function (e) {
      var r = c.getBoundingClientRect();
      c.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      c.style.setProperty('--my', (e.clientY - r.top) + 'px');
    });
  });

  /* ---- Tilt 3D pada kartu hero ---- */
  $$('[data-tilt]').forEach(function (el) {
    if (reduce) return;
    var wrap = el.parentElement;
    wrap.addEventListener('pointermove', function (e) {
      var r = wrap.getBoundingClientRect();
      var x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
      el.classList.add('aktif');
      el.style.transform = 'rotateY(' + (x * 16) + 'deg) rotateX(' + (-y * 16) + 'deg)';
    });
    wrap.addEventListener('pointerleave', function () { el.classList.remove('aktif'); el.style.transform = ''; });
  });

  /* ---- Efek riak pada tombol ---- */
  $$('.btn').forEach(function (b) {
    b.addEventListener('click', function (e) {
      if (reduce) return;
      var r = b.getBoundingClientRect(), s = Math.max(r.width, r.height);
      var d = document.createElement('span');
      d.className = 'ripple';
      d.style.cssText = 'width:' + s + 'px;height:' + s + 'px;left:' + (e.clientX - r.left - s / 2) + 'px;top:' + (e.clientY - r.top - s / 2) + 'px';
      b.appendChild(d);
      setTimeout(function () { d.remove(); }, 650);
    });
  });

  /* ---- Form: slider <-> input angka + pratinjau langsung ---- */
  var form = $('#form-prediksi');
  var pv = { nilai: $('#pratinjau-nilai'), isi: $('#pratinjau-isi') };
  function pratinjau() {
    if (!form || !pv.nilai) return;
    var total = parseFloat(form.getAttribute('data-intercept')), ok = !isNaN(total);
    $$('.field', form).forEach(function (f) {
      var num = $('input[type=number]', f), b = parseFloat(f.getAttribute('data-b')), v = parseFloat(num.value);
      if (isNaN(v) || isNaN(b)) ok = false; else total += b * v;
    });
    if (!ok) { pv.nilai.textContent = '–'; pv.isi.style.width = '0'; return; }
    total = Math.min(100, Math.max(0, total));
    pv.nilai.textContent = fmt(total, 1);
    pv.isi.style.width = total + '%';
  }
  $$('.field').forEach(function (f) {
    var num = $('input[type=number]', f), rng = $('input[type=range]', f);
    if (!num || !rng) return;
    var min = parseFloat(rng.min), max = parseFloat(rng.max);
    function paint() {
      var v = parseFloat(rng.value);
      rng.style.setProperty('--p', ((v - min) / (max - min) * 100) + '%');
    }
    rng.addEventListener('input', function () {
      num.value = rng.value; paint(); pratinjau();
      var box = num.parentElement; box.classList.remove('pop'); void box.offsetWidth; box.classList.add('pop');
    });
    num.addEventListener('input', function () {
      var v = parseFloat(num.value);
      if (!isNaN(v)) { rng.value = Math.min(max, Math.max(min, v)); paint(); }
      pratinjau();
    });
    num.value = num.value || rng.value;
    if (num.value !== '' && !isNaN(parseFloat(num.value))) rng.value = Math.min(max, Math.max(min, parseFloat(num.value)));
    paint();
  });
  pratinjau();

  /* ---- Preset cepat ---- */
  $$('[data-preset]').forEach(function (b) {
    b.addEventListener('click', function () {
      var vals = b.getAttribute('data-preset').split(',');
      $$('#form-prediksi .field').forEach(function (f, i) {
        var rng = $('input[type=range]', f);
        if (rng && vals[i] !== undefined) { rng.value = vals[i]; rng.dispatchEvent(new Event('input')); }
      });
    });
  });

  /* ---- Tombol submit: status memuat ---- */
  if (form) {
    form.addEventListener('submit', function () {
      var b = $('#btn-prediksi');
      if (form.checkValidity && !form.checkValidity()) return;
      b.disabled = true;
      b.innerHTML = '<span class="spin"></span><span>Menghitung...</span>';
    });
  }

  /* ---- Hasil: gulir di layar kecil + konfeti untuk predikat A ---- */
  var hasil = $('#hasil');
  function konfeti() {
    if (reduce) return;
    var warna = ['#5b5ef4', '#ff5c8a', '#ffb020', '#12b5a6', '#8b5cf6', '#12b76a'];
    for (var i = 0; i < 60; i++) {
      var c = document.createElement('i');
      c.className = 'konfeti';
      c.style.left = (Math.random() * 100) + 'vw';
      c.style.background = warna[i % warna.length];
      c.style.setProperty('--x', (Math.random() * 240 - 120) + 'px');
      c.style.setProperty('--r', (Math.random() * 900 - 450) + 'deg');
      c.style.setProperty('--t', (2 + Math.random() * 1.8) + 's');
      c.style.animationDelay = (Math.random() * .5) + 's';
      document.body.appendChild(c);
      setTimeout((function (n) { return function () { n.remove(); }; })(c), 4800);
    }
  }
  if (hasil) {
    if (window.matchMedia('(max-width: 899px)').matches) {
      setTimeout(function () { hasil.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'center' }); }, 250);
    }
    var gauge = $('.gauge', hasil);
    if (gauge && gauge.getAttribute('data-grade') === 'A') setTimeout(konfeti, 900);
    if (gauge) gauge.addEventListener('click', function () {
      hasil.classList.remove('go'); void hasil.offsetWidth;
      var ang = $('[data-count]', hasil); if (ang) countUp(ang);
      setTimeout(function () { hasil.classList.add('go'); if (gauge.getAttribute('data-grade') === 'A') konfeti(); }, 40);
    });
  }

  /* ---- Penjelasan AI ---- */
  var aiForm = $('#ai-form');
  function esc(s) { return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); }
  function inline(s) { return esc(s).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/`(.+?)`/g, '<code>$1</code>'); }
  function renderMd(text) {
    var out = [], list = null, lines = text.split(/\r?\n/);
    function close() { if (list) { out.push('</' + list + '>'); list = null; } }
    lines.forEach(function (ln) {
      var t = ln.trim(), m;
      if (!t) { close(); return; }
      if ((m = t.match(/^#{1,4}\s+(.*)/))) { close(); out.push('<h4>' + inline(m[1]) + '</h4>'); }
      else if ((m = t.match(/^[-*•]\s+(.*)/))) { if (list !== 'ul') { close(); out.push('<ul>'); list = 'ul'; } out.push('<li>' + inline(m[1]) + '</li>'); }
      else if ((m = t.match(/^\d+[.)]\s+(.*)/))) { if (list !== 'ol') { close(); out.push('<ol>'); list = 'ol'; } out.push('<li>' + inline(m[1]) + '</li>'); }
      else { close(); out.push('<p>' + inline(t) + '</p>'); }
    });
    close();
    return out.join('');
  }
  function show(box, html, err) {
    box.className = 'ai-hasil' + (err ? ' galat' : '');
    box.innerHTML = '<div class="ai-isi">' + html + '</div>';
    $$('.ai-isi > *', box).forEach(function (el, i) { el.style.setProperty('--i', i); });
  }
  if (aiForm) {
    var tombol = $('#ai-tombol'), kotak = $('#ai-hasil'), label = tombol.innerHTML;
    aiForm.addEventListener('submit', function (e) {
      e.preventDefault();
      tombol.disabled = true;
      tombol.innerHTML = '<span class="spin"></span><span>Sedang meminta penjelasan...</span>';
      kotak.className = 'ai-hasil';
      kotak.innerHTML = '<div class="skeleton" role="status" aria-label="Groq sedang menganalisis"><i></i><i></i><i></i><i></i></div>';
      fetch(aiForm.getAttribute('data-url'), {
        method: 'POST', body: new FormData(aiForm), headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
        .then(function (r) { return r.json().then(function (d) { if (!r.ok) throw new Error(d.galat || 'Permintaan AI gagal.'); return d; }); })
        .then(function (d) { show(kotak, renderMd(d.teks || 'Groq tidak mengembalikan jawaban.')); })
        .catch(function (err) { show(kotak, '<p>' + esc(err.message || 'Tidak bisa menghubungi server.') + '</p>', true); })
        .finally(function () { tombol.disabled = false; tombol.innerHTML = label; });
    });
  }
})();
