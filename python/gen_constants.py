import importlib
import sys
from pathlib import Path


def main(input_module_name: str, output_file: Path):
    src = """# This file is auto-generated from gen_constants.py


"""
    input_module = importlib.import_module(input_module_name)
    fields = input_module.DESCRIPTOR.GetOptions().ListFields()  # type: ignore
    for field, value in fields:
        src += f"{field.name} = '{value}'\n"
    with open(output_file, 'w') as f:
        f.write(src)


if __name__ == '__main__':
    main(sys.argv[1], Path(sys.argv[2]))
