# Adobe InDesign Online to PDF Downloader (Python)

Tool per scaricare e convertire cataloghi, riviste o documenti pubblicati tramite **Adobe InDesign Publish Online** (`indd.adobe.com`) in un documento PDF completo ad alta fedeltà.

## Come funziona
1. Interroga l'API pubblica Adobe (`indd.adobe.com/api/v1/getManifestdata`) per ottenere l'elenco delle pagine e le relative dimensioni in pixel.
2. Renderizza ciascuna pagina HTML tramite browser headless (**Playwright** o **Google Chrome/Edge**) mantenendo le proporzioni esatte.
3. Unisce opzionalmente tutte le pagine scaricate in un unico file PDF finale tramite `PyPDF2`.

## Requisiti

### Installazione dipendenze Python
```bash
pip install -r requirements.txt
```

Se si desidera utilizzare il motore Playwright (consigliato per la massima precisione dei layout):
```bash
playwright install chromium
```

In alternativa, se si preferisce usare il browser già installato sul sistema (Google Chrome o Microsoft Edge), è possibile passare il parametro `--renderer chrome`.

## Utilizzo

Dato un link di pubblicazione Adobe come:
`https://indd.adobe.com/view/9fffdfc4-55ed-43b2-93cd-4bcf5f53a412`

L'ID della pubblicazione è l'ultima parte dell'URL: `9fffdfc4-55ed-43b2-93cd-4bcf5f53a412`.

### Esempio rapido (Playwright)
```bash
python indesign_to_pdf.py --pub-id 9fffdfc4-55ed-43b2-93cd-4bcf5f53a412
```

### Esempio con Chrome headless di sistema
```bash
python indesign_to_pdf.py --pub-id 9fffdfc4-55ed-43b2-93cd-4bcf5f53a412 --renderer chrome
```

### Parametri opzionali
| Parametro | Descrizione | Default |
|---|---|---|
| `--pub-id` | **(Obbligatorio)** ID alfanumerico della pubblicazione | - |
| `--renderer` | Motore di rendering (`playwright` o `chrome`) | `playwright` |
| `--browser-path` | Percorso personalizzato dell'eseguibile Chrome/Edge | Ricerca automatica |
| `--output-dir` | Cartella in cui salvare i PDF delle singole pagine | `output_pages` |
| `--merged-pdf` | Nome del file PDF finale combinato | `catalogo.pdf` |
| `--no-merge` | Salva solo le singole pagine senza generare il PDF unito | `False` |
| `--max-pages` | Limita il numero massimo di pagine da scaricare (utile per test) | Tutte |
| `--start-page` | Indice di pagina iniziale da cui partire (0 = prima pagina) | `0` |
| `--timeout` | Timeout in millisecondi per il caricamento di ciascuna pagina | `15000` |
