# File Converters & Utilities (Convertitori)

Una raccolta di utility leggere, script e strumenti mirati per la conversione di formati di file (documenti, immagini, pubblicazioni digitali). 

Nato come serie di esperimenti pratici e script di automazione (2023–2024), questo repository è organizzato in modo modulare per consentire l'aggiunta rapida di nuovi convertitori in qualsiasi linguaggio.

---

## Indice dei Convertitori

| Convertitore | Linguaggio | Descrizione |
|---|---|---|
| [**file-to-txt**](python/file-to-txt/) | Python | Estrae testo da documenti `.docx`, `.odt` e file di codice/testo con fallback di codifica, preservando l'albero delle cartelle. Zero dipendenze esterne. |
| [**img-to-jpeg**](python/img-to-jpeg/) | Python + ImageMagick | Converte decine di formati di immagini in `.jpg`, applicando una ricerca binaria sul fattore qualità per rimanere sotto un limite target (~8.5 MB). |
| [**indesign-to-pdf**](python/indesign-to-pdf/) | Python + Playwright / Chromium | Scarica e converte pubblicazioni digitali Adobe InDesign (*Publish Online*) in un unico documento PDF ad alta fedeltà. |
| [**heic-to-jpeg**](cpp/heic-to-jpeg/) | C++17 (Windows WIC) | Convertitore batch ad alte prestazioni per decodificare file `.heic`/`.heif` di iPhone in JPEG sfruttando le API native Microsoft WIC. |

---

## Struttura del Repository

```text
.
├── LICENSE
├── README.md
├── .gitignore
├── cpp/
│   └── heic-to-jpeg/
│       ├── CMakeLists.txt
│       ├── README.md
│       └── main.cpp
└── python/
    ├── file-to-txt/
    │   ├── README.md
    │   ├── requirements.txt
    │   └── text_converter.py
    ├── img-to-jpeg/
    │   ├── README.md
    │   ├── requirements.txt
    │   └── img_to_jpeg.py
    └── indesign-to-pdf/
        ├── README.md
        ├── requirements.txt
        └── indesign_to_pdf.py
```

---

## Come Utilizzare i Convertitori

Ciascun convertitore è isolato e indipendente. Fai riferimento al file `README.md` presente nella rispettiva cartella per istruzioni dettagliate su installazione e opzioni di riga di comando:

- [Guida per `file-to-txt`](python/file-to-txt/README.md)
- [Guida per `img-to-jpeg`](python/img-to-jpeg/README.md)
- [Guida per `indesign-to-pdf`](python/indesign-to-pdf/README.md)
- [Guida per `heic-to-jpeg`](cpp/heic-to-jpeg/README.md)

---

## Come Aggiungere Nuovi Convertitori

Il repository è strutturato per linguaggio (`python/`, `cpp/`, o future cartelle come `go/`, `rust/`, ecc.):

1. Crea una cartella con il nome del nuovo convertitore (es. `python/pdf-to-images/` o `rust/audio-converter/`).
2. Includi il codice sorgente del tool.
3. Aggiungi il file delle dipendenze (es. `requirements.txt` o `Cargo.toml`).
4. Aggiungi un `README.md` dedicato con:
   - Descrizione del funzionamento
   - Prerequisiti
   - Esempi di utilizzo CLI
5. Aggiorna la tabella dell'indice in questo `README.md`.

---

## Licenza

Distribuito sotto licenza [MIT](LICENSE). Libero per uso personale e commerciale.

