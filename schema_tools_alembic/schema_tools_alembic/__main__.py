import pathlib
import sys
import subprocess
from definitions import enums, classes
from schema_tools.generator import generate, generate_docker_file
from schema_tools_alembic.alembic import deps
from schema_tools_alembic.settings import Settings

name = 'alembic'

if len(sys.argv) > 1 and sys.argv[1] == 'dockerfile':
    generate_docker_file(name, pathlib.Path(__file__).parent.resolve())
    exit(0)

out_dir = generate(name, pathlib.Path(__file__).parent.resolve(), enums, classes, deps, Settings())
if out_dir is not None:
    subprocess.run(f'./bin/python -m black {out_dir}'.split(' '))
