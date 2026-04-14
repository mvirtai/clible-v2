# Clible Web & CLI Integraatio-opas

Tämä dokumentti kuvaa, miten **Clible v2 CLI** (Python-pohjainen moottori) ja **Clible Web** (TypeScript/React-pohjainen käyttöliittymä) on integroitu toisiinsa hyödyntäen modernia pilviarkkitehtuuria ja kontitusta.

---

## 0. Esivalmistelut (Prerequisites)

Ennen kuin voit rakentaa sovelluksen paikallisesti, varmista että Docker on määritetty hakemaan imaget oikeista rekistereistä:

```bash
gcloud auth configure-docker europe-docker.pkg.dev,europe-north1-docker.pkg.dev
```

---

## 1. Arkkitehtuurin yleiskuva

Integraatio perustuu **"Unified Container" (Yhdistetty kontti)** -malliin. Sen sijaan, että web-sovellus ja CLI olisivat erillisiä palveluita, ne asuvat samassa Docker-kontissa.

- **Frontend (React/Vite):** Tarjoaa modernin käyttöliittymän, hakupalkin, analytiikan visualisoinnin ja viennin.
- **Backend (Express.js):** Toimii "siltana" (Bridge). Se vastaanottaa selaimen pyynnöt ja suorittaa paikallisia `clible`-komentoja `child_process`-moduulin kautta.
- **Engine (Clible-v2 CLI):** Python-sovellus, joka hoitaa FTS5-indeksoinnin, käännösten hallinnan, analytiikan ja varmuuskopioinnin.

---

## 2. Integraation kulmakivet

### A. API-silta (`server.ts`)

Web-palvelin ei koodi Raamattu-logiikkaa uudelleen. Se suorittaa `clible`-komentoja aivan kuin ne kirjoitettaisiin terminaaliin.

**Esimerkki:**
Kun selain kutsuu `/api/clible?cmd=verse&args=John+3:16`, palvelin ajaa:
```
clible verse "John 3:16" --json
```

**Tuetut komennot:**

| Endpoint | CLI-komento |
|---|---|
| `?cmd=verse&args=...` | `clible verse ...` |
| `?cmd=search&args=...` | `clible search ...` |
| `?cmd=analytics&args=...` | `clible analytics reference/chapter/book ...` |
| `?cmd=seed&args=list --json` | `clible seed list --json` |
| `POST /api/ai/insight` | Gemini API (palvelinpuolella) |
| `POST /api/ai/tone` | Gemini API (palvelinpuolella) |

### B. Analytiikkarajapisteiden argumenttien rakentaminen (`bibleService.ts`)

`bibleService.getNativeAnalytics` vastaanottaa aina **täyden jaeviittauksen** (esim. `"John 3:16"`) ja muuntaa sen analysointilaajuuden mukaan oikeaan CLI-muotoon:

| Laajuus | Palautettava argumentti | Esimerkki |
|---|---|---|
| `reference` | Viittaus sellaisenaan | `reference "John 3:16"` |
| `chapter` | Kirja + luku (ilman jae-osaa) | `chapter "John" 3` |
| `book` | Vain kirjan nimi | `book "John"` |

Moniosaisten kirjojen nimet (esim. `"1 Kings 3:5"` → `"1 Kings"`) käsitellään oikein regexillä `/\s+\d.*$/`.

### C. Kerrosarkkitehtuuri

```
types/          ← Datan rakenteet (BibleResponse, TextStats, …)
repositories/   ← HTTP-kutsut /api/*-rajapintaan
services/       ← Liiketoimintalogiikka (AI-kutsujen muodostaminen, analytiikka-args)
components/     ← React-komponentit (AnalyticsView, ReaderView, SearchView, …)
App.tsx         ← Tilan hallinta ja näkymien koordinointi
server.ts       ← Express: API-silta + autentikointi + AI-proxy
```

### D. Kontitus (`Dockerfile`)

1. Pohjana käytetään valmista `clible-v2dev`-imagea Artifact Registrystä.
2. Siihen asennetaan Node.js.
3. Web-sovellus rakennetaan ja käynnistetään samassa ympäristössä, jolloin se löytää `clible`-komennon suoraan PATH-muuttujasta.

---

## 3. Kehitystyön kulku (Workflow)

### CLI-sovelluksen päivitys
1. Tee muutokset Python-koodiin `clible-v2`-repositoriossa.
2. Rakenna ja puske uusi image Artifact Registryyn.
3. Päivitä web-sovelluksen `Dockerfile` viittaamaan uuteen image-tagiin.

### Web-sovelluksen päivitys
1. Muokkaa React-komponentteja tai TypeScript-logiikkaa.
2. Testaa paikallisesti (`npm run dev`; varmista että `clible` on asennettu).
3. Puske muutokset ja avaa PR.

---

## 4. Tärkeät huomiot

- **JSON-ulostulo:** Kaikki `clible`-komennot tukevat `--json`-lippua, jonka silta välittää suoraan selaimelle.
- **Suorituskyky:** CLI ja Web ovat samassa kontissa, joten latenssi on olematon. FTS5-haut ovat yhtä nopeita kuin terminaalissa.
- **Turvallisuus:** `server.ts` sallii vain tietyn komentojoukon — mielivaltainen koodin suoritus on estetty.
- **GEMINI_API_KEY:** Avain annetaan vain palvelimelle ajonaikana (`-e GEMINI_API_KEY=...`); se ei koskaan päädy selaimeen.

---

## 5. Tulevaisuuden laajennukset

- **Laajennetut laajuudet:** Useiden kirjojen analyysi, koko Vanha/Uusi testamentti, koko Raamattu.
- **Concordance-näkymä:** Sanahaku + konteksti suoraan web-käyttöliittymästä.
- **Pilvisynkronointi:** CLI:n GCS-varmuuskopiointiominaisuuksien integrointi web-käyttäjille.

