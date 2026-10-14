# Margell D-K · reglament de règim interior

Web de la Comunitat de Propietaris Margell D-K (Calella de Palafrugell), publicada a <https://margelldk.github.io>.

## Estructura

- `index.html`: portada amb el selector de llengües.
- `ca/`, `es/`, `en/`, `fr/`, `de/`, `nl/`, `it/`, `ru/`: el reglament en cada llengua. Són les adreces on porten els codis QR del cartell.
- `assets/`: full d'estil, banderes i logotips de l'administració.

## Com s'actualitza

Les pàgines es generen automàticament. No s'han d'editar a mà.

1. Edita els textos a `eines/textos.py` (carpeta `Margell`, fora d'aquest repositori).
2. Executa `python eines/genera.py` des de la carpeta `Margell`.
3. Publica els canvis: `git add -A`, `git commit -m "..."` i `git push`.

Les adreces de les pàgines no han de canviar mai, perquè els codis QR del cartell imprès hi apunten.
