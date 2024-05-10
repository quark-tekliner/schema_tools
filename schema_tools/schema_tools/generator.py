import pathlib
import inspect
from typing import get_args, get_origin
from types import UnionType, GenericAlias
from cookiecutter.main import cookiecutter
import jinja2
import shutil


from schema_tools.decorators import _format_doc_string


def _create_dir_structure(path, settings):
    replay_dir = './.gen-replay'
    layout_dir = 'layout'
    ret = cookiecutter(str(pathlib.Path(path, layout_dir)),
                        # no_input=True,
                        overwrite_if_exists=True,
                        replay=pathlib.Path(replay_dir, f'{layout_dir}.json').exists(),
                        default_config=dict(replay_dir=replay_dir),
                        output_dir=settings.out_dir)
    return pathlib.Path(ret)


def _get_with_tags(type_):
    for a in get_args(type_):
        if hasattr(a, '_tags'):
            yield a


def _get_tag_from_type(gen_name, type_):
    for tag in type_._tags:
        if tag.gen == gen_name:
            yield tag
            break


def _generate_nullable(gen_name, field_name, type_):
    # todo: check second is None
    for a in _get_with_tags(type_):
        for tag in _get_tag_from_type(gen_name, a):
            tag.make_nullable()
            tag.set_comment(a.__doc__)
            tag.set_name(field_name)
            yield tag


def _generate_multiple(gen_name, field_name, type_):
    for a in _get_with_tags(type_):
        for tag in _get_tag_from_type(gen_name, a):
            tag.make_multiple()
            tag.set_comment(a.__doc__)
            tag.set_name(field_name)
            yield tag


def _generate_field(gen_name, field_name, type_):
    for tag in _get_tag_from_type(gen_name, type_):
        tag.set_comment(type_.__doc__)
        tag.set_name(field_name)
        yield tag


def _generate_fields(gen_name, annotations):
    for field_name, type_ in annotations.items():
        if type(type_) == UnionType:
            yield from _generate_nullable(gen_name, field_name, type_)
        elif type(type_) == GenericAlias and get_origin(type_) == list:
            yield from _generate_multiple(gen_name, field_name, type_)
        elif hasattr(type_, '_tags'):
            yield from _generate_field(gen_name, field_name, type_)
        else:
            raise RuntimeError(f'Type `{type_}` not supported')


def _generate_class(env, klass, class_tag, field_tags):
    field_tmpl = env.get_template(f'field.jinja')
    ctx = {
        'class': klass,
        'class_decorator': class_tag,
        'fields': [field_tmpl.render(dict(type=t)) for t in field_tags]
    }
    return env.get_template('class.jinja').render(ctx).strip()


def _write_file(content, path):
    with open(path, 'w+') as f:
        f.write(content.strip())


def generate_docker_file(gen_name, path):
    shutil.copy(pathlib.Path(path, 'Dockerfile'), f'./Dockerfile-{gen_name}')


def generate(gen_name, path, enums, classes, deps, settings):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(pathlib.Path(path, 'templates')))
    rendered_classes = []
    for _, klass in classes:
        field_tags = []
        for tag in klass._tags:
            if tag.gen == gen_name:
                break
        else:
            continue
        tag.set_comment(_format_doc_string(klass.__doc__))
        bases = [b for b in inspect.getmro(klass)[1:] if hasattr(b, '_tags')]
        annotations = dict()
        bases_tags = []
        for b in reversed(bases):
            bases_tags += b._tags
            annotations.update(b.__annotations__)
        tag.set_bases_tags(bases_tags)
        annotations.update(klass.__annotations__)
        field_tags += list(_generate_fields(gen_name, annotations))
        if len(field_tags) == 0:
            continue
        rendered = _generate_class(env, klass, tag, field_tags)
        if len(rendered) > 0:
            rendered_classes.append(rendered)
    # todo: !!!! prevent override enums with same class names
    effective_enums = [e for name, e in enums if ('enums', name.split('.')[-1]) in deps]
    if len(rendered_classes) > 0 or len(effective_enums) > 0:
        out_dir = _create_dir_structure(path, settings)
        if len(rendered_classes) > 0:
            file_tmpl = env.get_template(f'file.jinja')
            _write_file(file_tmpl.render(
                dict(classes=rendered_classes, deps=deps)), out_dir / settings.classes_file_name)
        if len(effective_enums) > 0:
            enum_tmpl = env.get_template(f'enums.jinja')
            _write_file(enum_tmpl.render(dict(enums=effective_enums)), out_dir / settings.enums_file_name)
        return out_dir
