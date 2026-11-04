import os
import shutil
import subprocess
import tempfile

ALLOWED_EXT = {
    '.png', '.heic', '.heif', '.webp', '.pdf', '.gif', '.tif', '.tiff',
    '.psd', '.svg', '.raw', '.cr2', '.nef', '.arw', '.dng', '.bmp', '.jp2'
}
SKIP_EXT = {'.jpg', '.jpeg'}

MAX_SIZE_BYTES = int(8.9 * 1024 * 1024)
TARGET_SIZE_BYTES = int(8.5 * 1024 * 1024)

def has_imagemagick():
    return shutil.which('magick') is not None

def convert_with_imagemagick(src, dst, quality=95, first_page_only=True):
    # build source for multi-page formats (pdf,tiff): use first page index [0]
    src_arg = src
    _, ext = os.path.splitext(src)
    ext = ext.lower()
    if first_page_only and ext in ('.pdf', '.tif', '.tiff', '.gif'):
        src_arg = f"{src}[0]"
    args = [
        'magick', src_arg,
        '-strip',
        '-sampling-factor', '4:2:0',
        '-interlace', 'Plane',
        '-quality', str(int(quality)),
        dst
    ]
    subprocess.run(args, check=True)

def compress_to_target(src, dst, target_bytes=TARGET_SIZE_BYTES, max_iters=12):
    # binary search on quality to approach target size
    lo, hi = 5, 95
    best_tmp = None
    best_size = None

    for _ in range(max_iters):
        mid = (lo + hi) // 2
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp_path = tmp.name
        try:
            convert_with_imagemagick(src, tmp_path, quality=mid)
        except subprocess.CalledProcessError:
            # conversion failed at this quality; break
            os.remove(tmp_path)
            break

        size = os.path.getsize(tmp_path)
        # store best that is <= target
        if size <= target_bytes:
            # accept and try to increase quality (to get closer to target)
            best_tmp = tmp_path
            best_size = size
            lo = mid + 1
        else:
            # too big -> reduce quality
            hi = mid - 1
            os.remove(tmp_path)

        # if hi < lo stop
        if lo > hi:
            break

    # If we found an acceptable file, move it to dst
    if best_tmp:
        shutil.move(best_tmp, dst)
        return True, best_size
    else:
        # as fallback: try lowest quality once
        try:
            convert_with_imagemagick(src, dst, quality=lo if lo<=95 else 5)
            return True, os.path.getsize(dst)
        except subprocess.CalledProcessError:
            return False, None

def process_file(path):
    root, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext in SKIP_EXT:
        return False, "skipped"

    if ext not in ALLOWED_EXT:
        return False, "unsupported"

    dst = root + '.jpg'
    tmp_initial = None
    try:
        # initial conversion with high quality
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp_initial = tmp.name
        convert_with_imagemagick(path, tmp_initial)

        size = os.path.getsize(tmp_initial)
        if size > MAX_SIZE_BYTES:
            # compress to target size
            ok, final_size = compress_to_target(tmp_initial, dst)
            # remove initial tmp if still exists
            if os.path.exists(tmp_initial):
                os.remove(tmp_initial)
            if not ok:
                return False, "compress_failed"
            return True, final_size
        else:
            # move tmp to final destination
            shutil.move(tmp_initial, dst)
            return True, os.path.getsize(dst)

    except subprocess.CalledProcessError:
        if tmp_initial and os.path.exists(tmp_initial):
            os.remove(tmp_initial)
        return False, "convert_failed"
    except Exception as e:
        if tmp_initial and os.path.exists(tmp_initial):
            os.remove(tmp_initial)
        return False, f"error:{e}"

def walk_and_convert(folder):
    if not has_imagemagick():
        raise EnvironmentError("ImageMagick non trovato. Installare ImageMagick e assicurarsi che 'magick' sia nel PATH.")
    summary = {'converted':0, 'skipped':0, 'errors':0}
    for root, _, files in os.walk(folder):
        for f in files:
            path = os.path.join(root, f)
            ok, info = process_file(path)
            if ok:
                summary['converted'] += 1
                # assicurati che 'info' sia un numero prima di dividere
                size_bytes = info if isinstance(info, (int, float)) else None
                if size_bytes is not None:
                    print(f"OK: {path} -> {size_bytes/1024/1024:.2f} MB")
                else:
                    print(f"OK: {path} -> converted")
            else:
                if info == "skipped":
                    summary['skipped'] += 1
                else:
                    summary['errors'] += 1
                    print(f"ERR: {path} -> {info}")
    return summary

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Uso: python img_to_jpeg.py <cartella_con_immagini>")
        sys.exit(1)
    folder = sys.argv[1]
    if not os.path.isdir(folder):
        print("La cartella specificata non esiste.")
        sys.exit(1)
    print("Avvio conversione in:", folder)
    res = walk_and_convert(folder)
    print("Fatto:", res)
