#include "motion_model.h"
#include "sensing.h"
#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
int main(int argc, char **argv) {
  if (argc != 2)
    return 2;
  if (strcmp(argv[1], "motion") == 0) {
    float x[IMU_N][3], f[3], d[3];
    char extra;
    for (size_t i = 0; i < IMU_N; i++)
      for (size_t j = 0; j < 3; j++) {
        char token[96], tail;
        double v;
        if (scanf("%95s", token) != 1 ||
            sscanf(token, "%lf%c", &v, &tail) != 1 || !isfinite(v) ||
            fabs(v) > 16.0)
          return 2;
        x[i][j] = (float)v;
      }
    if (scanf(" %c", &extra) == 1 || !motion_features((const float (*)[3])x, f))
      return 2;
    int best = 0;
    for (int l = 0; l < 3; l++) {
      double sum = 0;
      for (int i = 0; i < 3; i++) {
        double z = ((double)f[i] - motion_mean[i]) / motion_scale[i];
        double e = z - motion_centers[l][i];
        sum += e * e;
      }
      d[l] = (float)sum;
      if (d[l] < d[best])
        best = l;
    }
    printf("{\"features\":[%.9g,%.9g,%.9g],\"label\":%d,\"distances\":[%.9g,%."
           "9g,%.9g]}\n",
           f[0], f[1], f[2], best, d[0], d[1], d[2]);
    return 0;
  }
  if (strcmp(argv[1], "audio") == 0) {
    int16_t p[AUDIO_N];
    float y[AUDIO_BINS];
    char token[96], extra;
    for (size_t i = 0; i < AUDIO_N; i++) {
      if (scanf("%95s", token) != 1)
        return 2;
      /* Bounded token, sscanf long long can overflow on hostile text: parse as
         double, require exact integer and int16 range before conversion. */
      double v;
      char tail;
      if (sscanf(token, "%lf%c", &v, &tail) != 1 || !isfinite(v) ||
          v < INT16_MIN || v > INT16_MAX || trunc(v) != v)
        return 2;
      p[i] = (int16_t)v;
    }
    if (scanf(" %c", &extra) == 1 || !audio_log_power(p, y))
      return 2;
    printf("{\"log_power\":[");
    for (size_t k = 0; k < AUDIO_BINS; k++)
      printf("%s%.9g", k ? "," : "", y[k]);
    puts("]}");
    return 0;
  }
  return 2;
}
