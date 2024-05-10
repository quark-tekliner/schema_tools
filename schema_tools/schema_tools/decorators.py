from schema_tools.decorator_types import FieldDefinition, TypeDefinition


def _format_doc_string(s):
    if s is None:
        return
    return '\\n'.join([p.strip() for p in s.strip().split('\n')])


def t(*tags: TypeDefinition):
    def w1(c):
        c._tags = tags
        return c
    return w1


def f(*tags: FieldDefinition | str):
    doc = ''
    actual_tags = []
    for tag in tags:
        if tag is str:
            doc = _format_doc_string(tag)
        else:
            actual_tags.append(tag)
    ret = type('Field', (), dict(_tags=actual_tags, __doc__=doc))
    return ret
