import gzip
import io
import os


extension_to_compressor = {
    'gz': gzip.GzipFile,
}


magic_bytes_to_extension = {
    b'\037\213': 'gz'
}


def file_name_has_compression(path):
    parts = os.path.splitext(path)
    if len(parts) == 1:
        return None
    else:
        ext = parts[1]
    if ext.startswith('.'):
        ext = ext[1:]
    return extension_to_compressor.get(ext, None)


def bytes_have_compression_magic(bytestring):
    for magic, extension in magic_bytes_to_extension.items():
        if bytestring.startswith(magic):
            return extension
