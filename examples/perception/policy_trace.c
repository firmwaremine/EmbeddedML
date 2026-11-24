#include "perception.h"
#include <stdio.h>
int main(void) {
  keyword_gate s;
  keyword_gate_init(&s);
  /* Deterministic scores, not microphone/model outputs. 12 seconds at 20ms. */
  for (uint64_t t = 0; t < 12000; t += 20) {
    float score = .1f;
    if ((t >= 1000 && t < 1260) || (t >= 1400 && t < 1500) ||
        (t >= 5000 && t < 5200) || (t >= 9000 && t < 9200))
      score = .9f;
    if (t == 7000 || t == 7020)
      score = .85f; /* Only two highs: no event. */
    if (keyword_gate_push(&s, score, t, true))
      printf("%llu\n", (unsigned long long)t);
  }
  return 0;
}
