#ifndef EML_SENSING_H
#define EML_SENSING_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define IMU_N 64
#define AUDIO_N 256
#define AUDIO_BINS 129
/* Reference features; no allocation, driver, concurrency or hard real-time
   claim. Caller owns all buffers. Output unspecified on failure. No overlapping
   buffers. */
bool motion_features(const float xyz[IMU_N][3], float out[3]);
bool audio_log_power(const int16_t pcm[AUDIO_N], float out[AUDIO_BINS]);
#endif
