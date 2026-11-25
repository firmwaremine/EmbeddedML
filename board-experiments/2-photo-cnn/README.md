# Real photographs, transfer learning and strict-C inference

This companion extends the host flower experiment with an original C11 implementation of the actual MobileNetV3-Small feature extractor and trained five-class head. It is a fixed-graph teaching reference, not a general model importer or optimized production engine.

## Evidence

- 555 held-out flower photographs, 80.90% classification accuracy.
- C and PyTorch labels agree on 555/555.
- All 156 intermediate nodes checked on all 555 images. Largest absolute intermediate error: 0.000322581. Final-logit error: 0.000046492.
- 405,504-byte static activation arena and 3,719,572-byte float weights. Counts exclude image input, camera/decoder buffers, stacks and SDK memory.
- Strict GCC C11 warnings pass. A recorded-input replay passes AddressSanitizer and UndefinedBehaviorSanitizer. That is one replay, not a full-dataset sanitizer claim.
- ESP-IDF 5.3.6 ESP32-S3 cross-build succeeds. App image is 4,023,984 bytes. No board execution, target latency, live camera accuracy or power evidence exists yet.

## VS Code host workflow

Use the official Microsoft Python extension in a Linux/WSL environment for the Python experiments and a GCC toolchain for host C. Keep the IDF extension workflow in a separate project window. Create/select a Python environment with the pinned requirements. The flower photographs are in the repository at ../realdata/data/flower_photos (relative to this folder); the scripts read them from there. The split manifest checks the intended image identities. Run train_transfer.py only to retrain; it overwrites artifacts. export_c.py regenerates the C graph/weights from flower_model.pt. The host tasks below compile and verify the delivered artifacts without retraining.

Open this folder in VS Code. Terminal > Run Task > FirmwareMine: C vision parity compiles the shared library and runs all-image/all-node comparisons. This requires the dataset and pinned Python dependencies. The sanitized replay task needs only GCC and the included replay tensor. Host timings include observer overhead and must not be quoted as device timings.

## Board workflow

Open korvo_vision as its own VS Code folder. Read RUN_ON_BOARD.md before flashing. This replay does not initialize a camera. The user's JQ-V360-F100 V3 marking/photo has not established its sensor ID, voltage or contact map. Do not connect an unknown flex by appearance or use an unrelated ESP32-CAM pin map.

## Provenance and rights

Original project code is provided as FirmwareMine teaching material. MobileNetV3-Small IMAGENET1K_V1 parameters are third-party pretrained assets obtained through torchvision, not original FirmwareMine weights. flower_model.pt and c_vision/weights.f32 contain these pretrained values plus the newly trained head. TORCHVISION_LICENSE.txt preserves the installed distribution's BSD notice; this does not warrant separate training-data/model rights for every downstream purpose. Check the upstream terms and intended use before further redistribution or commercial use. Do not describe these weights as newly trained from scratch.

The flower photographs are not in this folder; the repository keeps them in ../realdata. FLOWER_ATTRIBUTION.txt preserves their CC BY 2.0 credits. The included first-image replay tensor is a transformed image representation; preserve its attribution as well as the full list.

Sources:
- https://www.tensorflow.org/tutorials/load_data/images
- https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.mobilenet_v3_small.html
- https://github.com/pytorch/vision/blob/main/LICENSE
- https://www.espressif.com/en/dev-board/esp32-s3-korvo-2-en
- https://docs.espressif.com/projects/esp-adf/en/latest/multimedia-boards/dev-boards/user-guide-esp32-s3-korvo-2.html
