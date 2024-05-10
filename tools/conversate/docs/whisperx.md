WhisperX

GitHub stars GitHub issues GitHub license ArXiv paper Twitter

whisperx-arch

This repository provides fast automatic speech recognition (70x realtime with large-v2) with word-level timestamps and speaker diarization.

    ⚡️ Batched inference for 70x realtime transcription using whisper large-v2
    🪶 faster-whisper backend, requires <8GB gpu memory for large-v2 with beam_size=5
    🎯 Accurate word-level timestamps using wav2vec2 alignment
    👯‍♂️ Multispeaker ASR using speaker diarization from pyannote-audio (speaker ID labels)
    🗣️ VAD preprocessing, reduces hallucination & batching with no WER degradation

Whisper is an ASR model developed by OpenAI, trained on a large dataset of diverse audio. Whilst it does produces highly accurate transcriptions, the corresponding timestamps are at the utterance-level, not per word, and can be inaccurate by several seconds. OpenAI's whisper does not natively support batching.

Phoneme-Based ASR A suite of models finetuned to recognise the smallest unit of speech distinguishing one word from another, e.g. the element p in "tap". A popular example model is wav2vec2.0.

Forced Alignment refers to the process by which orthographic transcriptions are aligned to audio recordings to automatically generate phone level segmentation.

Voice Activity Detection (VAD) is the detection of the presence or absence of human speech.

Speaker Diarization is the process of partitioning an audio stream containing human speech into homogeneous segments according to the identity of each speaker.
New🚨

    1st place at Ego4d transcription challenge 🏆
    WhisperX accepted at INTERSPEECH 2023
    v3 transcript segment-per-sentence: using nltk sent_tokenize for better subtitlting & better diarization
    v3 released, 70x speed-up open-sourced. Using batched whisper with faster-whisper backend!
    v2 released, code cleanup, imports whisper library VAD filtering is now turned on by default, as in the paper.
    Paper drop🎓👨‍🏫! Please see our ArxiV preprint for benchmarking and details of WhisperX. We also introduce more efficient batch inference resulting in large-v2 with *60-70x REAL TIME speed.

Setup ⚙️
Tested for PyTorch 2.0, Python 3.10 (use other versions at your own risk!)

GPU execution requires the NVIDIA libraries cuBLAS 11.x and cuDNN 8.x to be installed on the system. Please refer to the CTranslate2 documentation.
1. Create Python3.10 environment

conda create --name whisperx python=3.10

conda activate whisperx
2. Install PyTorch, e.g. for Linux and Windows CUDA11.8:

conda install pytorch==2.0.0 torchaudio==2.0.0 pytorch-cuda=11.8 -c pytorch -c nvidia

for non-nvidia (cpu only):
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

See other methods here.
3. Install this repo

pip install git+https://github.com/m-bain/whisperx.git

If already installed, update package to most recent commit

pip install git+https://github.com/m-bain/whisperx.git --upgrade

If wishing to modify this package, clone and install in editable mode:

$ git clone https://github.com/m-bain/whisperX.git
$ cd whisperX
$ pip install -e .

You may also need to install ffmpeg, rust etc. Follow openAI instructions here https://github.com/openai/whisper#setup.
Speaker Diarization

To enable Speaker Diarization, include your Hugging Face access token (read) that you can generate from Here after the --hf_token argument and accept the user agreement for the following models: Segmentation and Speaker-Diarization-3.1 (if you choose to use Speaker-Diarization 2.x, follow requirements here instead.)

    Note
    As of Oct 11, 2023, there is a known issue regarding slow performance with pyannote/Speaker-Diarization-3.0 in whisperX. It is due to dependency conflicts between faster-whisper and pyannote-audio 3.0.0. Please see this issue for more details and potential workarounds.

Usage 💬 (command line)
English

Run whisper on example segment (using default params, whisper small) add --highlight_words True to visualise word timings in the .srt file.

whisperx examples/sample01.wav

Result using WhisperX with forced alignment to wav2vec2.0 large:
sample01.mp4

Compare this to original whisper out the box, where many transcriptions are out of sync:
sample_whisper_og.mov

For increased timestamp accuracy, at the cost of higher gpu mem, use bigger models (bigger alignment model not found to be that helpful, see paper) e.g.

whisperx examples/sample01.wav --model large-v2 --align_model WAV2VEC2_ASR_LARGE_LV60K_960H --batch_size 4

To label the transcript with speaker ID's (set number of speakers if known e.g. --min_speakers 2 --max_speakers 2):

whisperx examples/sample01.wav --model large-v2 --diarize --highlight_words True

To run on CPU instead of GPU (and for running on Mac OS X):

whisperx examples/sample01.wav --compute_type int8

Other languages

The phoneme ASR alignment model is language-specific, for tested languages these models are automatically picked from torchaudio pipelines or huggingface. Just pass in the --language code, and use the whisper --model large.

Currently default models provided for {en, fr, de, es, it, ja, zh, nl, uk, pt}. If the detected language is not in this list, you need to find a phoneme-based ASR model from huggingface model hub and test it on your data.
E.g. German

whisperx --model large-v2 --language de examples/sample_de_01.wav

sample_de_01_vis.mov

See more examples in other languages here.
Python usage 🐍

import whisperx
import gc 

device = "cuda" 
audio_file = "audio.mp3"
batch_size = 16 # reduce if low on GPU mem
compute_type = "float16" # change to "int8" if low on GPU mem (may reduce accuracy)

# 1. Transcribe with original whisper (batched)
model = whisperx.load_model("large-v2", device, compute_type=compute_type)

# save model to local path (optional)
# model_dir = "/path/"
# model = whisperx.load_model("large-v2", device, compute_type=compute_type, download_root=model_dir)

audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=batch_size)
print(result["segments"]) # before alignment

# delete model if low on GPU resources
# import gc; gc.collect(); torch.cuda.empty_cache(); del model

# 2. Align whisper output
model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)

print(result["segments"]) # after alignment

# delete model if low on GPU resources
# import gc; gc.collect(); torch.cuda.empty_cache(); del model_a

# 3. Assign speaker labels
diarize_model = whisperx.DiarizationPipeline(use_auth_token=YOUR_HF_TOKEN, device=device)

# add min/max number of speakers if known
diarize_segments = diarize_model(audio)
# diarize_model(audio, min_speakers=min_speakers, max_speakers=max_speakers)

result = whisperx.assign_word_speakers(diarize_segments, result)
print(diarize_segments)
print(result["segments"]) # segments are now assigned speaker IDs

Demos 🚀

Replicate (large-v3 Replicate (large-v2 Replicate (medium)

If you don't have access to your own GPUs, use the links above to try out WhisperX.
Technical Details 👷‍♂️

For specific details on the batching and alignment, the effect of VAD, as well as the chosen alignment model, see the preprint paper.

To reduce GPU memory requirements, try any of the following (2. & 3. can affect quality):

    reduce batch size, e.g. --batch_size 4
    use a smaller ASR model --model base
    Use lighter compute type --compute_type int8

