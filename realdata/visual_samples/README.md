# Actual training data samples

The PNG sheets show real examples selected from split0 of the saved training manifests, not generated images, test predictions or camera captures. The sample ZIP includes10 original photographs and5 original speech WAV files, their labels/hashes and photo credits. The full datasets are not duplicated here.

The waveform and log-mel panels are calculated from the same WAV in each row using the experiment frontend. Colors use one fixed log-power scale. The down recording is assigned to the model label other; other also includes left/right/up in the original clips plus declared synthetic low-level training negatives. These examples do not demonstrate arbitrary-word rejection.

Dataset sources:
- Flowers: https://www.tensorflow.org/tutorials/load_data/images
- Full flower archive: https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz
- Speech: https://www.tensorflow.org/tutorials/audio/simple_audio
- Speech excerpt: https://storage.googleapis.com/download.tensorflow.org/data/mini_speech_commands.zip
- Speech Commands dataset: https://www.tensorflow.org/datasets/catalog/speech_commands

Preserve PHOTO_CREDITS.txt when sharing the flower samples. Speech Commands is distributed under CC BY4.0; preserve the dataset citation/license. These are public benchmark recordings, not the user's speech. Full datasets, saved manifests and original training scripts determine the actual experiment, not this small display selection.
