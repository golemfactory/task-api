import sys
from pathlib import Path
from typing import Any, Dict

from google.protobuf.descriptor import EnumDescriptor


def main(input_module_file: Path, output_file: Path):
    src = """# This file is auto-generated from gen_enums.py
from enum import Enum"""

    input_module_src = input_module_file.read_text('utf-8')
    input_module: Dict[str, Any] = dict()
    exec(input_module_src, input_module)

    def enum_src(enum_name: str, enum_descriptor: EnumDescriptor) -> str:
        code = f"\n\n\nclass {enum_name}(Enum):"
        for value_descriptor in list(enum_descriptor.values):
            code += f"\n    {value_descriptor.name} = {value_descriptor.number}"
        return code

    def parse_enums(descriptor) -> str:
        code = ''
        for enum_name, enum_desc in descriptor.enum_types_by_name.items():
            code += enum_src(enum_name, enum_desc)
        return code

    def parse_message(descriptor) -> str:
        code = parse_enums(descriptor)
        for _, type_desc in descriptor.nested_types_by_name.items():
            code += parse_message(type_desc)
        return code

    src += parse_enums(input_module['DESCRIPTOR'])
    for _, desc in input_module['DESCRIPTOR'].message_types_by_name.items():
        src += parse_message(desc)

    with open(output_file, 'w') as f:
        f.write(src)
        f.write("\n")


if __name__ == '__main__':
    main(Path(sys.argv[1]), Path(sys.argv[2]))
