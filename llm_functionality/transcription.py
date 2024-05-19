from pydub import AudioSegment
from pydub.silence import split_on_silence
from openai import OpenAI


def transcribe_audio(file_path, transciption_client: OpenAI):

    audio_file = open(file_path, "rb")
    transcript = transciption_client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )

    return transcript.text


def transcribe_long_audio(file_path):
    # Load your audio file
    audio = AudioSegment.from_file(file_path, format="wav")

    # Split audio where silence is longer than 1000ms (1 second) and silence is quieter than -40dBFS
    chunks = split_on_silence(audio, min_silence_len=1000, silence_thresh=-40)

    # Export each chunk as a separate file
    for i, chunk in enumerate(chunks):
        chunk.export(f"chunk{i}.wav", format="wav")

    transcriptions = []

    for i in range(len(chunks)):
        print(f"Transcribing chunk: {i} of {len(chunks)}")
        chunk_file = f"chunk{i}.wav"
        transcription = transcribe_audio(chunk_file)
        transcriptions.append(transcription)

    # Combine all transcriptions into a single text
    full_transcription = " ".join(transcriptions)

    return full_transcription