import json
from pathlib import Path


def load_emails() -> list[dict]:
    """
    Carrega e-mails do arquivo JSON mockado.
    """
    data_dir = Path(__file__).parent.parent.parent / "data"
    json_path = data_dir / "emails_mock.json"

    with open(json_path, "r", encoding="utf-8") as file:
        emails = json.load(file)

    return emails


def get_unprocessed_emails() -> list[dict]:
    """
    Retorna todos os e-mails não processados (todos os e-mails do arquivo mock).
    """
    return load_emails()
