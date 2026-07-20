import asyncio
from sqlmodel import Session, SQLModel
from backend.app.core.db import engine

class WriteManager:
    """Centralized, thread-safe asynchronous SQLite writer queue singleton."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WriteManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.queue = asyncio.Queue()
        self.worker_task = None
        self._initialized = True

    async def start(self):
        """Starts the background worker queue task if not already running."""
        if self.worker_task is None or self.worker_task.done():
            self.worker_task = asyncio.create_task(self._process_writes())

    async def execute_write(self, model_instance: SQLModel) -> SQLModel:
        """Pushes a SQLModel object into the queue and waits for execution outcome."""
        await self.start()  # Safe lazy loader
        future = asyncio.get_running_loop().create_future()
        await self.queue.put((model_instance, future))
        return await future

    async def _process_writes(self):
        """Sequential database transaction executor."""
        while True:
            model_instance, future = await self.queue.get()
            try:
                # Execute transaction synchronously inside a session
                with Session(engine) as session:
                    session.add(model_instance)
                    session.commit()
                    session.refresh(model_instance)
                future.set_result(model_instance)
            except Exception as e:
                future.set_exception(e)
            finally:
                self.queue.task_done()

write_manager = WriteManager()
