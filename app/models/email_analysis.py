from dataclasses import dataclass

@dataclass
class EmailAnalysis:
    """
    Representa a análise estruturada de um e-mail feita pela IA.
    """
    categoria: str
    urgente: bool
    resumo: str
    acao_recomendada: str
