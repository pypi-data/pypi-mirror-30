"""Functions to build CouchDB documents from a directory."""

import os
import sys

import simplejson as json

if sys.version_info[0] > 2:
    from pathlib import Path
else:
    from pathlib2 import Path


def _get_file_content(path):
    """Return a file's content (json or text).

    :param pathlib.Path path: The file.
    :rtype: object
    """
    with path.open() as fp:
        if path.suffix == '.json':
            return json.load(fp)
        return fp.read().strip()


def _get_last_doc_ref(path, doc):
    """Mutate a document top-down using a path.

    :param pathlib.Path path: The path.
    :param dict doc: The document.
    :rtype: dict
    """
    for part in path.parts:
        if part not in doc:
            doc[part] = {}
        doc = doc[part]

    return doc


def parse_directory(path):
    """Return a document parsed from a directory.

    :param pathlib.Path path: The directory.
    :rtype: dict
    """
    top = str(path)
    doc = {}

    for (root, dirs, files) in os.walk(top, topdown=False):
        root_path = Path(root)
        obj = {}
        for file in files:
            file_path = root_path.joinpath(file)
            if file_path.name.startswith('.'):
                # Ignore hidden files (.DS_Store etc)
                continue
            content = _get_file_content(file_path)
            obj[file_path.stem] = content
        rel_path = root_path.relative_to(path)
        ref = _get_last_doc_ref(rel_path, doc)
        ref.update(obj)

    return doc


def parse_file(path):
    """Return a document parsed from a file.

    :param pathlib.Path path: The file.
    :rtype: dict
    """
    if path.suffix == '.json':
        with path.open() as fp:
            return json.load(fp)

    return {}


def compile_doc(target):
    """Build CouchDB documents from a directory.

    :param target: The directory.
    :rtype: dict
    """
    docs = {}

    for child in Path(target).iterdir():
        if child.is_dir():
            doc = parse_directory(child)
        if child.is_file():
            doc = parse_file(child)
        if doc != {}:
            # TODO: Raise exception for missing _ids
            docs[doc['_id']] = doc

    return docs
