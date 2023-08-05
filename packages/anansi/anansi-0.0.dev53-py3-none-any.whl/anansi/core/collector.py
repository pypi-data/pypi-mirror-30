"""Define Collector class."""
from enum import IntFlag, auto
from typing import Any, Callable, Iterable, Type, Union

from .collection import Collection
from .query import Query as Q


class CollectorFlags(IntFlag):
    """Flags for the Collector class."""

    Virtual = auto()


class Collector:
    """Class to generate a collection from a record."""

    Flags = CollectorFlags

    def __init__(
        self,
        *,
        code: str=None,
        flags: CollectorFlags=CollectorFlags(0),
        gettermethod: Callable=None,
        model: str=None,
        name: str=None,
        querymethod: Callable=None,
        settermethod: Callable=None,
        source: str=None,
        target: str=None,
        through: str=None,
    ):
        self._model = model
        self.code = code
        self.source = source
        self.gettermethod = gettermethod
        self.name = name
        self.querymethod = querymethod
        self.settermethod = settermethod
        self.through = through
        self.target = target

    async def assert_valid(self, value: Any):
        """Assert the given value can be assigned to this reference."""
        pass

    async def collect(
        self,
        record: 'Model',
        ignore_method: bool=False,
    ) -> Collection:
        """Create collection for specific record."""
        if self.gettermethod and not ignore_method:
            return await self.gettermethod(record)

        q = None

        if self.through:
            collection = await self.through_model.select(
                fields=self.target,
                where=Q(self.source) == record
            )
            keys = self.model.__schema__.key_fields
            key = (
                tuple(k.code for k in keys)
                if len(keys) > 1 else
                keys[0].code
            )
            q = Q(key).is_in(collection)

        elif self.source:
            q = Q(self.source) == record

        return Collection(
            collector=self,
            model=self._model,
            source=record,
            where=q,
        )

    def getter(self, func: callable) -> callable:
        """Assign gettermethod via decorator."""
        self.gettermethod = func
        return func

    def make_collection(
        self,
        *,
        constructor: callable=None,
        records: Iterable=None,
        source: 'Model'=None
    ) -> Collection:
        """Create new collection instance from value."""
        if isinstance(records, Collection):
            return records

        model = self.model
        constructor = constructor or (lambda x: model(values=x))
        if model is not None and records:
            records = [
                constructor(record) if type(record) is dict else record
                for record in records
            ]
            return Collection(
                collector=self,
                model=self._model,
                records=records,
                source=source
            )
        return Collection(
            collector=self,
            model=self._model,
            records=records,
            source=source
        )

    def get_model(self):
        """Return Model class instance associated with this collector."""
        if type(self._model) is str:
            from .model import Model
            return Model.find_model(self._model)
        return None

    def query(self, func: callable) -> callable:
        """Assign querymethod via decorator."""
        self.querymethod = func
        return func

    @property
    def source_field(self) -> 'Field':
        """Return the source field."""
        if not self.source:
            return None

        model = self.through_model or self.model
        if model:
            return model.__schema__[self.source]
        return None

    def setter(self, func: callable) -> callable:
        """Assign settermethod via decorator."""
        self.settermethod = func
        return func

    def set_model(self, model: Union[str, Type['Model']]):
        """Assign model type for this collector."""
        self._model = model

    @property
    def target_field(self) -> 'Field':
        """Return the target field."""
        if not self.target:
            return None

        model = self.through_model or self.model
        if model:
            return model.__schema__[self.target]
        return None

    @property
    def through_model(self) -> 'Field':
        """Return the through model for a piped collector."""
        if type(self.through) is str:
            from .model import Model
            return Model.find_model(self.through)
        return self.through

    model = property(get_model, set_model)
