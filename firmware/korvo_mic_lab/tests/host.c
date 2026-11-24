#include "mic_features.h"
#include <math.h>
#include <stdio.h>
#define CHECK(x)                                                               \
  do {                                                                         \
    if (!(x)) {                                                                \
      fprintf(stderr, "line %d\n", __LINE__);                                  \
      return 1;                                                                \
    }                                                                          \
  } while (0)
int main(void) {
  CHECK(mic_features_selftest());
  mic_features f;
  int16_t zero[8] = {0};
  CHECK(mic_extract(zero, 4, 2, 1, &f) && f.rms == 0 && f.clipped == 0);
  int16_t extremes[2] = {-32768, 32767};
  CHECK(mic_extract(extremes, 2, 1, 0, &f) && f.clipped == 2 && f.peak == 1);
  CHECK(!mic_extract(NULL, 2, 1, 0, &f));
  CHECK(!mic_extract(zero, 1, 1, 0, &f));
  CHECK(!mic_extract(zero, 4, 2, 2, &f));
  CHECK(!mic_extract(zero, 4, 0, 0, &f));
  CHECK(!mic_extract(zero, 4, 2, 0, NULL));
  puts("PASS exact self-test, zero, endpoints and five rejected inputs");
  return 0;
}
