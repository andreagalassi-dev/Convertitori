import os
import zipfile
import xml.etree.ElementTree as ET
import sys

# Configuration: Extensions to ignore (images, videos, etc.)
IGNORED_EXTENSIONS = {
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.svg', '.webp',
    # Videos
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm',
    # Audio
    '.mp3', '.wav', '.aac', '.ogg',
    # Documents to skip as requested
    '.pdf',
    # Archives/Binaries
    '.zip', '.rar', '.7z', '.tar', '.gz', '.exe', '.dll', '.bin'
}

def is_ignored(filename):
    """Check if the file has an ignored extension."""
    _, ext = os.path.splitext(filename)
    return ext.lower() in IGNORED_EXTENSIONS

def extract_text_from_docx(filepath):
    """Extract text from a .docx file using standard zipfile and xml libraries."""
    try:
        with zipfile.ZipFile(filepath) as docx:
            xml_content = docx.read('word/document.xml')
            tree = ET.fromstring(xml_content)
            
            # Word namespaces
            namespaces = {
                'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
            }
            
            text_parts = []
            # Find all text nodes (<w:t>)
            for node in tree.iter():
                if node.tag.endswith('}t'): # simplified check for w:t
                    if node.text:
                        text_parts.append(node.text)
                elif node.tag.endswith('}p'): # new paragraph
                    text_parts.append('\n')
            
            return "".join(text_parts)
    except Exception as e:
        return f"[ERROR: Could not extract text from .docx: {e}]"

def extract_text_from_odt(filepath):
    """Extract text from an .odt file using standard zipfile and xml libraries."""
    try:
        with zipfile.ZipFile(filepath) as odt:
            xml_content = odt.read('content.xml')
            tree = ET.fromstring(xml_content)
            
            text_parts = []
            # Find all text nodes in ODT
            namespaces = {
                'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'
            }
            
            # This is a basic extraction. ODT structure is complex.
            # We iterate over everything and look for text.
            for elem in tree.iter():
                if elem.text:
                    text_parts.append(elem.text)
                if elem.tail:
                    text_parts.append(elem.tail)
                if elem.tag.endswith('}p'): # Paragraph break
                     text_parts.append('\n')
            
            return "".join(text_parts).strip()
    except Exception as e:
        return f"[ERROR: Could not extract text from .odt: {e}]"

def read_plain_text(filepath):
    """Attempt to read file as plain text with various encodings."""
    encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-16']
    for enc in encodings:
        try:
            with open(filepath, 'r', encoding=enc) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return "[ERROR: Could not decode file as text]"

def convert_file(filepath, output_dir_base, source_root):
    """Convert a single file to .txt and save it preserving relative path structure."""
    filename = os.path.basename(filepath)
    if is_ignored(filename):
        print(f"Skipping ignored file: {filename}")
        return

    print(f"Processing: {filepath}")
    
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    
    content = ""
    if ext == '.docx':
        content = extract_text_from_docx(filepath)
    elif ext == '.odt':
        content = extract_text_from_odt(filepath)
    else:
        # Default to plain text reader for code files (.c, .py, .java etc) and others
        content = read_plain_text(filepath)

    # Determine relative path to maintain structure inside output folder
    # If source_root is /A and file is /A/B/file.txt, rel_path is B/file.txt
    try:
        rel_path = os.path.relpath(filepath, source_root)
    except ValueError:
        # Fallback if paths match exactly or issues occur
        rel_path = filename

    # Calculate output path
    # output_dir_base/rel_path.txt
    # Example: output/subfolder/file.c.txt
    output_path = os.path.join(output_dir_base, rel_path + ".txt")
    
    # Ensure subdirectory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Failed to write output for {filename}: {e}")

def main():
    print("--- File to TXT Converter ---")
    
    # Get source directory
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
    else:
        source_dir = input("Enter the path of the folder to analyze: ").strip()
    
    # Remove quotes if user added them
    source_dir = source_dir.strip('"').strip("'")
    
    if not os.path.isdir(source_dir):
        print(f"Error: The directory '{source_dir}' does not exist.")
        return

    # Create output directory
    output_dir_name = "converted_files_txt"
    output_dir = os.path.join(source_dir, output_dir_name)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    else:
        print(f"Using existing output directory: {output_dir}")

    # Walk through directory
    for root, dirs, files in os.walk(source_dir):
        # Modification to avoid recursing into the output directory itself
        # if it's inside the source directory
        if output_dir_name in dirs:
            dirs.remove(output_dir_name)
            
        for file in files:
            file_path = os.path.join(root, file)
            convert_file(file_path, output_dir, source_dir)

    print("\nconversion completed!")
    print(f"All files have been saved to: {output_dir}")

if __name__ == "__main__":
    main()
