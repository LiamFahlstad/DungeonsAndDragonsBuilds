import functools
from typing import Callable, TypeVar, cast


class SealedError(RuntimeError):
    """Something tried to record onto an evaluated part. A Character rebuilds
    its Ledger from its sources whenever they change, so a write there would
    be silently lost at the next rebuild."""


class Recorder:
    """Base of every part (and of the Ledger that holds them). Effects record
    into a part through its @records methods while the Character evaluates;
    the Character then seals the Ledger, and any later write raises
    SealedError. Grant the effect instead (Character.add_feature,
    Character.add_effect, ...)."""

    _sealed = False

    def seal(self) -> None:
        """Seal this part and every part it holds."""
        self._sealed = True
        for value in vars(self).values():
            children = value.values() if isinstance(value, dict) else [value]
            for child in children:
                if isinstance(child, Recorder):
                    child.seal()


Method = TypeVar("Method", bound=Callable)


def records(method: Method) -> Method:
    """Marks a part's mutator: it raises SealedError once the part is sealed."""

    @functools.wraps(method)
    def guarded(self: Recorder, *args, **kwargs):
        if self._sealed:
            raise SealedError(
                f"{type(self).__name__}.{method.__name__}: this part was already "
                "evaluated and is read-only. Grant the effect instead "
                "(Character.add_feature, Character.add_effect, ...)."
            )
        return method(self, *args, **kwargs)

    return cast(Method, guarded)
