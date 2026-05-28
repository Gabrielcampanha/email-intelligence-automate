from app.monitoring.logger import logger

def send_alert(message: str, severity: str = "CRITICAL"):
    """
    Simula o envio de um alerta. Em produção, poderia ser via Slack, PagerDuty ou Email.
    """
    logger.error(f"ALERT [{severity}]: {message}", alert=True)

class FailureMonitor:
    def __init__(self, threshold: int = 3):
        self.consecutive_failures = 0
        self.threshold = threshold

    def record_failure(self, error_msg: str):
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.threshold:
            send_alert(f"IA falhou {self.consecutive_failures} vezes consecutivas. Erro: {error_msg}")

    def record_success(self):
        self.consecutive_failures = 0

# Instância global para monitoramento de falhas de IA
ia_monitor = FailureMonitor()
