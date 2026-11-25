# Dependency and source attribution

Our main.c, features.c, mic_features.h, tests, prose and illustrations are original teaching work. Hardware register driver is not rewritten or claimed as original.

esp_codec_dev 1.6.2 is maintained by Espressif Systems, Apache-2.0. IDF Component Manager downloads it unmodified; its LICENSE/notices remain in the component. It supplies ES7210 register configuration and the I2C/I2S device interfaces. Firmware uses direct IDF I2S reads after codec open so the returned byte count and DMA-overflow status remain visible. ESP-IDF is also Espressif software with its own component licenses. See installed source for full notices. Not distributing SDK or managed dependencies as our code.

Verified source references:
- Korvo V3.1 guide: https://docs.espressif.com/projects/esp-adf/en/latest/multimedia-boards/dev-boards/user-guide-esp32-s3-korvo-2.html
- Official board support source, pin/audio reference: https://github.com/espressif/esp-bsp/blob/master/bsp/esp32_s3_korvo_2/README.md . Retrieved checkout a current source snapshot; runtime is not dependent on that whole BSP.
- Codec component: https://components.espressif.com/components/espressif/esp_codec_dev
- Codec source: https://github.com/espressif/esp-adf/tree/master/components/esp_codec_dev
- Exact IDF setup: https://docs.espressif.com/projects/esp-idf/en/v5.3.6/esp32s3/get-started/index.html
- V3.1.2 schematic: https://dl.espressif.com/dl/schematics/SCH_ESP32-S3-Korvo-2_V3.1.2_20240116.pdf

Pin contract: I2C SDA17/SCL18, I2S MCLK16/BCLK9/WS45/ADC DIN10. ES7210 MIC1/MIC2 are on-board analog microphones; MIC3 is associated with the documented echo reference. The app enables only MIC1/MIC2, not TDM/AEC. Speaker amplifier GPIO48 is driven low. No AEC, beamforming, noise suppression or speech recognition is claimed.
