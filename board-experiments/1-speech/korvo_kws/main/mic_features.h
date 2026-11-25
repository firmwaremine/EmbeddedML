#ifndef KORVO_FEATURES_H
#define KORVO_FEATURES_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
typedef struct {
  float mean, rms, ac_rms, peak, mean_abs_delta;
  unsigned clipped;
} mic_features;
bool mic_extract(const int16_t *interleaved, size_t frames, unsigned channels,
                 unsigned selected, mic_features *out);
bool mic_features_selftest(void);
#endif
