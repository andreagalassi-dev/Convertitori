# Image to JPEG Converter (Python + ImageMagick)

Script batch per convertire immagini di quasi qualsiasi formato in `.jpg`, con algoritmo di compressione automatica mirata (ricerca binaria sul fattore qualità) per non superare il limite di peso di ~8.5 MB.

## Caratteristiche
- **Ampio supporto formati**: converte `.png`, `.heic`, `.heif`, `.webp`, `.pdf` (prima pagina), `.gif`, `.tif`/`.tiff`, `.psd`, `.svg`, `.raw`, `.cr2`, `.nef`, `.arw`, `.dng`, `.bmp`, `.jp2`.
- **Compressione intelligente al target**: se l'immagine convertita supera 8.9 MB, esegue una ricerca binaria sul parametro di qualità JPEG (5-95) per massimizzare la resa visiva rimanendo entro 8.5 MB (ideale per upload con vincoli rigidi di dimensione).
- **Elaborazione ricorsiva**: analizza ricorsivamente l'intera struttura di cartelle passata come argomento.
- **Salta file già convertiti**: ignora file `.jpg` e `.jpeg` già presenti per evitare riconversioni inutili.

## Prerequisiti
1. **Python 3.8+**
2. **ImageMagick 7+** con il comando `magick` registrato nel PATH:
   - **macOS**: `brew install imagemagick`
   - **Ubuntu/Debian**: `sudo apt install imagemagick`
   - **Windows**: scaricare l'installer da [imagemagick.org](https://imagemagick.org/) abilitando l'opzione *"Add application directory to your system path"*.

## Utilizzo
```bash
python img_to_jpeg.py /percorso/della/cartella_con_immagini
```

Il file originale non viene eliminato; il nuovo file JPEG viene salvato con lo stesso nome e percorso, con estensione `.jpg`.
