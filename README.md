# Paper Library 3.0

Pacchetto Python per scaricare paper da DOI, costruire una biblioteca locale SQLite e ricercarla da terminale.

## Funzionalità

- DOI singolo o lista TXT
- metadati da Scopus/Elsevier, Crossref, Unpaywall, OpenAlex e Semantic Scholar
- download Elsevier quando autorizzato e fallback Open Access
- nomi file `2024 - TRC - Perboli - Titolo.pdf`
- cartelle PDF per anno
- deduplicazione per DOI
- database SQLite e ricerca testuale
- download parallelo
- export CSV, BibTeX e RIS
- ricerca semantica TF-IDF opzionale
- GitHub Actions e test

## Installazione

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e .
cp .env.example .env
```

Compila `.env` senza committare le chiavi.

## Comandi

```bash
paper download --doi "10.1016/j.trc.2024.104567"
paper download --file examples/doi.txt --workers 4
paper search "digital twin"
paper search --author Perboli --journal TRC --year 2024
paper stats
paper export --format csv
paper export --format bibtex
paper export --format ris
```

Ricerca semantica:

```bash
pip install -e '.[semantic]'
paper semantic-search "urban logistics digital twins"
```

## Nota legale

Il pacchetto scarica soltanto contenuti restituiti dalle API autorizzate o indicati come Open Access. L'accesso al full text Elsevier dipende dai diritti della chiave e dell'istituzione.
