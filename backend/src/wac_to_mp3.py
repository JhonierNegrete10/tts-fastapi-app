from pydub import AudioSegment

def convert_wav_to_mp3(wav_file_path, mp3_file_path):
    # Load the WAV file
    audio = AudioSegment.from_wav(wav_file_path)
    
    # Export as MP3
    audio.export(mp3_file_path, format="mp3")

if __name__ == "__main__":
    wav_file_path = "./output_2.wav"
    mp3_file_path = "./output_2.mp3"
    convert_wav_to_mp3(wav_file_path, mp3_file_path)