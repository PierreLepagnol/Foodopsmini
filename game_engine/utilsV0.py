import json
from pathlib import Path
from typing import Callable, Union

from pydantic import BaseModel, RootModel


def get_input(
    input_message: str,
    fn_validation: Callable,
    error_message: str = "Erreur dans la saisie",
):
    """Prompt for an integer with validation.

    - input_message: prompt shown to the user
    - fn_validation: predicate taking the parsed int and returning True if valid
    - error_message: message displayed on invalid input
    """
    while True:
        try:
            result = int(input(input_message).strip())
            if fn_validation(result):
                return result
        except Exception:
            pass
        print(error_message)


def load_and_validate(data_path: Path, model: Union[RootModel, BaseModel]) -> BaseModel:
    """
    Load and validate model data from data_path.
    Returns a validated model instance.
    """
    if not data_path.exists():
        raise FileNotFoundError(f"Concept fit data file not found: {data_path}")

    with data_path.open("r", encoding="utf-8") as f:
        raw_data = json.load(f)
        return model.model_validate(raw_data)
