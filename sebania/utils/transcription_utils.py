def cleanup_transcription(transcription: str) -> str:
    return (transcription.lower().strip()
            .replace(",", "")
            .replace(".", "")
            .replace("!", "")
            .replace("?", "")
            .replace(" ", ""))