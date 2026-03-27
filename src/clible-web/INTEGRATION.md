# Clible Web & CLI Integraatio-opas

Tämä dokumentti kuvaa, miten **Clible v2 CLI** (Python-pohjainen moottori) ja **Clible Web** (TypeScript/React-pohjainen käyttöliittymä) on integroitu toisiinsa hyödyntäen modernia pilviarkkitehtuuria ja kontitusta.

---

## 0. Esivalmistelut (Prerequisites)

Ennen kuin voit rakentaa sovelluksen paikallisesti, varmista että Docker on määritetty hakemaan imaget oikeista rekistereistä. Käytä tätä komentoa välttääksesi turhat konfiguraatiot:

```bash
gcloud auth configure-docker europe-docker.pkg.dev,europe-north1-docker.pkg.dev
```

---

## 1. Arkkitehtuurin yleiskuva

Integraatio perustuu **"Unified Container" (Yhdistetty kontti)** -malliin. Sen sijaan, että web-sovellus ja CLI-sovellus olisivat erillisiä palveluita, ne asuvat samassa Docker-kontissa.

- **Frontend (React/Vite):** Tarjoaa modernin käyttöliittymän, hakupalkin ja analytiikan visualisoinnin.
- **Backend (Express.js):** Toimii "siltana" (Bridge). Se vastaanottaa selaimen pyynnöt ja suorittaa paikallisia `clible`-komentoja.
- **Engine (Clible-v2 CLI):** Alkuperäinen Python-sovelluksesi, joka hoitaa FST5-indeksoinnin, 1000+ käännöksen hallinnan ja natiivin analytiikan.

---

## 2. Integraation kulmakivet

### A. API-silta (`server.ts`)
Web-palvelin ei yritä koodata Raamattu-logiikkaa uudelleen. Se käyttää Node.js:n `child_process`-moduulia suorittaakseen `clible`-komentoja aivan kuin ne kirjoitettaisiin terminaaliin.

**Esimerkki:**
Kun selain kutsuu `/api/clible?cmd=verse&args=John+3:16`, palvelin ajaa:
`clible verse "John 3:16" --json`

Tämä varmistaa, että kaikki CLI-sovelluksesi ominaisuudet (kuten FST5-haku) ovat heti käytettävissä webissä ilman koodin monistamista.

### B. Kerrosarkkitehtuuri (Separation of Concerns)
Web-sovellus on jaettu selkeisiin kerroksiin:
1. **Domain/Types (`src/types/`):** Määrittelee datan rakenteen (Verse, Stats, jne.).
2. **Repository (`src/repositories/`):** Hoitaa tiedonhakun. Se kutsuu paikallista API-siltaa.
3. **Service (`src/services/`):** Sisältää liiketoimintalogiikan, kuten AI-integraation (Gemini) ja natiivin analytiikan kutsumisen.
4. **UI (`src/App.tsx`):** Vastaa vain tiedon esittämisestä ja käyttäjän interaktiosta.

### C. Kontitus (`Dockerfile`)
Käytämme **Multi-stage build** -ideologiaa, mutta yhdistämme ajonaikaiset ympäristöt:
1. Pohjana käytetään valmista `clible-v2dev` -imagea Artifact Registrystä.
2. Siihen asennetaan Node.js.
3. Web-sovellus rakennetaan ja käynnistetään samassa ympäristössä, jolloin se löytää `clible`-komennon suoraan PATH-muuttujasta.

---

## 3. Kehitystyön kulku (Workflow)

### CLI-sovelluksen päivitys:
1. Tee muutokset Python-koodiin `clible-v2` -repositoriossa.
2. Rakenna ja puske uusi image Artifact Registryyn (kuten olet jo tehnyt).
3. Päivitä web-sovelluksen `Dockerfile` viittaamaan uuteen image-tagiin tai SHA-tunnisteeseen.

### Web-sovelluksen päivitys:
1. Muokkaa React-komponentteja tai TypeScript-logiikkaa.
2. Testaa paikallisesti (varmista, että `clible` on asennettu kehityskoneellesi).
3. Julkaise uusi versio Cloud Run -palveluun.

---

## 4. Tärkeät huomiot

- **JSON-ulostulo:** Jotta integraatio toimii saumattomasti, varmista että `clible`-komennot tukevat `--json` -lippua ja palauttavat validia JSON-dataa.
- **Suorituskyky:** Koska CLI ja Web ovat samassa kontissa, latenssi on olematon. FST5-haut ovat yhtä nopeita kuin terminaalissa.
- **Turvallisuus:** `server.ts` on suunniteltu niin, että se sallii vain tietyt komennot, mikä estää mielivaltaisen koodin suorittamisen palvelimella.

---

## 5. Tulevaisuuden laajennukset

- **Vienti (Export):** Voit lisätä painikkeen, joka kutsuu `clible export` -komentoa ja palauttaa tiedoston suoraan selaimelle.
- **Käännösten asennus:** Voit luoda käyttöliittymän, joka kutsuu `clible seed` -komentoa uusien käännösten lataamiseksi.
- **Synkronointi:** Hyödynnä CLI:n valmiita pilvisynkronointiominaisuuksia web-käyttäjän asetusten tallentamiseen.
