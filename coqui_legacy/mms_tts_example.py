import torch

# Load model directly
from transformers import AutoTokenizer, AutoModelForTextToWaveform
import scipy

gpu_is_active = torch.cuda.is_available()
device = torch.device("cuda:0" if gpu_is_active else "cpu")

tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-spa")
model = AutoModelForTextToWaveform.from_pretrained("facebook/mms-tts-spa")
if gpu_is_active == "cuda":
    model.to(device)  # Move the model to the GPU
text_input = "Hola, ¿cómo estás?"
inputs = tokenizer(
    text=[text_input],
    return_tensors="pt",
)
inputs = inputs.to(device)  # Move the inputs to the GPU

with torch.no_grad():
    output = model(**inputs).waveform

output_audio_file = "synthesized_speech"
scipy.io.wavfile.write(f"{output_audio_file}.wav", rate=model.config.sampling_rate, data=output)