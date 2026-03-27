# FGSMH Metrix-Laskuri 🏆

Automaattinen pistelaskuri **Frisbeegolfseura Mulligan Hooligans ry**:n viikkokisoihin. Ohjelma hakee tiedot suoraan Discgolf Metrixin rajapinnasta ja laskee sarjapisteet seuran sääntöjen mukaan.

Tuomas Virtanen 2026-03-27

## Pistelaskusäännöt
1. **Sijoituspisteet**: Lasketaan kaavalla `(Osallistujat - Sija)`.
2. **Tasatulokset**: Jaetut sijat saavat molemmat parhaan sijoituksen mukaiset pisteet.
3. **8 Parasta**: Lopulliseen summaan huomioidaan vain pelaajan 8 parasta sijoituspistesuoritusta.
4. **Osallistumisbonus**: Jokaisesta pelatusta kierroksesta saa +1 pisteen, joka lisätään loppusummaan.

## Käyttöönotto
Varmista, että koneellasi on [uv](https://docs.astral.sh/uv/) asennettuna.

```bash
# Kloonaa repo
git clone git@github.com:tuomastvirtanen/fgsmh_metrix.git
cd fgsmh_metrix

# Aja ohjelma (uv asentaa riippuvuudet automaattisesti)
uv run metrix_laskuri.py
```