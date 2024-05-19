from pydub import AudioSegment
from pydub.silence import split_on_silence
from openai import OpenAI

AUDIO_FILE_NAME = "audio_recordings/audio.mp3"
AUDIO_FILE_TYPE = AUDIO_FILE_NAME.split(".")[-1]


def transcribe_audio(file_path, transciption_client: OpenAI):
    audio_file = open(file_path, "rb")
    transcript = transciption_client.audio.transcriptions.create(
        model="whisper-1", file=audio_file
    )

    return transcript.text


# TODO - don't need this now, but if you envision having audio segments longer than 22 minutes that need to be transcribed you'll have to do this
def transcribe_long_audio(file_path, client):
    # Load your audio file
    audio = AudioSegment.from_file(file_path, format="mp3")

    # Split audio where silence is longer than 1000ms (1 second) and silence is quieter than -40dBFS
    chunks = split_on_silence(audio, min_silence_len=1000, silence_thresh=-40)

    # Define the maximum size in bytes (25MB)
    max_size = 25 * 1024 * 1024

    # Function to split a chunk into smaller chunks based on size
    def split_chunk_on_size(chunk, max_size):
        chunk_size = len(chunk.raw_data)
        if chunk_size <= max_size:
            return [chunk]

        # Calculate the number of parts needed
        num_parts = (chunk_size // max_size) + 1
        part_length = len(chunk) // num_parts

        return [
            chunk[i * part_length : (i + 1) * part_length] for i in range(num_parts)
        ]

    # Split chunks further based on size
    final_chunks = []
    for chunk in chunks:
        final_chunks.extend(split_chunk_on_size(chunk, max_size))

    # Export each chunk as a separate file
    for i, chunk in enumerate(final_chunks):
        chunk.export(f"audio_recordings/chunk{i}.mp3", format="mp3")

    transcriptions = []

    for i in range(len(chunks)):
        print(f"Transcribing chunk: {i} of {len(chunks)}")
        chunk_file = f"audio_recordings/chunk{i}.mp3"
        transcription = transcribe_audio(chunk_file, client)
        transcriptions.append(transcription)

    # Combine all transcriptions into a single text
    full_transcription = " ".join(transcriptions)

    return full_transcription
