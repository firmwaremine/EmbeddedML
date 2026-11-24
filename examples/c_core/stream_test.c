#include "eml.h"
#include "stream.h"
#include <assert.h>
#include <math.h>
int main(void) {
  eml_stream s;
  eml_stream_init(&s);
  float out[64] = {0};
  assert(!eml_stream_push(NULL, (eml_sample){0, 0, 0}, out));
  for (uint32_t i = 0; i < 128; ++i) {
    bool ready = eml_stream_push(
        &s, (eml_sample){i, 1000000 + (uint64_t)i * 7812, (float)i}, out);
    assert(ready == (i == 63 || i == 95 || i == 127));
    if (ready)
      for (int j = 0; j < 64; ++j)
        assert(out[j] == (float)(i - 63 + j));
  }
  assert(s.counters.emitted == 3);
  assert(!eml_stream_push(&s, (eml_sample){200, 3000000, 200}, out));
  for (uint32_t i = 1; i < 64; ++i) {
    bool ready = eml_stream_push(
        &s,
        (eml_sample){200 + i, 3000000 + (uint64_t)i * 7812, (float)(200 + i)},
        out);
    assert(ready == (i == 63));
  }
  assert(out[0] == 200 && out[63] == 263);
  assert(s.counters.sequence_gaps == 1 && s.counters.timing_faults == 1);
  assert(!eml_stream_push(&s, (eml_sample){264, 3500000, NAN}, out));
  assert(s.counters.nonfinite == 1);
  eml_stream_init(&s);
  eml_stream_push(&s, (eml_sample){UINT32_MAX, 1000000, 0}, out);
  eml_stream_push(&s, (eml_sample){0, 1007812, 0}, out);
  assert(s.counters.sequence_gaps == 0);
  eml_stream_push(&s, (eml_sample){1, 1007811, 0}, out);
  assert(s.counters.timing_faults == 1);
  eml_stream_init(&s);
  eml_stream_push(&s, (eml_sample){0, 1000000, 0}, out);
  eml_stream_push(&s, (eml_sample){1, 1000000, 0}, out);
  eml_stream_push(&s, (eml_sample){2, 1001000, 0}, out);
  eml_stream_push(&s, (eml_sample){3, 2000000, 0}, out);
  assert(s.counters.timing_faults == 3);
  assert(!eml_classify(NULL, 64).valid);
  float x[64] = {0};
  assert(!eml_classify(x, 63).valid);
  x[3] = NAN;
  assert(!eml_classify(x, 64).valid);
  assert(!emln_infer_float(NULL).valid);
  assert(!emln_infer_integer(NULL).valid);
  float z[3] = {INFINITY, 0, 0};
  assert(!emln_infer_float(z).valid && !emln_infer_integer(z).valid);
  return 0;
}
