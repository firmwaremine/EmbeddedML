#include "perception.h"
#include <math.h>
#include <string.h>
void keyword_gate_init(keyword_gate *s) {
  if (s) {
    memset(s, 0, sizeof(*s));
    s->armed = true;
  }
}
bool keyword_gate_push(keyword_gate *s, float score, uint64_t t, bool valid) {
  if (!s)
    return false;
  if (!valid || !isfinite(score) || score < 0 || score > 1) {
    s->streak = 0;
    s->armed = true;
    s->has_previous = false;
    return false;
  }
  if (s->has_previous && (t <= s->previous_ms || t - s->previous_ms > 40)) {
    s->streak = 0;
    s->armed = true;
    s->has_previous = false;
    return false;
  }
  s->previous_ms = t;
  s->has_previous = true;
  if (score < 0.4f) {
    s->armed = true;
    s->streak = 0;
    return false;
  }
  if (!s->armed) {
    s->streak = 0;
    return false;
  }
  if (score >= 0.8f) {
    if (s->streak < 3)
      s->streak++;
  } else
    s->streak = 0;
  if (s->streak == 3 &&
      (!s->has_emitted || (t >= s->emitted_ms && t - s->emitted_ms >= 1000))) {
    s->has_emitted = true;
    s->emitted_ms = t;
    s->armed = false;
    s->streak = 0;
    return true;
  }
  return false;
}
bool rgb_resize16(const uint8_t *src, size_t bytes, size_t w, size_t h,
                  size_t stride, uint8_t out[768]) {
  if (!src || !out || !w || !h || w > 4096 || h > 4096 || stride < w * 3)
    return false;
  size_t row = w * 3;
  if (h > 1 && stride > (SIZE_MAX - row) / (h - 1))
    return false;
  size_t need = (h - 1) * stride + row;
  if (bytes < need)
    return false;
  for (size_t y = 0; y < 16; y++)
    for (size_t x = 0; x < 16; x++) {
      size_t sy = y * h / 16, sx = x * w / 16;
      for (size_t c = 0; c < 3; c++)
        out[(y * 16 + x) * 3 + c] = src[sy * stride + sx * 3 + c];
    }
  return true;
}
bool rgb_features(const uint8_t image[768], float out[6]) {
  if (!image || !out)
    return false;
  unsigned sums[6] = {0};
  for (size_t y = 0; y < 16; y++)
    for (size_t x = 0; x < 16; x++)
      for (size_t c = 0; c < 3; c++)
        sums[(x >= 8 ? 3 : 0) + c] += image[(y * 16 + x) * 3 + c];
  for (size_t i = 0; i < 6; i++)
    out[i] = (float)((double)sums[i] / (128.0 * 255.0));
  return true;
}
bool anomaly_score(const float x[3], const float mean[3], const float scale[3],
                   double *out) {
  if (!x || !mean || !scale || !out)
    return false;
  double score = 0;
  for (size_t i = 0; i < 3; i++) {
    if (!isfinite(x[i]) || !isfinite(mean[i]) || !isfinite(scale[i]) ||
        scale[i] <= 0)
      return false;
    double z = ((double)x[i] - mean[i]) / scale[i];
    score += z * z;
  }
  if (!isfinite(score))
    return false;
  *out = score;
  return true;
}
#include "vision_model.h"
int vision_classify(const float f[6], double d[3]) {
  if (!f || !d)
    return -1;
  for (size_t i = 0; i < 6; i++)
    if (!isfinite(f[i]) || f[i] < 0 || f[i] > 1)
      return -1;
  int best = 0;
  for (size_t l = 0; l < 3; l++) {
    d[l] = 0;
    for (size_t i = 0; i < 6; i++) {
      double z = ((double)f[i] - vision_mean[i]) / vision_scale[i];
      double e = z - vision_centers[l][i];
      d[l] += e * e;
    }
    if (d[l] < d[best])
      best = (int)l;
  }
  return best;
}
