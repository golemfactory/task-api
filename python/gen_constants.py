import sys
from pathlib import Path

from golem_task_api.proto import constants_pb2


def main(output_file: Path):
    src = """# This file is auto-generated from gen_constants.py


"""
    for field, value in constants_pb2.DESCRIPTOR.GetOptions().ListFields():
        src += f"{field.name} = '{value}'\n"
    with open(output_file, 'w') as f:
        f.write(src)


if __name__ == '__main__':
    main(Path(sys.argv[1]))
