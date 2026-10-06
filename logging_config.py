import logging
from pathlib import Path

def configure_logging():
    log_dir = Path(__file__).resolve().parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        handlers=[logging.FileHandler(log_dir/'app.log', encoding='utf-8'), logging.StreamHandler()],
        force=True,
    )
