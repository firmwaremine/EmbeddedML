#include "sensing.h"
#include <math.h>
/* These are chosen teaching contracts, not a sensor or microphone
 * specification. */
bool motion_features(const float xyz[IMU_N][3], float out[3]) {
  if (!xyz || !out)
    return false;
  double m[IMU_N], sum = 0.0, ss = 0.0, delta = 0.0;
  for (size_t i = 0; i < IMU_N; i++) {
    for (size_t a = 0; a < 3; a++)
      if (!isfinite(xyz[i][a]) || fabsf(xyz[i][a]) > 16.0f)
        return false;
    m[i] =
        hypot(hypot((double)xyz[i][0], (double)xyz[i][1]), (double)xyz[i][2]);
    sum += m[i];
  }
  double mean = sum / IMU_N;
  for (size_t i = 0; i < IMU_N; i++) {
    double ac = m[i] - mean;
    ss += ac * ac;
    if (i)
      delta += fabs(m[i] - m[i - 1]);
  }
  out[0] = (float)mean;
  out[1] = (float)sqrt(ss / IMU_N);
  out[2] = (float)(delta / (IMU_N - 1));
  return true;
}
bool audio_log_power(const int16_t pcm[AUDIO_N], float out[AUDIO_BINS]) {
  if (!pcm || !out)
    return false;
  const double pi = 3.14159265358979323846;
  double mean = 0.0, window[AUDIO_N];
  for (size_t i = 0; i < AUDIO_N; i++)
    mean += (double)pcm[i] / 32768.0;
  mean /= AUDIO_N;
  for (size_t i = 0; i < AUDIO_N; i++)
    window[i] = ((double)pcm[i] / 32768.0 - mean) *
                (0.5 - 0.5 * cos(2 * pi * i / AUDIO_N));
  for (size_t k = 0; k < AUDIO_BINS; k++) {
    double re = 0.0, im = 0.0;
    for (size_t n = 0; n < AUDIO_N; n++) {
      double a = 2 * pi * k * n / AUDIO_N;
      re += window[n] * cos(a);
      im -= window[n] * sin(a);
    }
    double p = (re * re + im * im) / (AUDIO_N * AUDIO_N);
    out[k] = (float)log(fmax(p, 1e-12));
  }
  return true;
}
