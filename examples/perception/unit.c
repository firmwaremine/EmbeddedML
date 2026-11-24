#include "perception.h"
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#define CHECK(x)                                                               \
  do {                                                                         \
    if (!(x)) {                                                                \
      fprintf(stderr, "line %d failed\n", __LINE__);                           \
      return 1;                                                                \
    }                                                                          \
  } while (0)
int main(void) {
  keyword_gate s;
  keyword_gate_init(&s);
  CHECK(!keyword_gate_push(&s, .8f, 0, true));
  CHECK(!keyword_gate_push(&s, .8f, 20, true));
  CHECK(keyword_gate_push(&s, .8f, 40, true));
  CHECK(!keyword_gate_push(&s, 1, 60, true));
  CHECK(!keyword_gate_push(&s, .39f, 80, true));
  for (uint64_t t = 100; t < 1040; t += 20)
    CHECK(!keyword_gate_push(&s, .9f, t, true));
  CHECK(keyword_gate_push(&s, .9f, 1040, true));
  keyword_gate_init(&s);
  CHECK(!keyword_gate_push(&s, .9f, 0, true));
  CHECK(!keyword_gate_push(&s, .9f, 20, true));
  CHECK(!keyword_gate_push(&s, .9f, 100, true)); /* gap discards current */
  CHECK(!keyword_gate_push(&s, .9f, 120, true));
  CHECK(!keyword_gate_push(&s, .9f, 140, true));
  CHECK(keyword_gate_push(&s, .9f, 160, true));
  CHECK(!keyword_gate_push(&s, NAN, 180, true));
  CHECK(!keyword_gate_push(&s, 2, 200, true));
  CHECK(!keyword_gate_push(&s, .9f, 190, true));
  CHECK(!keyword_gate_push(&s, .9f, 190, true));
  CHECK(!keyword_gate_push(NULL, .8f, 0, true));
  uint8_t src[2 * 8] = {255, 0, 0,   0,   255, 0,   91, 92,
                        0,   0, 255, 255, 255, 255, 93, 94},
                  out[768];
  float f[6];
  CHECK(rgb_resize16(src, sizeof(src), 2, 2, 8, out));
  CHECK(out[0] == 255 && out[1] == 0);
  CHECK(out[8 * 3 + 1] == 255);
  CHECK(out[(8 * 16) * 3 + 2] == 255);
  CHECK(out[767] == 255);
  CHECK(rgb_features(out, f));
  CHECK(fabsf(f[0] - .5f) < 1e-7f && fabsf(f[1]) < 1e-7f &&
        fabsf(f[2] - .5f) < 1e-7f);
  CHECK(fabsf(f[3] - .5f) < 1e-7f && fabsf(f[4] - 1) < 1e-7f &&
        fabsf(f[5] - .5f) < 1e-7f);
  CHECK(!rgb_resize16(src, 13, 2, 2, 8, out));
  CHECK(!rgb_resize16(src, 16, 0, 2, 8, out));
  CHECK(!rgb_resize16(src, 16, 2, 2, 5, out));
  CHECK(!rgb_resize16(src, 16, 2, 2, SIZE_MAX, out));
  CHECK(!rgb_resize16(NULL, 16, 2, 2, 8, out));
  CHECK(!rgb_features(NULL, f));
  float x[3] = {2, 4, 6}, m[3] = {1, 2, 3}, sc[3] = {1, 2, 3};
  double score;
  CHECK(anomaly_score(x, m, sc, &score) && score == 3.0);
  sc[1] = 0;
  CHECK(!anomaly_score(x, m, sc, &score));
  sc[1] = -1;
  CHECK(!anomaly_score(x, m, sc, &score));
  sc[1] = NAN;
  CHECK(!anomaly_score(x, m, sc, &score));
  puts("policy, stride/resize/feature and anomaly boundary tests PASS");
  return 0;
}
