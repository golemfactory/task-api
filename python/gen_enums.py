import sys
from pathlib import Path

from google.protobuf.descriptor import EnumDescriptor


def main(input_module_file: Path, output_file: Path):
    src = """# This file is auto-generated from gen_enums.py
from enum import Enum
"""

    input_module_src = input_module_file.read_text('utf-8')
    input_module = dict()
    exec(input_module_src, input_module)

    def enum_src(enum_name: str, enum_descriptor: EnumDescriptor) -> str:
        code = f"\n\nclass {enum_name}(Enum):"
        for value_descriptor in list(enum_descriptor.values):
            code += f"\n    {value_descriptor.name} = {value_descriptor.number}"
        return code

    # Top level enums
    for name, desc in input_module['DESCRIPTOR'].enum_types_by_name.items():
        src += enum_src(name, desc)

    # Enums embedded in messages
    for _, msg_desc in input_module['DESCRIPTOR'].message_types_by_name.items():
        for name, desc in msg_desc.enum_types_by_name.items():
            src += enum_src(name, desc)

    with open(output_file, 'w') as f:
        f.write(src)
        f.write("\n")


if __name__ == '__main__':
    main(Path(sys.argv[1]), Path(sys.argv[2]))
