from pathlib import Path
from typing import Optional, List, Dict, Tuple, Type

import peewee
from golem_task_api.apputils.database import (
    database,
    initialize_database,
)
from golem_task_api.apputils.database.fields import EnumField
from golem_task_api.apputils.task import SubtaskStatus, TaskManager


class Part(peewee.Model):

    class Meta:
        database = database

    num = peewee.IntegerField(
        primary_key=True,
        unique=True)
    subtask = peewee.DeferredForeignKey(
        'Subtask',
        null=True,
        index=True,
        backref='parts')


class Subtask(peewee.Model):

    class Meta:
        database = database

    id = peewee.CharField(
        primary_key=True,
        unique=True)
    part = peewee.ForeignKeyField(
        Part,
        null=True,
        index=True,
        backref='subtasks')
    status = EnumField(
        SubtaskStatus,
        default=SubtaskStatus.default)


class DBTaskManager(TaskManager):
    """ TaskManager subclass with a SQLite database backend for persistence """

    def __init__(
            self,
            work_dir: Path,
            part_model: Type[Part] = Part,
            subtask_model: Type[Subtask] = Subtask,
    ) -> None:

        self._part = part_model
        self._subtask = subtask_model
        models = [self._part, self._subtask]

        initialize_database(
            db=self._database,
            db_path=work_dir / 'task.db',
            models=models)

    @property
    def _database(self) -> peewee.Database:
        """ Return an instance of a chosen `peewee.Database` subclass """
        return peewee.SqliteDatabase(
            database=None,
            thread_safe=True,
            pragmas=(
                ('foreign_keys', True),
                ('busy_timeout', 1000),
                ('journal_mode', 'WAL'),
            ),
        )

    def create_task(
            self,
            part_count: int,
    ) -> None:
        with database.atomic():
            for num in range(part_count):
                self._part.create(num=num, subtask=None)

    def abort_task(
            self,
    ) -> None:

        self._subtask.update(
            status=SubtaskStatus.ABORTED,
        ).where(
            self._subtask.status != SubtaskStatus.SUCCESS,
            self._subtask.id.in_(
                self._part.select(
                    self._part.subtask.id
                )
            )
        ).execute()

    def get_part(
            self,
            part_num: int,
    ) -> Optional[Part]:
        try:
            return self._part.get(num=part_num)
        except peewee.DoesNotExist:
            return None

    def get_part_num(
            self,
            subtask_id: str,
    ) -> Optional[int]:

        result = self._part.select(
            self._part.num
        ).join(
            self._subtask
        ).where(
            self._subtask.id == subtask_id
        ).execute()

        return result[0].num if result else None

    def get_subtask(
            self,
            subtask_id: str,
    ) -> Optional[Subtask]:
        try:
            return self._subtask.get(id=subtask_id)
        except peewee.DoesNotExist:
            return None

    def start_subtask(
            self,
            part_num: int,
            subtask_id: str,
    ) -> None:

        status = self.get_subtasks_statuses([part_num])
        if status and part_num in status:
            if not status[part_num][0].is_computable():
                raise RuntimeError(f"Subtask {part_num} already started")

        with database.atomic():
            part = self._part.get(self._part.num == part_num)
            part.subtask = subtask_id
            part.save()

            self._subtask.create(
                id=subtask_id,
                part=part,
                status=SubtaskStatus.COMPUTING)

    def update_subtask_status(
        self,
        subtask_id: str,
        status: SubtaskStatus
    ) -> None:

        self._subtask.update(
            status=status,
        ).where(
            self._subtask.id == subtask_id,
        ).execute()

    def get_subtasks_statuses(
            self,
            part_nums: List[int],
    ) -> Dict[int, Tuple[SubtaskStatus, Optional[str]]]:

        parts = self._part.select(
            self._part.num,
            self._subtask.status,
            self._subtask.id,
        ).join(
            self._subtask,
            join_type=peewee.JOIN.LEFT_OUTER,
        ).where(
            self._part.num.in_(part_nums),
        ).execute()

        return {
            p.num: (
                SubtaskStatus(p.subtask.status if p.subtask else None),
                p.subtask.id if p.subtask else None
            )
            for p in parts
        }

    def get_next_computable_part_num(
            self,
    ) -> Optional[int]:

        results = self._part.select(
            self._part.num
        ).where(
            ~peewee.fn.EXISTS(
                self._subtask.select(
                    self._subtask.id,
                ).where(
                    self._subtask.id == self._part.subtask,
                    self._subtask.status.not_in((
                        SubtaskStatus.ABORTED,
                        SubtaskStatus.FAILURE
                    ))
                )
            )
        ).order_by(
            self._part.num.asc()
        ).limit(1).execute()

        return results[0].num if results else None
