# Step by step: run the Korvo experiments

Follow the parts in order. Each part has the same shape: **open, check, build, flash, run, expected output, save, stop if**. Quoted log lines show the format the firmware prints. Numbers in them (times, errors, bytes) will differ on your board; those are exactly what you are measuring.

Nothing here has run on a board yet. Your logs are the first evidence.

## Part 0. One-time setup

### 0.1 Get the code

1. Open VS Code.
2. Press `Ctrl+Shift+P` (macOS `Cmd+Shift+P`) and run **Git: Clone**.
3. Paste `https://github.com/firmwaremine/EmbeddedML.git`, choose a folder, and open the clone.
4. Stay on the default branch, `main`. It already has everything in `board-experiments/`, so no branch switch is needed.
5. You only need the `board-experiments/` folder. The `realdata/` folder is 485 MB of training data. For a lighter clone, use **Code > Download ZIP** on the repository page and unzip only `board-experiments/`.

### 0.2 Install ESP-IDF in VS Code

1. Open the Extensions view (`Ctrl+Shift+X`). Search for **Espressif IDF** and install **ESP-IDF** by Espressif Systems, version 2.3.0.
2. Press `Ctrl+Shift+P` and run **ESP-IDF: Configure ESP-IDF Extension**.
3. Choose **Express** setup, pick ESP-IDF version **5.3.6**, accept the default install folders, and wait for the tools to download. It takes a while.
4. When it says setup is complete, restart VS Code.
5. Check: the bottom status bar shows the ESP-IDF version and icons for Build, Flash and Monitor.

### 0.3 Check the board before you flash anything

1. Read the revision printed on the PCB. It must be ESP32-S3-Korvo-2 **V3.1**.
2. Keep the board on the native-USB connection you already modified. No battery, no speaker, no new wiring.
3. Connect the board to the PC over that USB connection.
4. In VS Code run **ESP-IDF: Select Port to Use** and choose the native USB Serial/JTAG port. If no port appears, try another cable (it must carry data) and tell me what the OS shows.
5. Run **ESP-IDF: Set Espressif Device Target** and choose **esp32s3** (choose "ESP32-S3 chip (via builtin USB-JTAG)" if offered).
6. Open **ESP-IDF: Open ESP-IDF Terminal** and run:

   ```
   esptool.py --port <your port> flash_id
   ```

   Use the port name from step 4, for example `COM5` or `/dev/ttyACM0`.
7. Expected output includes a flash size line such as `Detected flash size: 16MB`. Save the whole output as `flash-id.txt`.
8. **Stop if** the flash size is below 8 MB, or you cannot tell whether the PSRAM is octal. Send me `flash-id.txt` and do not flash.
9. Save anything you need from the current firmware. Each flash below replaces the application and partition table. Never use **Erase Flash**. Never change eFuses.

### 0.4 How to save a full log

1. Run **ESP-IDF: Monitor Your Device**.
2. After the run, select all of the terminal text (`Ctrl+A` inside the terminal) and copy it into a new text file, or use the monitor's log-to-file option if your version offers one.
3. Save as the file name given in each part. A screenshot of the last line is not enough.

---

## Part 1. Speech: `1-speech/korvo_kws`

**Goal:** show that the board hears a spoken word, turns it into features, runs the network and prints an event.

### 1.1 Open and check

1. **File > Open Folder** and choose `board-experiments/1-speech/korvo_kws`. Open that folder itself, not `main`.
2. Open `.vscode/settings.json`. It must point to build folder `build-usb`, sdkconfig `sdkconfig.usb` and defaults `sdkconfig.usb.defaults`. These are already set. Do not change them.
3. Select the port and device target as in 0.3.

### 1.2 Build

1. Run **ESP-IDF: Build Your Project**.
2. Expected: the output ends with the app size, about 623,744 bytes, and no error lines.
3. **Stop if** the build fails. Send me the full build output.

### 1.3 Flash and monitor

1. Run **ESP-IDF: Flash Your Project**. Choose UART flashing if asked. This replaces the current application.
2. Run **ESP-IDF: Monitor Your Device**. Press the board's reset button if the boot log has already scrolled past.

### 1.4 Gate 1: the replay check

1. Find a line like this in the boot log:

   ```
   REPLAY label=<word> logit_error=0.0000xxx duration_us=<number> PASS=1
   ```

2. `PASS=1` means a real held-out recording stored in flash gives the same answer as the computer. It does not need any sound from you.
3. **Stop if** it says `PASS=0` or prints `feature self-test FAILED`. Save the full log. Do not change any tolerance.

### 1.5 Gate 2: the microphone works

1. Find the capture line. It reports 16000 Hz, stereo, 16-bit, MIC1/MIC2 and gain 24 dB.
2. Stay silent for at least 60 seconds. Count `GAP overflow=` warnings. The right number is zero. The log line `blocks=... ovf=... skipped=...` also prints `skipped`, the count of one-second windows the inference task could not start because it was still busy. It should stay at or near zero.
3. Speak at normal volume near the board. You should see `KWS` lines with a changing `rms` value:

   ```
   KWS t_ms=... label=<word> confidence=0.xxxx rms=0.0xxxxx front_us=... infer_us=... event=0 heap=... stack=...
   ```

4. Expected: `rms` rises when you speak and falls when you stop.
5. **Stop if** you see repeated `GAP overflow` warnings. The firmware is not keeping up and an accuracy run would be invalid. Save the log.

### 1.6 What the log fields mean

| Field | Meaning |
| --- | --- |
| `label` | Highest-scoring class. Not a verified fact. |
| `confidence` | Softmax score. Not a calibrated probability. |
| `rms` | Normalised loudness of the one-second input. |
| `front_us` | Time to compute the log-mel features. |
| `infer_us` | Time for the neural network only. This is not microphone-to-action latency. |
| `event=1` | The experimental policy decided a target word was said. |
| `heap` | Free internal heap, bytes. |
| `stack` | Task stack high-water mark, bytes. |

An event needs: a target word prediction, confidence of at least 0.90, `rms` of at least 0.005, a quiet second after the previous event, and three non-target evaluations to re-arm. These are starting values, not tuned settings.

### 1.7 The trial

Do this only after 1.4 and 1.5 pass.

1. Make a short practice run first to check levels. Save it as `run-validation.txt`. Do not use it as the final result.
2. Freeze everything: gain, distance to the board, room, thresholds.
3. Open `measurements/trials.csv`. It has the columns `session, trial, intended_word, onset_device_ms_if_synced, event_device_ms, event_label, miss, duplicate, notes`.
4. Start a new monitor log. Say each of **go, no, stop, yes** 20 times, in a shuffled order, at least 3 seconds apart. Write down your order as you go.
5. For each trial, record the intended word and what the log printed, including misses (`miss=1`) and duplicates (`duplicate=1`).
6. Run a separate negative session: quiet room, other people talking, the words down/left/right/up, ordinary noise. Note its length in minutes. Get consent from anyone you record.
7. Save the logs as `run-01.txt` (and the negative run as `run-negative.txt`) plus the completed `trials.csv`.
8. Also write down: board revision, USB port, SDK and extension versions, gain, distance, room, number of speakers.

Event latency needs word start times on the same clock as the device log. Without that, report feature and inference times only.

### 1.8 Known limits

- Four target words only. The fifth label `other` holds down/left/right/up and declared synthetic noise. It does not prove the model rejects any other speech, music or noise.
- On a constructed 160-clip stream the policy found 55 of 80 targets with 25 misses and 27 unmatched events. That stream shaped the design, so it is a development check. Do not treat this build as a reliable voice controller.

---

## Part 2. Photo CNN replay: `2-photo-cnn/korvo_vision`

**Goal:** show that a convolutional network written in pure C gives the same answer on the board as on the computer. No camera is used.

### 2.1 Open and check

1. **File > Open Folder** and choose `board-experiments/2-photo-cnn/korvo_vision`.
2. Check `partitions.csv`: one 7 MiB factory app, no OTA.
3. Check the flash and PSRAM as in 0.3.
4. Select the port and the esp32s3 target.

### 2.2 Build, flash, monitor

1. Run **ESP-IDF: Build Your Project**. Expected app size: about 4,023,984 bytes. It needs the 7 MiB partition.
2. Run **ESP-IDF: Flash Your Project**, then **ESP-IDF: Monitor Your Device**.
3. The run is slow on purpose. Wait until you see the final line.

### 2.3 Expected output

```
Recorded-input replay only. Camera, LCD, microphone and speaker are NOT initialized. Task watchdog is disabled for this slow diagnostic.
PSRAM_BYTES=<about 8 million>
TRIAL=0 label=<class> expected=<class> logit_error=0.00000xx duration_us=<number> free_internal=... free_psram=... stack_watermark_bytes=... PASS=1
TRIAL=1 ...
TRIAL=2 ...
LOGITS <five numbers>
Replay finished. No target benchmark is established until these logs are captured on the physical board.
```

1. `PASS=1` needs the expected class and a final-logit error below 0.01.
2. The three trials show whether time and memory are stable.
3. The task watchdog is off here because the float reference is slow. That is a diagnostic choice, not a production setting.
4. **Stop if** PSRAM fails to start, the arena allocation fails or any `PASS=0` appears. Save the full log and the module label. Do not edit the code to force a pass.

### 2.4 Send back

The full boot log, saved as `cnn-replay.txt`, and the module label or `flash-id.txt`.

### 2.5 Run the computer-side check (optional)

This needs Linux or WSL, Python 3.10 or later, a C compiler, and the flower photos in `realdata/data/flower_photos`.

1. Open `board-experiments/2-photo-cnn` in VS Code.
2. Create a Python environment and run `pip install -r requirements.txt`.
3. Run **Terminal > Run Task > FirmwareMine: C vision parity**. Expected: 555 of 555 labels agree, and the largest output error is about 0.0000465.
4. `train_transfer.py` retrains the model and overwrites the saved files. Only run it if you want to retrain.

### 2.6 Known limits

- Computer result: 80.90% on 555 held-out photos. 156 graph nodes match PyTorch on all of them.
- Preprocessing on the computer uses Pillow. The C camera preprocessing does not exist yet. Do not claim camera accuracy.
- The weights are third-party pretrained values plus a newly trained head. They are not trained from scratch.

---

## Part 3. Camera health: `3-camera-health/korvo_camera_health`

**Goal:** identify the camera sensor and save one real frame. No network and no CNN.

### 3.1 Install the camera (power off)

1. Unplug USB. Make sure nothing else powers the board.
2. Find the 24-contact camera connector. It is not the 20-contact LCD connector.
3. Insert only the supplied camera, in its original orientation. Do not force it, hot-plug it, trim it, reverse it or rewire it.
4. **Stop if** you are not sure how it goes in. Take a photo of the socket and the flex contacts and send it to me. Do not guess.
5. Reconnect USB.

Board side camera bus, for reference: D0 to D7 are GPIO 13, 47, 14, 3, 12, 42, 41, 39. VSYNC 21, HREF 38, PCLK 11, XCLK 40 at 20 MHz, SCCB on 17 and 18. Reset and power-down are not used. GPIO48 keeps the speaker amplifier off. No IO-expander output is changed.

### 3.2 Build, flash, monitor

1. **File > Open Folder** and choose `board-experiments/3-camera-health/korvo_camera_health`.
2. Check the flash and PSRAM as in 0.3. Select the port and the esp32s3 target.
3. **ESP-IDF: Build Your Project.** Expected app size about 228,208 bytes.
4. **ESP-IDF: Flash Your Project.** Then **ESP-IDF: Monitor Your Device** with log saving on, then press reset. Capture everything, including every `FM_JPEG_BEGIN`, `FM_HEX` and `FM_JPEG_END` line.

### 3.3 Expected output

```
SENSOR_PID=0x3660 expected=0x3660 VER=0x..
FRAME=0 width=320 height=240 format=... bytes=<n> crc32=<hex> capture_us=<n> free_internal=... free_psram=...
FRAME=1 ...
FRAME=2 ...
FM_JPEG_BEGIN <bytes> <crc>
FM_HEX ...      (many lines)
FM_JPEG_END
Capture diagnostic done. Inspect saved frame before preprocessing or inference.
```

The app drops five warmup frames first, then records three. Sending the first frame as hex is slow. Do not use that time as capture latency.

### 3.4 Turn the log into a picture

1. Save the monitor text as `monitor.log` in the project folder.
2. Open a terminal in VS Code (a normal terminal with Python) and run:

   ```
   python extract_frame.py monitor.log capture.jpg
   ```

   Or use **Terminal > Run Task > FirmwareMine: extract captured JPEG**.
3. Expected: `Saved <n> CRC-checked bytes to capture.jpg.`
4. If it says `No complete JPEG block`, `Byte count mismatch` or `CRC mismatch`, the log is incomplete or corrupted. Capture again with a full log. Do not use that frame.
5. Open `capture.jpg`. Check colour, focus, orientation and framing.

### 3.5 Stop if

- Camera init fails, or `SENSOR_PID` is not `0x3660`. Send the full log. Do not change wires or pins to make it pass.
- A sensor ID prints but no viewable frame can be extracted. That is not a successful capture.

### 3.6 Send back

`monitor.log` and `capture.jpg`.

---

## Part 4. USB power: `4-power-measurement`

Do this after Parts 1 to 3 pass. Read `MEASUREMENT_GUIDE.md` first. Summary:

1. Check the meter model and its specification. The UT658DUAL reads 0.01 V and 0.01 A, with current ranges starting at 0.05 A. One display step at 5 V is about 0.05 W.
2. With power disconnected, photograph the power routing. Confirm the modified native-USB port is the board's power input.
3. Wire: supported 5 V supply, then the meter, then the board. No battery. No second USB feed that bypasses the meter. No cutting, soldering or multimeter probing.
4. Do not trigger quick charge or any higher voltage. Do not use the meter's load accessory.
5. Warm up for two minutes. Reset or note the energy and time counters after warmup.
6. Run each condition for at least five minutes. Record end energy, elapsed time, voltage, current. Photograph the start and end screens.
7. Repeat at least three times per condition, alternating idle and work. Keep failed runs with a reason.
8. Average power in watts is the change in watt-hours times 3600 divided by elapsed seconds. Report no more digits than the display supports.
9. Fill `power_runs.csv` only with real readings.

**Not ready yet:** the current CNN replay runs three inferences only. It is not a long timed idle-versus-work benchmark. Extend the firmware with logged timed phases first, or the energy comparison is meaningless.

---

## Checklist: what to send back

- [ ] `flash-id.txt`, board revision, USB port, photo of the connection
- [ ] `run-01.txt`, `run-negative.txt`, completed `trials.csv`, gain, distance, speaker count
- [ ] `cnn-replay.txt`
- [ ] `monitor.log` and `capture.jpg`
- [ ] Power: meter model, start and end photos, routing photo, `power_runs.csv` (only if measured)

Partial runs and failures help. A successful flash or a photo of the board is not a measurement.

## Troubleshooting

| Symptom | What to do |
| --- | --- |
| No serial port appears | Try a data cable, another USB port, and unplug other boards. Re-run **Select Port to Use**. |
| Flash fails to connect | Check you chose the native USB port. Send the full flash output. Do not erase flash. |
| Monitor shows garbage | Check you flashed the build for this folder and selected the right port. |
| Boot log scrolled past | Press the board's reset button while the monitor is open. |
| Build says wrong SDK | Re-run **ESP-IDF: Configure ESP-IDF Extension** and choose 5.3.6. |
| Build fails with `prefix_map` not found or an `esp_libc` resolve error | Two ESP-IDF versions are mixed in one build. Typical cause: the extension points at one install (for example `C:\esp\v6.1`) while the `IDF_PATH` environment variable points at another (`C:\esp\v5.3.6`). Fix: run **ESP-IDF: Select Current ESP-IDF Version** and choose 5.3.6, delete the project's `build-usb` folder (**ESP-IDF: Full Clean** or delete it in the Explorer), close and reopen the ESP-IDF terminal, then build again. Check that the extension and `IDF_PATH` both name the 5.3.6 folder. |
| Anything else | Send the full log and what you did. Do not change the pin map or tolerances. |
