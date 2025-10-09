"""
Instancias globales de schedulers
"""
from backend.scheduler.cleanup_scheduler import CleanupScheduler

# Instancia global del scheduler de limpieza
cleanup_scheduler = CleanupScheduler()
