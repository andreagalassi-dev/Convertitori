// HEIC -> JPEG batch converter (Windows, WIC)
// Usage:
//   main.exe "C:\\input_folder" "C:\\output_folder" [--recursive]
// Requires: Windows HEIF Image Extensions installed (for HEIC decoding).

#include <windows.h>
#include <wincodec.h>
#include <oleauto.h> // VariantInit, VariantClear
#include <wrl/client.h>
#include <filesystem>
#include <string>
#include <iostream>
#include <vector>

#pragma comment(lib, "windowscodecs.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "OleAut32.lib")

using Microsoft::WRL::ComPtr;
namespace fs = std::filesystem;

static bool iequals(const std::wstring& a, const std::wstring& b) {
    if (a.size() != b.size()) return false;
    for (size_t i = 0; i < a.size(); ++i) {
        wchar_t ca = a[i], cb = b[i];
        if (ca >= L'A' && ca <= L'Z') ca = ca - L'A' + L'a';
        if (cb >= L'A' && cb <= L'Z') cb = cb - L'A' + L'a';
        if (ca != cb) return false;
    }
    return true;
}

static void print_hresult(const char* where, HRESULT hr) {
    std::wcerr << L"[ERRORE] " << where << L" hr=0x" << std::hex << hr << std::dec << L"\n";
}

static bool ConvertHeicToJpeg(IWICImagingFactory* factory,
                              const std::wstring& inputPath,
                              const std::wstring& outputPath,
                              float quality = 1.0f) {
    ComPtr<IWICBitmapDecoder> decoder;
    HRESULT hr = factory->CreateDecoderFromFilename(
        inputPath.c_str(), nullptr, GENERIC_READ, WICDecodeMetadataCacheOnDemand, decoder.GetAddressOf());
    if (FAILED(hr)) {
        if (hr == WINCODEC_ERR_COMPONENTNOTFOUND) {
            std::wcerr << L"Decoder HEIC non trovato. Installa 'HEIF Image Extensions' dal Microsoft Store.\n";
        }
        print_hresult("CreateDecoderFromFilename", hr);
        return false;
    }

    ComPtr<IWICBitmapFrameDecode> frame;
    hr = decoder->GetFrame(0, frame.GetAddressOf());
    if (FAILED(hr)) {
        print_hresult("GetFrame", hr);
        return false;
    }

    UINT width = 0, height = 0;
    hr = frame->GetSize(&width, &height);
    if (FAILED(hr) || width == 0 || height == 0) {
        print_hresult("GetSize", hr);
        return false;
    }

    // Convert to a JPEG-friendly format
    ComPtr<IWICFormatConverter> converter;
    hr = factory->CreateFormatConverter(converter.GetAddressOf());
    if (FAILED(hr)) {
        print_hresult("CreateFormatConverter", hr);
        return false;
    }

    hr = converter->Initialize(
        frame.Get(),
        GUID_WICPixelFormat24bppBGR,
        WICBitmapDitherTypeNone,
        nullptr,
        0.0,
        WICBitmapPaletteTypeCustom);
    if (FAILED(hr)) {
        print_hresult("converter->Initialize", hr);
        return false;
    }

    // Prepare output stream
    ComPtr<IWICStream> stream;
    hr = factory->CreateStream(stream.GetAddressOf());
    if (FAILED(hr)) {
        print_hresult("CreateStream", hr);
        return false;
    }
    hr = stream->InitializeFromFilename(outputPath.c_str(), GENERIC_WRITE);
    if (FAILED(hr)) {
        print_hresult("InitializeFromFilename (output)", hr);
        return false;
    }

    // Create JPEG encoder
    ComPtr<IWICBitmapEncoder> encoder;
    hr = factory->CreateEncoder(GUID_ContainerFormatJpeg, nullptr, encoder.GetAddressOf());
    if (FAILED(hr)) {
        print_hresult("CreateEncoder", hr);
        return false;
    }
    hr = encoder->Initialize(stream.Get(), WICBitmapEncoderNoCache);
    if (FAILED(hr)) {
        print_hresult("encoder->Initialize", hr);
        return false;
    }

    ComPtr<IWICBitmapFrameEncode> frameEncode;
    ComPtr<IPropertyBag2> options;
    hr = encoder->CreateNewFrame(frameEncode.GetAddressOf(), options.GetAddressOf());
    if (FAILED(hr)) {
        print_hresult("CreateNewFrame", hr);
        return false;
    }

    // Set JPEG quality to max (1.0)
    if (options) {
        PROPBAG2 prop = {};
        prop.pstrName = const_cast<LPOLESTR>(L"ImageQuality");
        VARIANT var; VariantInit(&var);
        var.vt = VT_R4; // float 0.0 - 1.0
        var.fltVal = (quality > 1.0f) ? 1.0f : (quality < 0.0f ? 0.0f : quality);
        options->Write(1, &prop, &var);
        VariantClear(&var);
    }

    hr = frameEncode->Initialize(options.Get());
    if (FAILED(hr)) {
        print_hresult("frameEncode->Initialize", hr);
        return false;
    }

    hr = frameEncode->SetSize(width, height);
    if (FAILED(hr)) {
        print_hresult("frameEncode->SetSize", hr);
        return false;
    }

    WICPixelFormatGUID pf = GUID_WICPixelFormat24bppBGR;
    hr = frameEncode->SetPixelFormat(&pf);
    if (FAILED(hr)) {
        print_hresult("frameEncode->SetPixelFormat", hr);
        return false;
    }

    // Write converted pixels
    hr = frameEncode->WriteSource(converter.Get(), nullptr);
    if (FAILED(hr)) {
        print_hresult("frameEncode->WriteSource", hr);
        return false;
    }

    hr = frameEncode->Commit();
    if (FAILED(hr)) {
        print_hresult("frameEncode->Commit", hr);
        return false;
    }
    hr = encoder->Commit();
    if (FAILED(hr)) {
        print_hresult("encoder->Commit", hr);
        return false;
    }

    return true;
}

int wmain(int argc, wchar_t* argv[]) {
    std::wcout << L"Convertitore HEIC -> JPEG (qualità massima)\n";
    std::wcout << L"Uso: main.exe <cartella_input> <cartella_output> [--recursive]\n\n";

    fs::path inDir;
    fs::path outDir;

    if (argc < 3) {
        std::wcerr << L"Errore: specificare sia la cartella di input che quella di output.\n";
        std::wcerr << L"Esempio: main.exe \"C:\\cartella_input\" \"C:\\cartella_output\" [--recursive]\n";
        return 1;
    }
    inDir = argv[1];
    outDir = argv[2];
    bool recursive = false;
    if (argc >= 4 && (iequals(argv[3], L"--recursive") || iequals(argv[3], L"-r"))) {
        recursive = true;
    }

    if (!fs::exists(inDir) || !fs::is_directory(inDir)) {
        std::wcerr << L"La cartella di input non esiste o non è una cartella: " << inDir.wstring() << L"\n";
        return 1;
    }
    std::error_code ec;
    fs::create_directories(outDir, ec);
    if (ec) {
        std::wcerr << L"Impossibile creare la cartella di output: " << outDir.wstring() << L"\n";
        return 1;
    }

    HRESULT hr = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    if (FAILED(hr)) {
        print_hresult("CoInitializeEx", hr);
        return 1;
    }

    ComPtr<IWICImagingFactory> factory;
    hr = CoCreateInstance(CLSID_WICImagingFactory, nullptr, CLSCTX_INPROC_SERVER,
                          IID_PPV_ARGS(factory.GetAddressOf()));
    if (FAILED(hr)) {
        print_hresult("CoCreateInstance(WICImagingFactory)", hr);
        CoUninitialize();
        return 1;
    }

    size_t converted = 0, failed = 0, skipped = 0;

    auto process_entry = [&](const fs::directory_entry& e) {
        if (!e.is_regular_file()) { skipped++; return; }
        const fs::path& p = e.path();
        const std::wstring ext = p.extension().wstring();
        if (!(iequals(ext, L".heic") || iequals(ext, L".heif"))) { skipped++; return; }

        fs::path outPath = outDir / p.filename().replace_extension(L".jpg");
        std::wcout << L"Converto: " << p.wstring() << L" -> " << outPath.wstring() << L"\n";
        if (ConvertHeicToJpeg(factory.Get(), p.wstring(), outPath.wstring(), 1.0f)) {
            converted++;
        } else {
            failed++;
        }
    };

    try {
        if (recursive) {
            for (auto& e : fs::recursive_directory_iterator(inDir)) process_entry(e);
        } else {
            for (auto& e : fs::directory_iterator(inDir)) process_entry(e);
        }
    } catch (const std::exception& ex) {
        std::wcerr << L"Errore durante la scansione cartella: " << ex.what() << L"\n";
        CoUninitialize();
        return 1;
    }

    std::wcout << L"\nCompletato. Convertite: " << converted
               << L", Fallite: " << failed
               << L", Ignorate: " << skipped << L"\n";

    CoUninitialize();
    return failed == 0 ? 0 : 2;
}
