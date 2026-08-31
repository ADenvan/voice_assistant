import asyncio
import logging

import numpy as np
import sounddevice as sd
from scipy.signal import resample as scipy_resample

from src.core.config import Config

logger = logging.getLogger("voice_ai.audio.output")