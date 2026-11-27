# Korvo recorded-speech experiment, run guide

This is a research build, not a finished voice-control product. Use the previously verified modified ESP32-S3-Korvo-2 V3.1 native-USB connection. The speaker amplifier stays disabled. No further wiring change is required or recommended. The application is pure C on ESP-IDF 5.3.6 with esp_codec_dev 1.6.2. The SDK has mixed-language internals; there is no C++ model engine.

## What is actually ready

- A model trained on real public speech recordings, not synthetic speech.
- Four target words: go, no, stop, yes. The fifth label, other, includes down, left, right and up from this subset plus the declared synthetic training-noise examples. It does NOT establish rejection of arbitrary speech, music or noise.
- A speaker-disjoint custom split: 5,384 training, 1,239 validation and 1,377 test clips.
- Test clip accuracy: 82.93%. Pure C and the training implementation agree on all 1,377 test labels. These are computer results, not measurements on your board.
- A cross-built microphone-to-model application with an embedded recorded-clip replay check, per-stage timing, memory and overflow logging.

## Before flashing

Flashing replaces the application on the board. Save anything you need from its current firmware first. Confirm the board revision on the PCB. Do not use a battery or modify USB wiring for this first run. Use the already modified native-USB connection from the earlier lab. This pack does not instruct any new soldering or pin changes. Keep the original board connection documentation available.

## VS Code workflow

1. Open the `korvo_kws` folder as the workspace, not its `main` subfolder.
2. Use the official Espressif ESP-IDF extension, version 2.3.0, as selected for this book. Configure ESP-IDF 5.3.6 through the extension's setup workflow.
3. Check the workspace settings: build folder `build-usb`, sdkconfig `sdkconfig.usb`, defaults `sdkconfig.usb.defaults`. The delivered workspace is configured for the modified native-USB/JTAG console.
4. Use the extension command **ESP-IDF: Set Espressif Device Target**, choose ESP32-S3. Choose the native USB Serial/JTAG serial port through **ESP-IDF: Select Port to Use**.
5. Use **ESP-IDF: Build Your Project**. Read the output and stop if there is an error. The delivered build was cross-compiled and has run in short practice runs on one board (replay passed, microphone capture, no overflow). The formal trial has not been recorded.
6. When you are ready to replace the current board application, use **ESP-IDF: Flash Your Project**. Then open **ESP-IDF: Monitor Your Device**. Do not erase the entire flash as a routine troubleshooting step.
7. Save the full monitor output to a text file. If your extension's monitor does not offer a save control, copy its full terminal text into `run-01.txt`; do not keep only a screenshot of the final line.

## First gate: replay and capture health

The boot log should include `REPLAY`, a label, logit error, duration and `PASS=1`. This runs an actual held-out recorded clip embedded in flash. It checks target arithmetic without relying on room sound. If it reports `PASS=0`, stop. Save the complete log and build version. Do not loosen the tolerance simply to make the check green.

Next look for the capture-format line: 16 kHz, stereo, signed 16-bit, with MIC1/MIC2 and gain 24 dB. The model currently reads the first slot only. Speak at normal volume and observe the RMS/clip summaries. Hardware channel order and level must be confirmed by this run. Do not assume an empty result means your pronunciation is wrong.

Save at least 60 seconds of idle-room logs before scoring recognition. Check read errors, short reads and overflow counts. Context resets after a stream fault. Repeated overflow means the experiment is not keeping up; it is not a valid accuracy run. The double-precision reference FFT was chosen for numerical agreement, not proven MCU speed. Its timing must be measured here before choosing an optimized replacement.

## What the KWS log means

- `label`: highest-scoring class, not a verified fact.
- `confidence`: softmax score, not a calibrated probability.
- `rms`: normalized audio level for the one-second input.
- `front_us`: log-mel feature computation duration.
- `infer_us`: neural inference duration only.
- `event=1`: the experimental policy emitted an event.
- `heap`: free internal heap in bytes at that log point.
- `stack`: task stack high-water value reported by ESP-IDF on this target, in bytes.

The model sees a 1-second context. A new context is evaluated after at least 1,600 new samples, nominally 100 milliseconds (block boundaries can add up to one capture block). These durations are part of response delay, not included in `infer_us`. Do not describe inference duration alone as microphone-to-action latency.

The policy requires one target prediction, softmax at least 0.90, RMS at least 0.005, a one-second quiet interval after an event and three noncandidate evaluations to release its latch. These are declared starting values, not validated settings. The previous two-hit policy missed most words in a constructed host stream and was replaced after validation. Record misses honestly before deciding whether to change the policy.

## Recognition trial, after capture health passes

Use `measurements/trials.csv`. Do not tune settings on the final test session.

1. Make a short validation run first to check levels and decide whether the starting policy is usable. Save it separately.
2. Freeze the model, gain, thresholds, distance and room setup.
3. For a new test session, say each of go/no/stop/yes 20 times in a shuffled order, with at least 3 seconds between attempts. Record the intended word, trial onset and corresponding event label/time, including misses and duplicates. More speakers and a separate day give stronger evidence than repetitions from one person.
4. Record negative exposure separately: quiet room, unrelated speech, the other dataset words and ordinary sounds. Obtain consent from anyone recorded. Do not send private raw audio unless they agree.
5. Report counts per target, correct events, wrong events, misses, duplicates and false events per negative hour. Do not call a short quiet-room trial a general accuracy benchmark.
6. Event latency requires word onset/end timestamps on the same timebase as the device log. Without synchronized timestamps, report feature/inference timings only and mark event latency unmeasured.

## Electrical power, only with suitable equipment

Firmware cannot measure supply power by itself. If you have a suitable inline USB meter or current analyzer, record instrument model, sample rate, supply voltage and measurement boundary. A slow USB display may support only an average, not inference peaks.

Keep the same native-USB connection and logging setup for comparable runs. Measure the full powered board for a quiet interval and a spoken-command interval, recording duration and average voltage/current. Report power as voltage × current only when those averages support that estimate; for time-varying traces integrate instantaneous power. Do not add separate CPU/radio figures to a whole-board reading. Do not open power rails, bridge jumpers or attach a battery for this step. If no instrument is available, mark power unmeasured, not zero.

## Return these files

- Full boot and run log, including REPLAY and capture counters.
- Completed trial sheet and negative-exposure duration.
- Board revision, USB port/profile, SDK/extension version, model hash, gain, room/distance and speaker count.
- Power instrument notes/trace only if actually measured.

The book can include the real results after these files are checked. A successful flash or a photograph of the board is not an accuracy, timing or power measurement.

## Current limitations and model revision

Training augmentation now shifts recordings from training speakers and adds 1,500 synthetic low-level-noise negatives. Those negatives are explicitly synthetic; speech clips remain real. The fixed 160-clip constructed stream gives 55 correct target events out of 80, 25 misses and 27 unmatched events. It is a development diagnostic, not an untouched final continuous-speech benchmark: an earlier version of that test panel revealed the alignment problem and influenced this revision. The current threshold was chosen on separate validation speakers. A new naturally recorded test is still required. Do not deploy this as a reliable voice controller.
