import re
from functools import partial

from .exceptions import DocumentDoesNotExist, DocumentImportError

__all__ = ['parse_document']


import_regex = re.compile(r'#\s+from\s+(.*)\s+import\s+(.*)')


def import_definitions(document, match):
    name, definitions = match.groups()
    path = name.lstrip('.')
    dots = len(name) - len(path)
    query_key = document.origin.query_key[:-dots] + path.split('.')

    try:
        imported = document.origin.loader.engine.get_document(query_key)
    except DocumentDoesNotExist:
        msg = 'No document named `{}`'.format(query_key)
        raise DocumentImportError(msg)

    ret = ''
    for identifier in definitions.split(','):
        definition = identifier.strip()
        if definition not in imported.definitions:
            msg = 'Cannot import definition `{}`'.format(definition)
            raise DocumentImportError(msg)
        ret += imported.definitions[definition]
    return ret


def parse_document(document):
    header = document.source.body[:document.ast.loc.start]
    source = import_regex.sub(partial(import_definitions, document), header)
    source += document.source.body[document.ast.loc.start:]
    return source
