# Korvo USB power worksheet

Prepared for a UNI-T UT658DUAL expected Thursday26November2026. Verify the delivered model before using its specifications. This is an optional measurement stage; software replay/capture trials can happen earlier.

## What the meter can establish

UNI-T specifies0.01V voltage resolution,0.01A current resolution, and current ranges starting at0.05A. At5V a0.01A display step corresponds to about0.05W. The tester is suitable for whole-board USB input readings and accumulated consumption over sustained runs. It is not a waveform instrument, peak-current detector or reliable deep-sleep-current meter. Do not describe a tiny subtraction of two rounded display values as a precise inference cost.

Ten stored sets do not establish high-rate logging. Inspect the actual meter/manual for energy/time screens and reset behavior. Record the displayed energy units and least significant digit rather than assuming an undocumented resolution. Do not treat mAh as energy without a supported voltage/time calculation.

## Check the measurement boundary first

1. Confirm the exact board modification, module, power-input connector and power routing. With power disconnected, photograph the board/connection arrangement. A meter on one USB cable measures only that path.
2. Use the board's supported5VUSB supply and a correct rated cable. Do not activate a quick-charge trigger or request a higher voltage. Do not use the tester's electrical-load accessory or connect an unrelated load.
3. Source -> meter -> board's verified power input. No battery or second USB power feed may bypass the meter if the claim is whole-board input. Do not defeat power protection or connect a second supply to preserve logging. If logging requires an additional powered USB lead, stop and settle the routing before measurement.
4. No PCB cutting, soldering or multimeter insertion is part of this plan. If the modified native-USB port's supply path is unclear, return the photo instead of guessing.
5. Keep cable, supply, LEDs, display, camera, microphones, radios, console activity and ambient conditions the same between runs. Record every exception. USB input includes regulator and peripheral consumption; it is not bare-chip inference power. Meter/cable insertion can change voltage and must be reported.

## Run sequence

First complete numerical replay and capture health. Record firmware SHA256, configuration, serial logs and runtime stability before measuring power. A repeated failing run is not useful workload energy.

Use an explicitly implemented idle phase and a sustained repeated-work phase with the same peripherals. The current three-inference CNN replay is a diagnostic, not yet a controlled long-duration idle-versus-compute benchmark. It must be extended with clearly logged timed phases before using that comparison. Do not call camera-active versus camera-off a compute-only difference.

For each condition:
- Warm up for two minutes without changing connections.
- Reset or note the energy/time counters after warmup, not during boot. Record the start readings.
- Run for at least five minutes; extend when the accumulated energy changes by too few displayed units. Avoid interpreting a difference below several counter steps. Note the exact displayed resolution.
- Record end energy, elapsed time, representative voltage/current and observed display ranges. A photo of start/end screens helps prevent transcription errors.
- Save the matching firmware phase timestamps and completed-work count. Repeated workload should yield/delay safely rather than hiding watchdog failures.
- Repeat at least three times per condition, preferably alternating idle and work. Keep all runs, including failures and resets, with a reason if excluded.

Average input power in watts = change in watt-hours ×3600 / elapsed seconds. Total energy per completed operation = measured joules / completed operations, only when those operations and the full measurement window are defined. This total includes board baseline. Incremental energy requires a matched baseline subtraction and remains limited by meter quantization, drift and workload equivalence. Do not report more significant digits than the evidence supports.

No measurements are prefilled. Do not substitute a module datasheet's current or a software timing estimate for a meter reading.

Official specification: https://meters.uni-trend.com/product/ut658-series/
