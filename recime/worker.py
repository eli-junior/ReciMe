"""Executor demonstrativo local: uv run python -m recime.worker."""
import argparse
from contextlib import contextmanager
import logging
import signal
import threading

from filelock import FileLock, Timeout

from recime import demo
from recime.store import Store, db_path


@contextmanager
def exclusive_worker(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = FileLock(path.with_suffix(path.suffix + ".worker.lock"), timeout=0)
    try:
        lock.acquire()
    except Timeout:
        raise RuntimeError("Já existe um executor para este banco.") from None
    try:
        yield
    finally:
        lock.release()


def process_one(store, stop=None, delay=0):
    stop = stop or threading.Event()
    item = store.claim()
    if item is None:
        return False
    if stop.wait(delay):
        store.finish(item["id"], error="Processamento interrompido. Você pode tentar novamente.")
    elif item["code"] != demo.DEMO_CODE:
        store.finish(item["id"], error="Não há amostra para este link. Esta demonstração não acessa o Instagram. Use o link de exemplo.")
    elif item["scenario"] == "fail_once" and item["attempts"] == 1:
        store.finish(item["id"], error="Falha simulada na primeira tentativa. Tente novamente para carregar a amostra.")
    else:
        store.finish(item["id"], draft=demo.recipe())
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delay", type=float, default=3, help="Espera demonstrativa em segundos (0 a 120).")
    parser.add_argument("--once", action="store_true", help="Processa no máximo um item e encerra.")
    args = parser.parse_args()
    if not 0 <= args.delay <= 120:
        parser.error("--delay deve estar entre 0 e 120")
    store, stop = Store(db_path()), threading.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda *_: stop.set())
    with exclusive_worker(store.path):
        store.initialize()
        store.recover()
        logging.warning("Executor de DEMONSTRAÇÃO iniciado; não faz downloads nem chamadas de IA.")
        while not stop.is_set():
            worked = process_one(store, stop, args.delay)
            if args.once:
                break
            if not worked:
                stop.wait(1)


if __name__ == "__main__":
    main()
