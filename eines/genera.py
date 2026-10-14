# Genera la web margelldk.github.io i el cartell DIN A3 (HTML i PDF) a partir de textos.py.
# Ús: python eines/genera.py   (des de l'arrel del repositori)

import html
import io
import re
import shutil
import subprocess
from pathlib import Path

import qrcode
import qrcode.image.svg

from textos import ICONES, ICONES_RESUM, ORDRE, T

ARREL = Path(__file__).resolve().parent.parent
WEB = ARREL
PDF = ARREL / "cartell" / "Cartell_Margell_DK_A3.pdf"
NAVEGADORS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "chromium", "chrome", "msedge",
]
DOMINI = "https://margelldk.github.io"

FONTS = ("https://fonts.googleapis.com/css2?family=Montserrat:wght@600;700;800"
         "&family=Source+Sans+3:ital,wght@0,400;0,600;0,700;1,400&display=swap")
NOMS_ICONES = sorted(set(ICONES + ICONES_RESUM + [
    "print", "call", "mail", "language", "location_on", "emergency", "volume_off",
    "electric_scooter", "no_food", "shower", "translate", "arrow_forward", "schedule", "download",
]))
ICONS_URL = ("https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:"
             "opsz,wght,FILL,GRAD@20..48,500,0..1,0&icon_names=" + ",".join(NOMS_ICONES))

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
           "%3Crect width='64' height='64' rx='14' fill='%230f2f57'/%3E"
           "%3Cpath d='M10 40c6-5 12-5 18 0s12 5 18 0 8-4 8-4v14H10z' fill='%2363b3ed'/%3E"
           "%3Ctext x='32' y='33' font-family='Arial' font-weight='700' font-size='20' "
           "fill='%23fff' text-anchor='middle'%3EDK%3C/text%3E%3C/svg%3E")


def tipografia(text, llengua):
    """Polit tipogràfic segons la llengua."""
    if llengua in ("ca", "fr", "it", "en", "nl", "es"):
        text = text.replace("'", "’")
    text = re.sub(r"(\d) €", "\\1\u00a0€", text)
    text = re.sub(r"€ (\d)", "€\u00a0\\1", text)
    text = re.sub(r"(\d) (h|uur|Uhr)\b", "\\1\u00a0\\2", text)
    text = re.sub(r"(\d) (am|pm)\b", "\\1\u00a0\\2", text)
    if llengua == "fr":
        text = re.sub(r" ([:;!?])", "\u202f\\1", text)
        text = re.sub(r"(\d) h (\d)", "\\1\u00a0h\u00a0\\2", text)
    if llengua == "ru":
        text = text.replace("т. п.", "т.\u00a0п.")
    return text


def e(text, llengua):
    return html.escape(tipografia(text, llengua), quote=False)


def icona(nom, classe="ic"):
    return f'<span class="{classe}" aria-hidden="true">{nom}</span>'


def qr_svg(url):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0, box_size=10)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
    buf = io.BytesIO()
    img.save(buf)
    svg = buf.getvalue().decode("utf-8")
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg).strip()
    svg = re.sub(r'width="[^"]*mm" height="[^"]*mm" ', "", svg)
    return svg.replace('fill="#000000"', 'fill="#0f2f57"')


# ------------------------------------------------------------------ web

CAP_COMU = """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titol}</title>
<meta name="description" content="{descripcio}">
<meta name="theme-color" content="#0f2f57">
<link rel="icon" href="{favicon}">
{alternates}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{fonts}">
<link rel="stylesheet" href="{icons}">
<link rel="stylesheet" href="{base}assets/estil.css">
</head>
"""


def alternates():
    linies = [f'<link rel="alternate" hreflang="{k}" href="{DOMINI}/{k}/">' for k in ORDRE]
    linies.append(f'<link rel="alternate" hreflang="x-default" href="{DOMINI}/">')
    return "\n".join(linies)


def logos(base):
    return f"""<div class="logos">
  <img src="{base}assets/img/giscom.jpg" alt="GiScom Real Estate" class="logo-giscom">
  <img src="{base}assets/img/api.jpg" alt="Registre d’Agents Immobiliaris de Catalunya · API" class="logo-api">
  <img src="{base}assets/img/finques.jpg" alt="Administrador de Finques Col·legiat" class="logo-finques">
</div>"""


def selector(actual, base):
    items = []
    for k in ORDRE:
        cur = ' aria-current="page"' if k == actual else ""
        items.append(f'<a href="{base}{k}/" hreflang="{k}" lang="{k}"{cur}>'
                     f'<img src="{base}assets/flags/{k}.svg" alt="" width="24" height="16">'
                     f'<span>{T[k]["nom"]}</span></a>')
    return "\n    ".join(items)


def peu(k, base):
    t = T[k]
    return f"""<footer class="peu">
  <div class="peu-in">
    <div>
      <p class="peu-titol">{e(t["admin"], k)}</p>
      <p><strong>DR GiScom S.L.</strong><br>
      {icona("location_on", "ic sm")} C/ Cavallers, 21 · 17200 Palafrugell</p>
    </div>
    <ul class="contacte">
      <li>{icona("call", "ic sm")} <a href="tel:+34972611023">972 611 023</a></li>
      <li>{icona("emergency", "ic sm")} {e(t["urgencies"], k)}: <a href="tel:+34677762644">677 762 644</a></li>
      <li>{icona("mail", "ic sm")} <a href="mailto:info@giscom.cat">info@giscom.cat</a></li>
      <li>{icona("language", "ic sm")} <a href="https://www.giscom.cat" rel="noopener">www.giscom.cat</a></li>
    </ul>
  </div>
  <p class="peu-final">Comunitat de Propietaris Margell D-K · Calella de Palafrugell</p>
</footer>"""


def pagina_llengua(k):
    t = T[k]
    base = "../"
    resum = "\n".join(
        f'<li>{icona(ic)}<span class="r-et">{e(et, k)}</span><span class="r-val">{e(val, k)}</span></li>'
        for ic, (et, val) in zip(ICONES_RESUM, t["resum"]))
    arts = "\n".join(
        f'''<li class="art" id="article-{i}">
  <div class="art-num" aria-hidden="true"><span>{i}</span></div>
  <div class="art-cos">
    <h3>{icona(ICONES[i - 1], "ic art-ic")}<span class="art-et">{e(t["article"], k)} {i}</span> {e(t["titols"][i - 1], k)}</h3>
    <p>{e(t["articles"][i - 1], k)}</p>
  </div>
</li>''' for i in range(1, 22))
    nota = (f'<p class="nota">{icona("translate", "ic sm")} {e(t["nota"], k)}</p>'
            if t["nota"] else "")
    cap = CAP_COMU.format(
        lang=k, titol=f'{e(t["doc"], k)} · Margell D-K',
        descripcio=html.escape(tipografia(t["intro"], k)), favicon=FAVICON,
        alternates=alternates(), fonts=FONTS, icons=ICONS_URL, base=base)
    return cap + f"""<body>
<a class="salta" href="#articles">{e(t["articles_titol"], k)}</a>
<nav class="idiomes" aria-label="{e(t["idioma"], k)}">
  <div class="idiomes-in">
    {selector(k, base)}
  </div>
</nav>
<header class="cap">
  {logos(base)}
</header>
<main>
  <section class="hero">
    <p class="kicker">Margell D-K · Calella de Palafrugell</p>
    <h1>{e(t["doc"], k)}</h1>
    <p class="intro">{e(t["intro"], k)}</p>
    {nota}
    <div class="accions"><button class="imprimeix" type="button" onclick="window.print()">{icona("print", "ic sm")} {e(t["imprimeix"], k)}</button></div>
  </section>
  <section class="resum" aria-labelledby="resum-t">
    <h2 id="resum-t">{e(t["resum_titol"], k)}</h2>
    <ul>
{resum}
    </ul>
  </section>
  <section class="articles" id="articles" aria-labelledby="art-t">
    <h2 id="art-t">{e(t["articles_titol"], k)}</h2>
    <ol>
{arts}
    </ol>
  </section>
</main>
{peu(k, base)}
</body>
</html>
"""


def pagina_inici():
    targetes = "\n".join(
        f'''<li><a href="{k}/" hreflang="{k}" lang="{k}">
  <img src="assets/flags/{k}.svg" alt="" width="66" height="44">
  <span class="t-nom">{T[k]["nom"]}</span>
  <span class="t-doc">{e(T[k]["doc"], k)}</span>
  {icona("arrow_forward", "ic t-fl")}
</a></li>''' for k in ORDRE)
    tria = " · ".join(f'<span lang="{k}">{e(T[k]["tria"], k)}</span>' for k in ORDRE)
    cap = CAP_COMU.format(
        lang="ca", titol="Margell D-K · Reglament de règim interior",
        descripcio="Comunitat de Propietaris Margell D-K (Calella de Palafrugell): reglament de règim interior en vuit llengües.",
        favicon=FAVICON, alternates=alternates(), fonts=FONTS, icons=ICONS_URL, base="")
    return cap + f"""<body class="inici">
<header class="cap">
  {logos("")}
</header>
<main>
  <section class="hero hero-inici">
    <p class="kicker">Calella de Palafrugell</p>
    <h1>Comunitat de Propietaris<br>Margell D-K</h1>
    <p class="tria">{tria}</p>
  </section>
  <ul class="targetes">
{targetes}
  </ul>
  <p class="descarrega"><a href="cartell/Cartell_Margell_DK_A3.pdf" download>{icona("download", "ic sm")} Cartell informatiu · DIN A3 (PDF)</a></p>
</main>
{peu("ca", "")}
</body>
</html>
"""


# ------------------------------------------------------------------ cartell

def esc_qr(text):
    text = text.replace(" QR", "\u00a0QR")
    return re.sub(r"(QR-\w+)", r'<span class="nw">\1</span>', text)


def cartell():
    cols = []
    for k in ORDRE:
        t = T[k]
        url = f"{DOMINI}/{k}/"
        ps = "".join(f"<p>{e(p, k)}</p>" for p in t["cartell"]).replace("Eigent\u00fcmergemeinschaft", "Eigent\u00fcmer\u00adgemeinschaft")
        cols.append(f'''<div class="col" lang="{k}">
  <img class="band" src="../assets/flags/{k}.svg" alt="">
  <h2>{t["nom"]}</h2>
  <div class="txt">{ps}</div>
  <div class="qr">{qr_svg(url)}</div>
  <p class="esc"><span>{esc_qr(e(t["escaneja"], k))}</span></p>
  <p class="url">margelldk.github.io/{k}</p>
  <p class="gr"><strong>{e(t["gracies"][0], k)}</strong><br>{e(t["gracies"][1], k)}</p>
</div>''')
    benvinguda = " · ".join(
        f'<span lang="{k}">{w}</span>' for k, w in [
            ("en", "Welcome"), ("es", "Bienvenidos"), ("fr", "Bienvenue"), ("de", "Willkommen"),
            ("nl", "Welkom"), ("it", "Benvenuti"), ("ru", "Добро пожаловать")])

    def picto(ic, valor, no=False, extra=""):
        cl = {True: "pic no", False: "pic", "x": "pic nx"}[no]
        return (f'<div class="{cl}"><span class="pi">{ic}</span>{extra}'
                + (f'<span class="pv">{valor}</span>' if valor else "") + "</div>")

    return f"""<!doctype html>
<html lang="ca">
<head>
<meta charset="utf-8">
<title>Cartell Margell D-K · DIN A3</title>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{ICONS_URL}">
<link rel="stylesheet" href="cartell.css">
</head>
<body>
<div class="full">
  <header>
    <div class="onada" aria-hidden="true"></div>
    <p class="loc">Calella de Palafrugell</p>
    <h1><span class="b">Benvinguts a la</span>Comunitat de Propietaris Margell D-K</h1>
    <p class="wel">{benvinguda}</p>
  </header>
  <section class="pictos">
    <div class="grup">
      {picto("pool", "10:00 – 22:00")}
      {picto("shower", "")}
      {picto("pets", "", True)}
      {picto("no_food", "", "x")}
    </div>
    <div class="grup">
      {picto("bedtime", "23:00 – 08:00")}
      {picto("volume_off", "", "x")}
      {picto("sports_tennis", "09:00 – 21:30")}
    </div>
    <div class="grup">
      {picto("outdoor_grill", "", True)}
      {picto("checkroom", "", True)}
      {picto("electric_scooter", "", True)}
      {picto("smoke_free", "", "x")}
    </div>
  </section>
  <section class="cols">
    {"".join(cols)}
  </section>
  <footer>
    <span>Reglament de règim interior · margelldk.github.io</span>
  </footer>
</div>
</body>
</html>
"""


def main():
    for k in ORDRE:
        d = WEB / k
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(pagina_llengua(k), encoding="utf-8")
    (WEB / "index.html").write_text(pagina_inici(), encoding="utf-8")
    html_cartell = ARREL / "eines" / "cartell.html"
    html_cartell.write_text(cartell(), encoding="utf-8")
    print("Web generada:", ", ".join(ORDRE))
    genera_pdf(html_cartell)


def genera_pdf(html_cartell):
    """Imprimeix el cartell en PDF amb Chrome o Edge en mode headless."""
    nav = next((n for n in NAVEGADORS if Path(n).exists() or shutil.which(n)), None)
    if not nav:
        print("No s'ha trobat Chrome ni Edge: obre eines/cartell.html i imprimeix-lo en A3 apaïsat.")
        return
    PDF.parent.mkdir(exist_ok=True)
    PDF.unlink(missing_ok=True)
    subprocess.run([nav, "--headless=new", "--disable-gpu", "--virtual-time-budget=10000",
                    "--no-pdf-header-footer", f"--print-to-pdf={PDF}", html_cartell.as_uri()],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    print("PDF generat:" if PDF.exists() else "No s'ha pogut generar el PDF:", PDF.relative_to(ARREL))


if __name__ == "__main__":
    main()
