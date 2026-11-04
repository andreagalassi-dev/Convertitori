# File to TXT Converter (Python)

Script Python autonomo per l'estrazione e la conversione massiva di file di testo e documenti (`.docx`, `.odt`, codice sorgente, file di testo puro con varie codifiche) in file di testo `.txt`, preservando la struttura delle cartelle di origine.

## Caratteristiche
- **Zero dipendenze esterne**: utilizza esclusivamente la libreria standard di Python (`zipfile`, `xml.etree.ElementTree`, `os`).
- **Supporto formati Office**: estrae il testo direttamente da documenti Word (`.docx`) e OpenDocument (`.odt`) analizzandone l'XML interno.
- **Rilevamento intelligente della codifica**: fallback sequenziale per file di testo (`utf-8`, `latin-1`, `cp1252`, `utf-16`).
- **Filtro automatico dei file**: salta file binari, multimediali (immagini, video, audio) e archivi.
- **Mantenimento della gerarchia**: ricrea la stessa struttura di sottocartelle all'interno della directory di destinazione `converted_files_txt`.

## Requisiti
- Python 3.8 o superiore (nessun pacchetto pip richiesto).

## Utilizzo

### Tramite argomento riga di comando
```bash
python text_converter.py /percorso/della/cartella
```

### In modalità interattiva
Se avviato senza argomenti, lo script richiederà il percorso da terminale:
```bash
python text_converter.py
```

I file convertiti verranno salvati all'interno della cartella di origine nella sottodirectory `converted_files_txt/`.
