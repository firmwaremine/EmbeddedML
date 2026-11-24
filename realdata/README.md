# Real-data experiments and source data

This directory includes the actual dataset files used by the book, not only sample pictures or download scripts. It is intentionally large: 3,670 original flower JPGs and8,000 original speech WAVs, with original metadata/credits. DATA_SHA256SUMS records every delivered dataset byte. No macOS extraction metadata is included.

## Layout

- data/flower_photos: full3,670-photo dataset, with per-image photographer/source credits in LICENSE.txt. CC BY2.0, not the repository's code license.
- data/mini_speech_commands: full8,000-recording tutorial excerpt,8word folders. Speech Commands CC BY4.0; preserve dataset attribution below.
- audio/split_manifest.json: exact source clip paths, speaker IDs and training/validation/test assignment. Speaker-hash split,5384/1239/1377 original recordings.
- vision/split_manifest.json: exact photograph paths, hashes and training/validation/test assignment.2556/559/555 images. Identical file bytes stay together; near-duplicate/session independence is not guaranteed.
- audio and vision: original training/export/verification source, saved model artifacts, reports and reproducibility requirements.
- visual_samples: training-photo and waveform/log-mel sheets, recorded learning curves, held-out prediction examples, exact source manifests and photo credits.

Original photos are stored unchanged, not the model's96x96 crops. The speech source recordings are unchanged, not the augmented shifts/noise inputs. The training scripts document how source data becomes model input. Model normalization is fitted on training data only. All figures are explanatory samples, not a new evaluation panel.

## Attribution and separate rights

The root MIT license applies to original FirmwareMine code, not third-party images, recordings, pretrained model values or upstream SDK drivers. Preserve all third-party notices.

Flower source/individual credits: data/flower_photos/LICENSE.txt. Archive source: https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz . Archive SHA256:4c54ace7911aaffe13a365c34f650e71dd5bf1be0a58b464e5a7183e3e595d9c . Source guide: https://www.tensorflow.org/tutorials/load_data/images . CC BY2.0: https://creativecommons.org/licenses/by/2.0/ . Original photos unchanged. Display sheets/crops identify their transformations and credits.

Speech Commands by Pete Warden, Google. Citation: Speech Commands: A Dataset for Limited-Vocabulary Speech Recognition (2018), https://arxiv.org/abs/1804.03209 . Dataset catalog/license: https://www.tensorflow.org/datasets/catalog/speech_commands . CC BY4.0: https://creativecommons.org/licenses/by/4.0/ . Tutorial excerpt source: https://storage.googleapis.com/download.tensorflow.org/data/mini_speech_commands.zip . Archive SHA256:49650f2341b26d886b46b3f4fb8fed59e30300b17550f1ee4a768b3106cf93a0 . Original WAVs unchanged; derived shifts/features are described by the scripts and not misrepresented as original recordings.

MobileNetV3-Small IMAGENET1K_V1 backbone values are pretrained third-party assets obtained through torchvision, not trained from scratch by FirmwareMine. Saved full-model and C weight files contain these values plus the new head. Preserve TORCHVISION_LICENSE.txt and inspect upstream model/data terms for the intended use. Documentation: https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.mobilenet_v3_small.html . The original code license is not a blanket relicensing of pretrained values.

## Evidence boundaries

Flower:80.90% on555 held-out public photographs; strict C matches555/555 reference labels and all156 nodes within the recorded float tolerances. No camera accuracy or target execution result is implied.

Audio:82.93% aligned-clip development score; constructed stream55/80 target detections,25misses,27unmatched events. Earlier stream failures informed revision, so results remain development evidence, not an untouched final benchmark. Other covers down/left/right/up and declared synthetic low-level noise, not arbitrary unknown speech. Public-source training is not the user's own voice.

No physical Korvo replay, microphone accuracy, camera capture, target timing or power result has been measured in these artifacts. Cross-build evidence is separate from board execution.
