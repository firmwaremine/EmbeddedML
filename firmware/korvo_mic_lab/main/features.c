#include "mic_features.h"
#include <math.h>
bool mic_extract(const int16_t *p, size_t n, unsigned channels,
                 unsigned selected, mic_features *o) {
  if (!p || !o || n < 2 || n > 16000 || channels < 1 || channels > 4 ||
      selected >= channels)
    return false;
  double sum = 0, ss = 0, delta = 0, peak = 0;
  unsigned clips = 0;
  for (size_t i = 0; i < n; i++) {
    int16_t raw = p[i * channels + selected];
    double v = (double)raw / 32768.0;
    sum += v;
    ss += v * v;
    if (fabs(v) > peak)
      peak = fabs(v);
    if (i)
      delta += fabs(v - (double)p[(i - 1) * channels + selected] / 32768.0);
    if (raw == INT16_MIN || raw == INT16_MAX)
      clips++;
  }
  double mean = sum / n, variance = fmax(ss / n - mean * mean, 0);
  *o = (mic_features){.mean = (float)mean,
                      .rms = (float)sqrt(ss / n),
                      .ac_rms = (float)sqrt(variance),
                      .peak = (float)peak,
                      .mean_abs_delta = (float)(delta / (n - 1)),
                      .clipped = clips};
  return true;
}
bool mic_features_selftest(void) {
  const int16_t p[] = {16384, 0, -16384, 0, 16384, 0, -16384, 0};
  mic_features f;
  return mic_extract(p, 4, 2, 0, &f) && f.mean == 0 && f.rms == .5f &&
         f.ac_rms == .5f && f.peak == .5f && f.mean_abs_delta == 1 &&
         f.clipped == 0;
}
