#include "esp_camera.h"
#include "esp_heap_caps.h"
#include "esp_log.h"
#include "esp_psram.h"
#include "esp_timer.h"
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <inttypes.h>
#include <stdio.h>
static const char*TAG="korvo_camera";
static uint32_t crc32(const unsigned char*p,size_t n){uint32_t c=0xffffffff;for(size_t i=0;i<n;i++){c^=p[i];for(int b=0;b<8;b++)c=(c>>1)^((0u-(c&1u))&0xedb88320u);}return ~c;}
void app_main(void){
 gpio_config_t pa={.pin_bit_mask=1ULL<<48,.mode=GPIO_MODE_OUTPUT};ESP_ERROR_CHECK(gpio_config(&pa));ESP_ERROR_CHECK(gpio_set_level(48,0));
 ESP_LOGI(TAG,"Kit OV3660 diagnostic; no CNN, microphone, LCD, speaker or network. PSRAM=%u",(unsigned)esp_psram_get_size());
 camera_config_t c={.pin_pwdn=-1,.pin_reset=-1,.pin_xclk=40,.pin_sccb_sda=17,.pin_sccb_scl=18,.pin_d0=13,.pin_d1=47,.pin_d2=14,.pin_d3=3,.pin_d4=12,.pin_d5=42,.pin_d6=41,.pin_d7=39,.pin_vsync=21,.pin_href=38,.pin_pclk=11,.xclk_freq_hz=20000000,.ledc_timer=LEDC_TIMER_0,.ledc_channel=LEDC_CHANNEL_0,.pixel_format=PIXFORMAT_JPEG,.frame_size=FRAMESIZE_QVGA,.jpeg_quality=12,.fb_count=1,.fb_location=CAMERA_FB_IN_PSRAM,.grab_mode=CAMERA_GRAB_WHEN_EMPTY};
 esp_err_t e=esp_camera_init(&c);if(e!=ESP_OK){ESP_LOGE(TAG,"Camera init failed %s; stop, do not rewire by trial",esp_err_to_name(e));return;}
 sensor_t*s=esp_camera_sensor_get();if(!s){ESP_LOGE(TAG,"No sensor handle");esp_camera_deinit();return;}
 ESP_LOGI(TAG,"SENSOR_PID=0x%04x expected=0x3660 VER=0x%02x",s->id.PID,s->id.VER);
 if(s->id.PID!=OV3660_PID){ESP_LOGE(TAG,"Unexpected sensor; stop before capture");esp_camera_deinit();return;}
 vTaskDelay(pdMS_TO_TICKS(1200));
 for(int i=0;i<5;i++){camera_fb_t*f=esp_camera_fb_get();if(!f){ESP_LOGE(TAG,"Warmup capture failed");esp_camera_deinit();return;}esp_camera_fb_return(f);vTaskDelay(pdMS_TO_TICKS(100));}
 for(int i=0;i<3;i++){
  int64_t t=esp_timer_get_time();camera_fb_t*f=esp_camera_fb_get();int64_t elapsed=esp_timer_get_time()-t;
  if(!f){ESP_LOGE(TAG,"Capture failed");break;}
  ESP_LOGI(TAG,"FRAME=%d width=%u height=%u format=%d bytes=%u crc32=%08" PRIx32 " capture_us=%" PRId64 " free_internal=%u free_psram=%u",i,(unsigned)f->width,(unsigned)f->height,f->format,(unsigned)f->len,crc32(f->buf,f->len),elapsed,(unsigned)heap_caps_get_free_size(MALLOC_CAP_INTERNAL),(unsigned)heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
  if(i==0){
   printf("FM_JPEG_BEGIN %u %08" PRIx32 "\n",(unsigned)f->len,crc32(f->buf,f->len));
   for(size_t off=0;off<f->len;off+=32){printf("FM_HEX ");size_t n=f->len-off;if(n>32)n=32;for(size_t j=0;j<n;j++)printf("%02x",f->buf[off+j]);printf("\n");if(off%512==0)vTaskDelay(1);}
   printf("FM_JPEG_END\n");fflush(stdout);
  }
  esp_camera_fb_return(f);vTaskDelay(pdMS_TO_TICKS(500));
 }
 esp_camera_deinit();ESP_LOGI(TAG,"Capture diagnostic done. Inspect saved frame before preprocessing or inference.");
}
