from background_task import background

from thomas_ai.tasks.extract import extract


@background(schedule=0, queue='analyze')
def analyze(vocal_id: int):
    extract(vocal_id=vocal_id)