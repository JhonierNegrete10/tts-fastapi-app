"""the original example code
# IS_GPU = not torch.cuda.is_available()
# DEVICE = torch.device("cuda:0" if IS_GPU else "cpu")

# Initialize model and tokenizer
# TOKENIZER = AutoTokenizer.from_pretrained("facebook/mms-tts-spa")
# MODEL_TTS = AutoModelForTextToWaveform.from_pretrained("facebook/mms-tts-spa")
# TOKENIZER = VitsTokenizer.from_pretrained("facebook/mms-tts-spa")
# MODEL_TTS = VitsModel.from_pretrained("facebook/mms-tts-spa")
# MODEL_TTS.to(DEVICE)
#


# waveform = outputs.waveform[0]
#         scipy.io.wavfile.write(
#             output_path,
#             rate=MODEL_TTS.config.sampling_rate,
#             data=waveform.cpu().numpy(),
#         )
"""

import torch
import scipy.io.wavfile
from transformers import (
    # AutoTokenizer,
    # AutoModelForTextToWaveform,
    VitsTokenizer,
    VitsModel,
    set_seed,
)
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

set_seed(555)  # make deterministic

class TTSLocalModel:
    def __init__(self):
        self.tokenizer = VitsTokenizer.from_pretrained("facebook/mms-tts-spa")
        self.model = VitsModel.from_pretrained("facebook/mms-tts-spa").to(
            self._get_device()
        )

    def _is_gpu(self):
        return not torch.cuda.is_available()

    def _get_device(self):
        return torch.device("cuda:0" if self._is_gpu() else "cpu")

    def sintetic_voice(self, text: str):
        # Encode text to tensor
        inputs = self.tokenizer(text, return_tensors="pt")
        # Generate waveform
        with torch.no_grad():
            waveform = self.model(**inputs.to(self._get_device()))
        return waveform

    def save_waveform(self, waveform, output_path: str):
        # Save waveform to file
        waveform = waveform.cpu().numpy()
        try:
            scipy.io.wavfile.write(
                output_path,
                rate=self.model.config.sampling_rate,
                data=waveform,
            )
            return output_path
        except Exception as e:
            logger.error(f"Failed to save waveform: {e}")
            raise

