# FirmwareMine embedded ML examples

Version 1.1. Audited 24 November 2026. This directory contains development-workstation teaching experiments for the Korvo-only book. It is **not an ESP-IDF board project**. For board capture, flashing and debugging, open the separate `Korvo_Mic_Lab_1_Source_and_Prebuild.zip` project and follow Chapter 23. Do not search for an `esp32/` folder in this archive or try to flash these host executables.

## Start in VS Code

On a Linux development workstation, open this entire `examples` directory with File > Open Folder. Windows users should open it in a VS Code WSL Linux window, not a native PowerShell/CMD window. macOS/native Windows execution is not verified. The C builds use GCC-style flags and libm; the vision verifier expects a Linux `.so` shared library. Opening this ZIP on Windows is fine, but execution uses the stated Linux environment.

Prerequisites: Python 3.10+, GCC with C11 support, CMake 3.16+, CTest and NumPy 2.2.6. In VS Code use Python: Create Environment, select Venv and the installed Python, and select `neural/requirements.txt` when prompted. Then Python: Select Interpreter selects `.venv/bin/python`. The supplied tasks explicitly use that interpreter; no system-Python package installation is needed. The environment-creation UI and WSL installation are not tested by this package's host regression.

Choose Terminal > Run Task and a named `FirmwareMine: Chapter ...` task. Chapter 22 runs the full ordinary host regression without retraining. Chapter 4 retrains the baseline; Chapter 7 retrains the neural model; Chapters 10, 13 and 15 regenerate their own teaching models. Training/export rewrites files. Back up any changed experiment first, and export C headers/rebuild after training. The full regression uses the saved models and is the safest first check. Task commands are visible in `.vscode/tasks.json` for review.

ESP-IDF extension `espressif.esp-idf-extension` 2.3.0 and framework 5.3.6 belong to the separate Korvo board workspace. They are not the compiler/toolchain for this host-only examples folder. No C++ compiler, extra deployment platform, camera driver or physical sensor connection is required here.

## Scope and verification

The four retained CMake projects are `c_core/`, `applications/`, `perception/` and `systems/`. Run the matching named task, not a root-level CMake configure. Model JSON/header/data files are kept so readers can inspect and reproduce the exact supplied experiment without retraining. Reports and known-answer fixtures are deliberately retained as evidence, not runtime dependencies. Only one Markdown guide is shipped to avoid conflicting instructions.

The ordinary Linux acceptance suite was rerun from the cleaned package. It built all four projects, passed CTest where defined, checked scalar/neural/motion/audio/vision parity and policy/box/budget/release fixtures. The acceptance runner verifies 19 commands. All 14 supplied VS Code task command sequences were also executed in an isolated Linux copy, including the retraining tasks; no C++ headers were regenerated. This tests the commands, not the VS Code interface. Existing explicitly named sanitizer reports record earlier sanitizer runs; that separate sanitizer suite was not rerun as part of this audit. Synthetic accuracy is not field performance. Host execution is not Korvo execution. No physical timing, energy, speech detection, camera inference, MFCC, authenticated activation or on-device neural training is claimed.

Input contracts: the scalar CLI accepts 64 finite samples and EOF; neural mode accepts three standardized features. Motion accepts 64 XYZ triples; audio accepts 256 integer-valued signed-int16 samples. The teaching integer neural format is not LiteRT or ESP-DL. Libraries use caller-owned buffers/state; callers must respect lengths, lifetimes and serialization. Read API headers and chapter contracts before adapting them.

## Folder map

| Folder | Purpose |
|---|---|
| `.vscode/` | VS Code host experiment tasks. |
| `applications/` | Independent synthetic motion and audio-feature experiments. |
| `c_core/` | Pure-C scalar/neural inference and stream fixtures. |
| `data/` | Included synthetic scalar training/validation/test data. |
| `generated/` | Saved scalar model, golden windows and provenance. |
| `neural/` and `neural/generated/` | NumPy training/reference checks and saved neural artifacts. |
| `perception/` | Event policy, synthetic pixels, geometry and normal-reference experiments. |
| `systems/` | Bounded adaptation, budget/release fixtures and acceptance runner. |
| `tests/` | Independent baseline Python/C parity check. |
| `tools/` | Baseline generation, C export and row replay helpers. |

## Complete shipped-file map

Every file in the archive is listed below. Build directories, `.venv`, Python caches, logs and host executables are generated locally and are not shipped.

| File | Role and limits |
|---|---|
| `.vscode/tasks.json` | Named VS Code host tasks used by the book. Runs Python training/verification and CMake/CTest on the development workstation, never flashes a board. |
| `README.md` | This setup guide, complete shipped-file map, folder roles, scope and audit decisions. It is the only Markdown document retained. |
| `SHA256SUMS` | SHA-256 inventory of every other delivered file. Describes the ZIP bytes, not files after training or report regeneration. |
| `applications/CMakeLists.txt` | C11 host build for the independent motion/audio reference library and sensing_cli. |
| `applications/known_answers.json` | Representative motion/audio outputs saved by the verifier for readable replay inspection. |
| `applications/lab_cli.c` | Strict motion/audio test adapter: 192 XYZ values or 256 signed-int16-valued PCM samples, then EOF. |
| `applications/motion_model.h` | Generated C constants for the motion classifier; used by sensing.c. |
| `applications/motion_model.json` | Saved synthetic-motion normalization, centers, labels and input assumptions. |
| `applications/motion_train.py` | Generates synthetic XYZ patterns and trains/evaluates a separate motion model. Writes JSON, header and report. |
| `applications/motion_training_report.json` | Synthetic motion split/metric/provenance record. Not human-gesture measurements. |
| `applications/sensing.c` | XYZ-magnitude features, synthetic-motion nearest-center classifier and periodic-Hann log-power DFT reference. No device driver or MFCC. |
| `applications/sensing.h` | Motion and audio C API, input dimensions and result contracts. |
| `applications/verification.json` | Recorded motion/audio parity counts, numerical errors and tested cases. |
| `applications/verify.py` | Checks 1,080 synthetic XYZ windows, rotation/numeric faults and six audio fixtures against an independent NumPy FFT oracle. |
| `c_core/CMakeLists.txt` | Independent C11-only host build: static library, strict numeric CLI and CTest boundary executable. Configure this subfolder, not the examples root. |
| `c_core/centroid_sanitizer_verification.json` | Recorded centroid parity summary from the separately executed sanitizer-enabled host build. Not rerun by the ordinary acceptance task. |
| `c_core/centroid_verification.json` | Recorded ordinary host centroid parity and invalid-input summary. |
| `c_core/cli.c` | Strict text-input host test executable. Default: 64 finite samples. Neural mode: three standardized features. Invalid input exits 2. |
| `c_core/eml.c` | C implementations of scalar features, nearest-center inference, float neural inference, quantization and bounded integer arithmetic. |
| `c_core/eml.h` | Public C API and result types for features, centroid prediction, float neural prediction and integer teaching inference. |
| `c_core/expected_replay_outputs.json` | Saved readable expected results for the three replay windows; useful for inspection, not a second dataset. |
| `c_core/model_data.h` | Generated C constants for saved centroid and neural models, including the teaching integer weights/scales. Rebuild after export. |
| `c_core/neural_sanitizer_verification.json` | Recorded neural parity summary from the separately executed sanitizer-enabled host build. Not board evidence. |
| `c_core/neural_verification.json` | Recorded ordinary host float/integer neural parity, boundary and invalid-input summary. |
| `c_core/replay_data.h` | Generated C array of the three scalar golden windows. It is a fixture, not live sensor data. |
| `c_core/stream.c` | Window/hop assembly with sequence/timestamp/invalid-sample recovery. No ISR synchronization or physical driver. |
| `c_core/stream.h` | Caller-owned single-threaded window assembler API, state and explicit continuity rules. |
| `c_core/stream_test.c` | C known-answer and invalid-input checks for numeric boundaries, stream windows and discontinuities. |
| `data/windows.csv` | Included synthetic scalar-waveform dataset: session/window/label/split plus 64 samples. Not microphone recordings or field data. |
| `generated/golden.json` | Three selected held-out raw windows with Python features, distances and predicted labels. Source for replay_data.h. |
| `generated/model.json` | Saved nearest-centroid model: training-only normalization, class centers and label order. |
| `generated/training_report.json` | Saved baseline generator provenance, split metrics and model hash. Synthetic performance only. |
| `neural/generated/neural_model.json` | Saved float neural weights, biases, preprocessing and custom integer-format parameters. Not LiteRT or ESP-DL format. |
| `neural/generated/training_report.json` | Neural seed, environment, loss history/selection, synthetic metrics and saved model hash. |
| `neural/requirements.txt` | Pinned NumPy 2.2.6 requirement for neural training and the neural/audio reference checks. |
| `neural/train_neural.py` | NumPy trainer for the 3-8-3 ReLU model, training-only normalization and power-of-two integer teaching parameters. Writes JSON model/report, not a firmware image. |
| `neural/verify.py` | Python reference versus C CLI checks across 720 windows, exact integer logits and float tolerances; also tests malformed inputs and quantizer boundaries. |
| `perception/CMakeLists.txt` | C11 static/shared perception libraries plus boundary-test and policy-trace executables. |
| `perception/anomaly_model.json` | Saved synthetic normal-reference means/scales/threshold and evaluation results; separate from the C known-answer fixture. |
| `perception/anomaly_train.py` | Independent synthetic normal-reference experiment with validation-selected nearest-rank threshold. Does not automatically wire its JSON into firmware. |
| `perception/box_report.json` | Saved exact box/NMS fixture results. |
| `perception/boxes.py` | Half-open box geometry, IoU and class-aware deterministic NMS tests. No object detector. |
| `perception/evaluate_events.py` | Checks policy_trace event times and computes illustrative false-event/exposure results. |
| `perception/known_answers.json` | Saved representative vision features/classes/distances for inspection. |
| `perception/perception.c` | Bounded policy state, explicit-stride RGB888 nearest-neighbor stretch, regional features, synthetic classifier and anomaly arithmetic. No speech/detector model. |
| `perception/perception.h` | C APIs for score-event policy, RGB resizing/features/classification and diagonal anomaly scoring. |
| `perception/policy_report.json` | Saved fabricated-trace event/exposure metrics. Not keyword detection performance. |
| `perception/policy_trace.c` | Runs an exact fabricated score trace through the event gate. Not microphone output. |
| `perception/unit.c` | C boundary/known-answer tests for policy, pixels and anomaly arithmetic. |
| `perception/verification.json` | Recorded Python/C image and resize parity summary. |
| `perception/verify.py` | ctypes Python/C parity for synthetic images and six byte-exact resize fixtures; loads the ordinary Linux shared library. |
| `perception/vision_model.h` | Generated C vision parameters used by perception.c. |
| `perception/vision_model.json` | Saved regional-color synthetic model and label order. |
| `perception/vision_train.py` | Generates 900 synthetic RGB patterns and trains/evaluates the six-feature nearest-center vision model. |
| `perception/vision_training_report.json` | Synthetic image-session split and model metrics; no camera accuracy claim. |
| `systems/CMakeLists.txt` | C11 bounded-prototype library and its CTest executable. |
| `systems/acceptance_report.json` | Result of the acceptance runner executed for this audited package. Records host/Python/scope and successful-command count. |
| `systems/bounded.c` | Restricted in-memory prototype update with a fixed reference radius, update cap and rollback. No neural fine-tuning or durable flash transaction. |
| `systems/bounded.h` | Public bounded-prototype state/update/rollback API and limits. |
| `systems/budget.py` | Exact illustrative memory, scheduling, duty-cycle/charge arithmetic with invented inputs, not measured board data. |
| `systems/budget_report.json` | Saved budget/queue/energy example outputs and scope labels. |
| `systems/release_gate.py` | Offline model hash/shape/label/revision compatibility fixtures. Writes manifest/report; never activates or flashes firmware. |
| `systems/release_manifest.json` | Saved teaching manifest referencing the neural JSON and its hash. Explicitly has no verified signature. |
| `systems/release_report.json` | One accepted fixture and seven rejected tamper/incompatibility cases. Hash checks are not authentication. |
| `systems/run_all.py` | Ordinary Linux host acceptance runner: four independent C builds, CTests and parity/fixture scripts, 19 checked commands, temporary build directories. |
| `systems/unit.c` | Known-answer/rejection tests for bounded adaptation and rollback. |
| `tests/verify.py` | Baseline Python versus C CLI parity on all 720 saved windows plus malformed-input tests. |
| `tools/export_c.py` | Exports C headers from the saved baseline/neural JSON models and golden windows. Does not retrain. |
| `tools/train.py` | Standard-library baseline synthetic generator/trainer. Rewrites dataset, baseline model, golden windows and training report. |
| `tools/window_to_stdin.py` | Prints a chosen CSV row as raw numeric CLI input. Used by the Chapter 4/5 replay tasks. |

## Audit decisions

Removed the root mixed-language CMake project, all C++ source/header/test adapters, historical C++ guide, obsolete compatibility note and three small module READMEs whose useful contracts are consolidated above and in the file map. Removed duplicated C++ verification reports and captured training stdout. Trainers no longer emit unused C++ headers. The separate C-only CMake projects and their C/Python dependencies remain. The redundant Chapter 5 task remains as the same core replay check because it is a harmless book-facing shortcut, not another target.

The retained reports are optional for running the code but necessary for inspecting the saved experiment and its evidence. The included CSV/model/header/fixture files are intentional: removing them would force retraining or break parity/export/release examples. There is no obsolete hardware adapter hidden among them.

Removed files from the previous package:

- `CMakeLists.txt`
- `COMPATIBILITY.md`
- `README_HISTORICAL_CPP.md`
- `applications/README.md`
- `common/classifier.hpp`
- `common/window_stream.hpp`
- `generated/host_verification.json`
- `generated/model.hpp`
- `generated/replay.hpp`
- `generated/sanitizer_verification.json`
- `generated/training_stdout.json`
- `linux/main.cpp`
- `neural/classifier.hpp`
- `neural/generated/host_verification.json`
- `neural/generated/neural_model.hpp`
- `neural/generated/sanitizer_verification.json`
- `neural/main.cpp`
- `perception/README.md`
- `systems/README.md`
- `tests/stream.cpp`
- `tests/unit.cpp`

## Integrity and regenerated outputs

`SHA256SUMS` covers every shipped file except itself. Retraining, export and checks that save reports intentionally change bytes, so the delivered manifest is no longer expected to match after those operations. The acceptance runner uses temporary build directories, but writes `systems/acceptance_report.json` and some report/manifest files. Python may create `__pycache__` locally. These generated files are not additional shipped dependencies.
