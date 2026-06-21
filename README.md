# FGSMH Metrix-Laskuri 🏆

Automaattinen pistelaskuri **Frisbeegolfseura Mulligan Hooligans ry**:n viikkokisoihin. Ohjelma hakee tiedot suoraan Discgolf Metrixin rajapinnasta ja laskee sarjapisteet seuran sääntöjen mukaan.

Tuomas Virtanen 2026-03-27

## Pistelaskusäännöt

Ohjelma tukee kahta rinnakkaista pistelaskujärjestelmää. Lopullisissa tulostaulukoissa huomioidaan molemmat mallit omilla sarakkeillaan.

### Vanha pistelaskumalli
* **Sijoituspisteet:** Lasketaan kaavalla `Osallistujat - Sija`.
* **Tasatulokset:** Jaetut sijat saavat molemmat parhaan sijoituksen mukaiset pisteet (esim. jaetulla 2. sijalla molemmat saavat 2. sijan pisteet).
* **8 Parasta:** Lopulliseen pistepottiin huomioidaan vain pelaajan 8 parasta sijoituspistesuoritusta kauden ajalta.
* **Osallistumisbonus:** Jokaisesta pelatusta kierroksesta saa +1 pisteen, joka lisätään suoraan loppusummaan.

### Uusi pistelaskumalli (101-1)
* **Sijoituspisteet:** Lasketaan prosentuaalisella kaavalla per osakilpailu:
  $$ROUND\left(\frac{100 \times (N - \text{Rank} + 1)}{N} + 1\right)$$
  *Missä $N$ on osakilpailun osallistujamäärä ja $\text{Rank}$ on pelaajan sijoitus.*
* **Tasatulokset:** Jaetut sijat saavat parhaan sijoituksen mukaiset pisteet (vastaava sijoituslogiikka kuin vanhassa mallissa).
* **8 Parasta:** Lopulliseen pistepottiin huomioidaan vain pelaajan 8 parasta osakilpailusuoritusta.
* **Osallistumisbonus:** Jokaisesta pelatusta kierroksesta saa +1 pisteen, joka lisätään suoraan loppusummaan.

## Käyttöönotto
Varmista, että koneellasi on [uv](https://docs.astral.sh/uv/) asennettuna.

```bash
# Kloonaa repo
git clone git@github.com:tuomastvirtanen/fgsmh_metrix.git
cd fgsmh_metrix

# Aja ohjelma (uv asentaa riippuvuudet automaattisesti)
uv run metrix_laskuri.py
```