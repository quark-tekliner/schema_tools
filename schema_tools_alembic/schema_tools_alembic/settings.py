from schema_tools.settings import Settings as Base


class Settings(Base):

    classes_file_name: str = 'classes.py'
    enums_file_name: str = 'enums.py'
    black: str = './bin/python -m black {out_dir}'