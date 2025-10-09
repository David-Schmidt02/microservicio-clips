"""
Scheduler para limpieza automática de clips temporales
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.services.cleanup_service import CleanupService
from backend.config.settings import settings


class CleanupScheduler:
    """Programador de tareas de limpieza automática"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.cleanup_service = CleanupService()
        self._running = False

    def ejecutar_limpieza(self, max_age_hours: int = 2):
        """
        Ejecuta la limpieza de clips antiguos.

        Args:
            max_age_hours: Edad máxima en horas de los clips a mantener
        """
        try:
            cantidad, archivos = self.cleanup_service.limpiar_clips_antiguos(max_age_hours)

            if cantidad > 0:
                print(f"\n[CLEANUP] Limpieza automatica ejecutada:")
                print(f"   OK: {cantidad} archivo(s) eliminado(s)")
                for archivo in archivos[:5]:  # Mostrar máximo 5
                    print(f"      - {archivo}")
                if len(archivos) > 5:
                    print(f"      ... y {len(archivos) - 5} mas")
            else:
                print(f"[CLEANUP] No hay clips antiguos para eliminar")

        except Exception as e:
            print(f"[ERROR] Error en limpieza automatica: {e}")

    def iniciar(self, intervalo_horas: int = 1, max_age_hours: int = 2):
        """
        Inicia el scheduler de limpieza automática.

        Args:
            intervalo_horas: Cada cuántas horas ejecutar la limpieza (por defecto 1)
            max_age_hours: Edad máxima de clips a mantener (por defecto 2)
        """
        if self._running:
            print("[WARNING] Scheduler ya esta ejecutandose")
            return

        # Agregar tarea de limpieza
        self.scheduler.add_job(
            func=self.ejecutar_limpieza,
            trigger=IntervalTrigger(hours=intervalo_horas),
            args=[max_age_hours],
            id='cleanup_clips',
            name=f'Limpieza de clips cada {intervalo_horas}h',
            replace_existing=True,
            max_instances=1  # Evitar ejecuciones concurrentes
        )

        # Iniciar scheduler
        self.scheduler.start()
        self._running = True

        print(f"\n[SCHEDULER] Limpieza automatica iniciada:")
        print(f"   - Intervalo: cada {intervalo_horas} hora(s)")
        print(f"   - Elimina clips de mas de {max_age_hours} hora(s)")
        #print(f"   - Directorio: {settings.OUTPUT_DIR}\n")

    def detener(self):
        """Detiene el scheduler de limpieza"""
        if not self._running:
            return

        try:
            self.scheduler.shutdown(wait=False)
            self._running = False
            print("[SCHEDULER] Scheduler de limpieza detenido")
        except Exception as e:
            print(f"[WARNING] Error al detener scheduler: {e}")

    def obtener_estado(self) -> dict:
        """
        Obtiene el estado actual del scheduler.

        Returns:
            Diccionario con información del estado
        """
        if not self._running:
            return {
                "activo": False,
                "mensaje": "Scheduler no está ejecutándose"
            }

        jobs = self.scheduler.get_jobs()

        if not jobs:
            return {
                "activo": True,
                "tareas": 0,
                "mensaje": "Scheduler activo pero sin tareas programadas"
            }

        job = jobs[0]
        next_run = job.next_run_time

        return {
            "activo": True,
            "tareas": len(jobs),
            "proxima_ejecucion": next_run.isoformat() if next_run else None,
            "nombre_tarea": job.name
        }
