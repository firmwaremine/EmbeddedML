#include "vision_c.h"
#include "driver/gpio.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_psram.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <inttypes.h>
#include <math.h>
#include <stdlib.h>
extern const float vision_weights[],vision_replay_input[],vision_replay_logits[];
static const char *TAG="vision_replay";
static const char *labels[]={"daisy","dandelion","roses","sunflowers","tulips"};
void app_main(void){
 gpio_config_t pa={.pin_bit_mask=1ULL<<48,.mode=GPIO_MODE_OUTPUT};
 ESP_ERROR_CHECK(gpio_config(&pa));ESP_ERROR_CHECK(gpio_set_level(48,0));
 ESP_LOGW(TAG,"Recorded-input replay only. Camera, LCD, microphone and speaker are NOT initialized. Task watchdog is disabled for this slow diagnostic.");
 ESP_LOGI(TAG,"PSRAM_BYTES=%u",(unsigned)esp_psram_get_size());
 if(esp_psram_get_size()<1024*1024){ESP_LOGE(TAG,"PSRAM unavailable; stop");return;}
 float *arena=heap_caps_malloc(VISION_ARENA_FLOATS*sizeof(float),MALLOC_CAP_SPIRAM|MALLOC_CAP_8BIT);
 if(!arena){ESP_LOGE(TAG,"Arena allocation failed; stop");return;}
 float out[5];
 for(int trial=0;trial<3;trial++){
  vTaskDelay(pdMS_TO_TICKS(100));int64_t t=esp_timer_get_time();
  int pred=vision_run(vision_replay_input,vision_weights,arena,out,NULL);
  int64_t elapsed=esp_timer_get_time()-t;float error=0;int finite=1;
  for(int i=0;i<5;i++){finite=finite&&isfinite(out[i]);error=fmaxf(error,fabsf(out[i]-vision_replay_logits[i]));}
  int expected=0;for(int i=1;i<5;i++)if(vision_replay_logits[i]>vision_replay_logits[expected])expected=i;
  int valid=pred>=0&&pred<5;
  ESP_LOGI(TAG,"TRIAL=%d label=%s expected=%s logit_error=%.7f duration_us=%" PRId64 " free_internal=%u free_psram=%u stack_watermark_bytes=%u PASS=%d",trial,valid?labels[pred]:"INVALID",labels[expected],error,elapsed,(unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),(unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM),(unsigned)uxTaskGetStackHighWaterMark(NULL),finite&&valid&&pred==expected&&error<0.01f);
  ESP_LOGI(TAG,"LOGITS %.7f %.7f %.7f %.7f %.7f",out[0],out[1],out[2],out[3],out[4]);
 }
 free(arena);ESP_LOGI(TAG,"Replay finished. No target benchmark is established until these logs are captured on the physical board.");
}
