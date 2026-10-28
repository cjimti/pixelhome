"""Speak lines in a cloned voice with Chatterbox. Runs in its own venv (scripts/audio-setup.sh), called by
`python -m pixelhome intro`: argv is a JSON list of {text, ref, out, seed, exaggeration, cfg}."""
import json, sys
import torch, torchaudio
from chatterbox.tts import ChatterboxTTS

jobs = json.loads(sys.argv[1])
model = ChatterboxTTS.from_pretrained(device='mps' if torch.backends.mps.is_available() else 'cpu')
for j in jobs:
    torch.manual_seed(j['seed'])
    wav = model.generate(j['text'], audio_prompt_path=j['ref'], exaggeration=j['exaggeration'], cfg_weight=j['cfg'])
    torchaudio.save(j['out'], wav.cpu(), model.sr)
    print(j['out'], flush=True)
