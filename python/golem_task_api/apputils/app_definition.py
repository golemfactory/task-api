from distutils import cmd
import hashlib
import json
import shutil

from pathlib import Path
from typing import Dict, Any

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from marshmallow import fields as mm_fields, validate

AppId = str


@dataclass_json
@dataclass
class AppDefinitionBase:
    name: str
    requestor_env: str
    requestor_prereq: Dict[str, Any] = field(metadata=config(
        mm_field=mm_fields.Dict(keys=mm_fields.Str())
    ))
    max_benchmark_score: float
    version: str = '0.0'
    description: str = ''
    author: str = ''
    license: str = ''
    market_strategy: str = mm_fields.Str(
        validate=validate.OneOf(["brass", "wasm"]),
        default='brass'
    )

    @property
    def id(self) -> AppId:
        return hashlib.blake2b(  # pylint: disable=no-member
            self.to_json().encode('utf-8'),
            digest_size=16
        ).hexdigest()

    @classmethod
    def from_json(cls, json_str: str) -> 'AppDefinitionBase':
        raise NotImplementedError  # A stub to silence the linters

    def to_json(self) -> str:
        raise NotImplementedError  # A stub to silence the linters


def save_app_to_json_file(app_def: AppDefinitionBase, json_file: Path) -> None:
    """ Save application definition to the given file in JSON format.
        Create parent directories if they don't exist. """
    try:
        json_file.parent.mkdir(parents=True, exist_ok=True)
        json_file.write_text(app_def.to_json())
    except OSError:
        msg = f"Error writing app definition to file '{json_file}."
        print(msg)
        raise ValueError(msg)


class BuildAppDefCommand(cmd.Command):
    description = 'build app definition for distribution in golem'
    user_options = [
        # The format is (long option, short option, description).
        ('dist-path', 'd',
            'Path to output build results, will be deleted before build'),
        ('config-path', 'c', 'Config file with task-api settings'),
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.dist_path = ''
        self.config_path = ''

    def finalize_options(self):
        """Post-process options."""
        if self.dist_path:
            self.dist_path = Path(self.dist_path)
        else:
            self.dist_path = Path('dist/')
        if self.config_path:
            self.config_path = Path(self.config_path)
        else:
            self.config_path = Path('task-api-config.json')
        self.config = json.loads(self.config_path.read_text())

    def run(self):
        """Run command."""
        shutil.rmtree(self.dist_path, ignore_errors=True)
        self.dist_path.mkdir()

        dist = self.distribution
        version = dist.get_version()
        description = dist.get_description()
        author = dist.get_maintainer()
        license = dist.get_license()

        name = self.config['name']
        app_definition = AppDefinitionBase(
            name=name,
            author=author,
            license=license,
            version=version,
            market_strategy=self.config['market_strategy'],
            description=description,
            requestor_env=self.config['requestor_env'],
            requestor_prereq=self.config['requestor_prereq'],
            max_benchmark_score=self.config['max_benchmark_score'],
        )
        file = self.dist_path / f'{name.replace("/", "_")}_{version}_' \
            f'{app_definition.id}.json'
        save_app_to_json_file(app_definition, file)
        print(f'Saved app_definition to "{file}"')
