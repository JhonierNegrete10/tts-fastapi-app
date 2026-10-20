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
        return torch.cuda.is_available()

    def _get_device(self):
        return torch.device("cuda:0" if self._is_gpu() else "cpu")

    def _sintetic_voice(self, text: str):
        print(f"Sintetic voice: {self._is_gpu()}")
        # Encode text to tensor
        try:
            inputs = self.tokenizer(text, return_tensors="pt")
            # print(f"Inputs: {inputs}")
        except Exception as e:
            logger.error(f" self.tokenizer() Failed to generate synthetic voice: {e}")
            raise
        # Generate waveform
        try:
            with torch.no_grad():
                outputs = self.model(**inputs.to(self._get_device()))
            return outputs
        except Exception as e:
            logger.error(f"torch.no_grad() Failed to generate synthetic voice: {e}")
            raise

    def save_waveform(self, outputs, output_path: str):
        # Save waveform to file
        if not self._is_gpu():
            waveform = outputs.waveform.cpu().numpy()
        else:
            waveform = outputs.waveform[0].cpu().numpy()
        # print(f"Waveform: {waveform}")
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

    def synthetic_voice(self, text: str, output_path: str = "output.wav"):
        waveform = self._sintetic_voice(text)
        self.save_waveform(waveform, output_path)
        return output_path
