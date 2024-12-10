__all__ = ["extract_words"]
__version__ = "1.0.0"
__author__ = "Eggie"


from typing import BinaryIO
from pathlib import Path


def _blocks(file: BinaryIO, size: int = 65536):
    """
    Reads a file in chunks and yields blocks of data.

    :param file: The file to read from, which must be opened in binary mode.
    :param size: The size of each block to read, in bytes. Defaults to 65,536
        bytes (64 KB).

    :yield: A block of data from the file.
    """
    while True:
        block = file.read(size)
        if not block:
            break
        yield block


def extract_words(filepath: str | Path) -> set[str]:
    """
    Extracts unique words from a file and returns them as a set.

    This function reads the contents of a file specified by ``filepath`` in
    binary mode, processes it in chunks, and extracts individual words
    separated by newlines. It returns a set of words to ensure that there are
    no duplicate words.

    :param filepath: The path to a file containing words delimited by a
        newline.

    :return: A set of unique words found in the file.
    """
    lexicon = set()

    with open(filepath, "rb") as file:
        buffer = b""
        for block in _blocks(file):
            lines = (buffer + block).split(b'\n')
            for line in lines[:-1]:
                word = line.strip().decode("utf-8")
                lexicon.add(word)
            buffer = lines[-1]

    if buffer:
        word = buffer.strip().decode("utf-8")
        lexicon.add(word)

    return lexicon
