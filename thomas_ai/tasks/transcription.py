from background_task import background

@background(schedule=0)
def transcribe(voice_message_id: int):
    pass