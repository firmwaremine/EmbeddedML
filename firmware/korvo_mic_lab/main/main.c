#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "driver/i2s_std.h"
#include "esp_codec_dev.h"
#include "esp_codec_dev_defaults.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/portmacro.h"
#include "mic_features.h"
#include <inttypes.h>
#include <stdio.h>
#define FRAMES 256
#define RATE 16000
static const char *TAG = "korvo_mic";
static int16_t pcm[FRAMES * 2];
static uint32_t rx_overflows;
static portMUX_TYPE overflow_lock = portMUX_INITIALIZER_UNLOCKED;
static bool IRAM_ATTR on_overflow(i2s_chan_handle_t h, i2s_event_data_t *e,
                                  void *ctx) {
  (void)h;
  (void)e;
  (void)ctx;
  portENTER_CRITICAL_ISR(&overflow_lock);
  rx_overflows++;
  portEXIT_CRITICAL_ISR(&overflow_lock);
  return false;
}
void app_main(void) {
  if (!mic_features_selftest()) {
    ESP_LOGE(TAG, "feature self-test FAILED");
    return;
  }
  ESP_LOGI(TAG,
           "SELFTEST PASS; Korvo-2 V3.1 capture experiment; no ML classifier");
  /* Speaker amplifier stays disabled; no speaker or DAC is initialized. */
  gpio_config_t pa = {.pin_bit_mask = 1ULL << 48, .mode = GPIO_MODE_OUTPUT};
  ESP_ERROR_CHECK(gpio_config(&pa));
  ESP_ERROR_CHECK(gpio_set_level(48, 0));
  i2c_master_bus_handle_t bus;
  i2c_master_bus_config_t bc = {.i2c_port = 0,
                                .sda_io_num = 17,
                                .scl_io_num = 18,
                                .clk_source = I2C_CLK_SRC_DEFAULT,
                                .glitch_ignore_cnt = 7,
                                .flags.enable_internal_pullup = true};
  ESP_ERROR_CHECK(i2c_new_master_bus(&bc, &bus));
  /* Codec driver uses 8-bit wire address 0x80; bus probe uses 7-bit 0x40. */
  ESP_ERROR_CHECK(i2c_master_probe(bus, 0x40, 1000));
  i2s_chan_handle_t rx;
  i2s_chan_config_t cc = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  cc.dma_desc_num = 8;
  cc.dma_frame_num = FRAMES;
  ESP_ERROR_CHECK(i2s_new_channel(&cc, NULL, &rx));
  i2s_std_config_t sc = {
      .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(RATE),
      .slot_cfg = I2S_STD_PHILIP_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_16BIT,
                                                     I2S_SLOT_MODE_STEREO),
      .gpio_cfg = {
          .mclk = 16, .bclk = 9, .ws = 45, .dout = I2S_GPIO_UNUSED, .din = 10}};
  ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx, &sc));
  i2s_event_callbacks_t callbacks = {.on_recv_q_ovf = on_overflow};
  ESP_ERROR_CHECK(i2s_channel_register_event_callback(rx, &callbacks, NULL));
  audio_codec_i2c_cfg_t ctrl_cfg = {
      .port = 0, .addr = ES7210_CODEC_DEFAULT_ADDR, .bus_handle = bus};
  const audio_codec_ctrl_if_t *ctrl = audio_codec_new_i2c_ctrl(&ctrl_cfg);
  audio_codec_i2s_cfg_t data_cfg = {.port = 0, .rx_handle = rx};
  const audio_codec_data_if_t *data = audio_codec_new_i2s_data(&data_cfg);
  es7210_codec_cfg_t adc_cfg = {.ctrl_if = ctrl,
                                .mic_selected =
                                    ES7210_SEL_MIC1 | ES7210_SEL_MIC2,
                                .master_mode = false};
  if (!ctrl || !data) {
    ESP_LOGE(TAG, "codec interface allocation failed");
    return;
  }
  const audio_codec_if_t *adc = es7210_codec_new(&adc_cfg);
  if (!adc) {
    ESP_LOGE(TAG, "ES7210 init failed");
    return;
  }
  esp_codec_dev_cfg_t dc = {
      .dev_type = ESP_CODEC_DEV_TYPE_IN, .codec_if = adc, .data_if = data};
  esp_codec_dev_handle_t dev = esp_codec_dev_new(&dc);
  if (!dev) {
    ESP_LOGE(TAG, "codec device allocation failed");
    return;
  }
  esp_codec_dev_sample_info_t fmt = {
      .sample_rate = RATE, .channel = 2, .bits_per_sample = 16};
  ESP_ERROR_CHECK(esp_codec_dev_open(dev, &fmt));
  ESP_ERROR_CHECK(esp_codec_dev_set_in_gain(dev, 24.0f));
  ESP_LOGI(TAG, "CAPTURE 16000Hz stereo 16-bit; MIC1/MIC2; gain24dB; discard "
                "first 0.256s");
  uint64_t blocks = 0;
  uint32_t errors = 0, short_reads = 0, last_ovf = 0;
  int64_t max_us = 0, start_us = esp_timer_get_time();
  for (;;) {
    size_t got = 0;
    esp_err_t err = i2s_channel_read(rx, pcm, sizeof(pcm), &got, 1000);
    if (err != ESP_OK || got != sizeof(pcm)) {
      errors += (err != ESP_OK);
      short_reads++;
      ESP_LOGW(TAG, "read reset err=%s bytes=%u", esp_err_to_name(err),
               (unsigned)got);
      continue;
    }
    blocks++;
    if (blocks <= 16)
      continue;
    mic_features f[2];
    int64_t t = esp_timer_get_time();
    bool ok = mic_extract(pcm, FRAMES, 2, 0, &f[0]) &&
              mic_extract(pcm, FRAMES, 2, 1, &f[1]);
    int64_t elapsed = esp_timer_get_time() - t;
    if (elapsed > max_us)
      max_us = elapsed;
    if (!ok) {
      ESP_LOGE(TAG, "feature failure");
      continue;
    }
    if (blocks % 64 == 0) {
      portENTER_CRITICAL(&overflow_lock);
      uint32_t ovf = rx_overflows;
      portEXIT_CRITICAL(&overflow_lock);
      ESP_LOGI(TAG,
               "blocks=%" PRIu64 " errors=%" PRIu32 " short=%" PRIu32
               " ovf=%" PRIu32 " delta_ovf=%" PRIu32 " elapsed_ms=%" PRId64
               " feat_max_us=%" PRId64 " heap=%u minheap=%u",
               blocks, errors, short_reads, ovf, ovf - last_ovf,
               (esp_timer_get_time() - start_us) / 1000, max_us,
               (unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),
               (unsigned)heap_caps_get_minimum_free_size(MALLOC_CAP_INTERNAL));
      last_ovf = ovf;
      for (unsigned c = 0; c < 2; c++)
        ESP_LOGI(TAG,
                 "slot%u latest mean=%.6f rms=%.6f ac=%.6f peak=%.6f mad=%.6f "
                 "clip=%u",
                 c, f[c].mean, f[c].rms, f[c].ac_rms, f[c].peak,
                 f[c].mean_abs_delta, f[c].clipped);
    }
  }
}
