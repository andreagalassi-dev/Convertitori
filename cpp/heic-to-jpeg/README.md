# HEIC to JPEG Converter (C++ / Windows WIC)

Convertitore batch ad alte prestazioni per convertire immagini `.heic` e `.heif` in formato `.jpg` su sistemi Windows, sfruttando nativamente le API **WIC (Windows Imaging Component)** e il decoder di sistema a massima qualità (100%).

## Caratteristiche
- **Prestazioni native**: implementato in C++17 con Windows COM / WIC, senza dipendenze da runtime esterni pesanti.
- **Supporto ricorsivo**: scansiona sottocartelle con `--recursive` o `-r`.
- **Qualità massima**: codifica JPEG con parametro `ImageQuality = 1.0` (senza perdita visibile).

## Requisiti
- **Sistema Operativo**: Windows 10 / 11 a 64 bit.
- **Codec HEIF**: Estensione **"Estensioni immagine HEIF"** (*HEIF Image Extensions*) installata da Microsoft Store (gratuita) o codec HEVC equivalente per consentire a WIC la decodifica.
- **Compilatore**: MSVC (Visual Studio 2019/2022 o Build Tools) con supporto C++17.

## Compilazione

### Metodo 1: MSVC Developer Command Prompt
```cmd
cl /std:c++17 /EHsc /O2 main.cpp windowscodecs.lib ole32.lib OleAut32.lib /Fe:heic_to_jpeg.exe
```

### Metodo 2: CMake
```cmd
cmake -B build
cmake --build build --config Release
```

## Utilizzo
```cmd
heic_to_jpeg.exe <cartella_input> <cartella_output> [--recursive]
```

### Esempi
- Conversione dei soli file nella cartella specificata:
  ```cmd
  heic_to_jpeg.exe "C:\Foto\iPhone" "C:\Foto\JPEG"
  ```

- Conversione ricorsiva includendo tutte le sottocartelle:
  ```cmd
  heic_to_jpeg.exe "C:\Foto\iPhone" "C:\Foto\JPEG" --recursive
  ```

