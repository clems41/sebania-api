from background_task import background

@background(schedule=0, queue='extract')
def extract(vocal_id: int):
    pass