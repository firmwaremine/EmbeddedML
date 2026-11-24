#include "eml.h"
#include "model_data.h"
#include <limits.h>
#include <math.h>
_Static_assert(EMLN_EX >= -20 && EMLN_EX <= 10, "input exponent");
_Static_assert(EMLN_EX + EMLN_EW1 - EMLN_EH >= -30 &&
                   EMLN_EX + EMLN_EW1 - EMLN_EH <= 20,
               "rescale exponent");
/* Feature contract: mean, AC RMS, average absolute successive change. */
eml_result eml_classify(const float *x, size_t n) {
  eml_result r = {0};
  r.label = -1;
  if (!x || n != 64)
    return r;
  double mean = 0, var = 0, delta = 0;
  for (size_t i = 0; i < n; ++i) {
    if (!isfinite(x[i]))
      return r;
    mean += x[i];
  }
  mean /= n;
  for (size_t i = 0; i < n; ++i) {
    double d = (double)x[i] - mean;
    var += d * d;
    if (i)
      delta += fabs((double)x[i] - x[i - 1]);
  }
  r.features[0] = (float)mean;
  r.features[1] = (float)sqrt(var / n);
  r.features[2] = (float)(delta / (n - 1));
  float z[3] = {0};
  for (int j = 0; j < 3; ++j) {
    if (!isfinite(r.features[j]) || !(eml_scale[j] > 0))
      return r;
    z[j] = (r.features[j] - eml_mean[j]) / eml_scale[j];
    if (!isfinite(z[j]))
      return r;
  }
  for (int k = 0; k < 3; ++k) {
    double d = 0;
    for (int j = 0; j < 3; ++j) {
      double a = (double)z[j] - eml_centers[k][j];
      d += a * a;
    }
    r.distances[k] = (float)d;
    if (!isfinite(r.distances[k]))
      return r;
  }
  r.label = 0;
  for (int k = 1; k < 3; ++k)
    if (r.distances[k] < r.distances[r.label])
      r.label = k;
  r.valid = true;
  return r;
}
bool emln_standardize(const float *f, float *z) {
  if (!f || !z)
    return false;
  for (int j = 0; j < 3; ++j) {
    if (!isfinite(f[j]) || !(emln_scale[j] > 0))
      return false;
    z[j] = (f[j] - emln_mean[j]) / emln_scale[j];
    if (!isfinite(z[j]))
      return false;
  }
  return true;
}
emln_float_result emln_infer_float(const float *z) {
  emln_float_result r = {0};
  r.label = -1;
  if (!z)
    return r;
  for (int i = 0; i < 3; ++i)
    if (!isfinite(z[i]))
      return r;
  float h[8] = {0};
  for (int j = 0; j < 8; ++j) {
    float a = emln_b1[j];
    for (int i = 0; i < 3; ++i)
      a += z[i] * emln_w1[i][j];
    if (!isfinite(a))
      return r;
    h[j] = fmaxf(0, a);
  }
  for (int k = 0; k < 3; ++k) {
    float a = emln_b2[k];
    for (int j = 0; j < 8; ++j)
      a += h[j] * emln_w2[j][k];
    if (!isfinite(a))
      return r;
    r.logits[k] = a;
  }
  r.label = 0;
  for (int k = 1; k < 3; ++k)
    if (r.logits[k] > r.logits[r.label])
      r.label = k;
  r.valid = true;
  return r;
}
/* Exported power-of-two scales. Round ties away from zero.
 * The exporter constrains exponents and accumulator bounds. */
static int64_t rescale(int64_t v, int e) {
  if (e >= 0)
    return v * ((int64_t)1 << e);
  int64_t d = (int64_t)1 << (-e);
  return (v >= 0 ? 1 : -1) * ((v >= 0 ? v : -v) + d / 2) / d;
}
emln_integer_result emln_infer_integer(const float *z) {
  emln_integer_result r = {0};
  r.label = -1;
  if (!z)
    return r;
  int32_t x[3] = {0}, h[8] = {0};
  for (int i = 0; i < 3; ++i) {
    if (!isfinite(z[i]))
      return r;
    double a = ldexp((double)z[i], -EMLN_EX);
    if (!isfinite(a))
      return r;
    a = round(a);
    if (a < -128 || a > 127)
      ++r.clipped_inputs;
    x[i] = (int32_t)fmin(127, fmax(-128, a));
  }
  for (int j = 0; j < 8; ++j) {
    int64_t a = emln_qb1[j];
    for (int i = 0; i < 3; ++i)
      a += x[i] * (int32_t)emln_qw1[i][j];
    if (a < INT32_MIN || a > INT32_MAX)
      return r;
    int64_t v = rescale(a, EMLN_EX + EMLN_EW1 - EMLN_EH);
    if (v < 0)
      v = 0;
    if (v > 127) {
      ++r.clipped_hidden;
      v = 127;
    }
    h[j] = (int32_t)v;
  }
  for (int k = 0; k < 3; ++k) {
    int64_t a = emln_qb2[k];
    for (int j = 0; j < 8; ++j)
      a += h[j] * (int32_t)emln_qw2[j][k];
    if (a < INT32_MIN || a > INT32_MAX)
      return r;
    r.logits[k] = (int32_t)a;
  }
  r.label = 0;
  for (int k = 1; k < 3; ++k)
    if (r.logits[k] > r.logits[r.label])
      r.label = k;
  r.valid = true;
  return r;
}
