from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Tariff:
    code: str
    label: str
    price_cents: int


_TARIFFS: dict[str, Tariff] = {
    "standard": Tariff("standard", "Plein tarif", 1200),
    "student": Tariff("student", "Etudiant", 900),
    "under16": Tariff("under16", "Moins de 16 ans", 700),
    "unemployed": Tariff("unemployed", "Demandeur d'emploi", 800),
}

DEFAULT_TARIFF = "standard"


def available_codes() -> Iterable[str]:
    return _TARIFFS.keys()


def get_tariff(code: str | None) -> Tariff:
    normalized = (code or DEFAULT_TARIFF).strip().lower()
    if normalized not in _TARIFFS:
        raise KeyError(
            f"Invalid tariff '{code}'. Allowed values: {', '.join(_TARIFFS)}."
        )
    return _TARIFFS[normalized]


def serialize_all() -> dict[str, dict[str, int | str]]:
    return {
        code: {"label": tariff.label, "price_cents": tariff.price_cents}
        for code, tariff in _TARIFFS.items()
    }
