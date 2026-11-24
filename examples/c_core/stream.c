#include "stream.h"
#include <math.h>
#include <string.h>
/* Single-threaded: caller serializes pushes and owns output lifetime. */
void eml_stream_init(eml_stream *s) {
  if (s)
    memset(s, 0, sizeof(*s));
}
static void reset(eml_stream *s) {
  s->next = 0;
  s->count = 0;
  s->since = 0;
}
bool eml_stream_push(eml_stream *s, eml_sample v, float *out) {
  if (!s || !out)
    return false;
  /* Never synthesize data across a known measurement gap. */
  if (!isfinite(v.value)) {
    ++s->counters.nonfinite;
    reset(s);
    s->have_previous = false;
    return false;
  }
  if (s->have_previous) {
    bool gap = v.sequence != (uint32_t)(s->previous.sequence + (uint32_t)1);
    bool timing = v.time_us <= s->previous.time_us ||
                  v.time_us - s->previous.time_us < 7000 ||
                  v.time_us - s->previous.time_us > 8500;
    if (gap)
      ++s->counters.sequence_gaps;
    if (timing)
      ++s->counters.timing_faults;
    if (gap || timing)
      reset(s);
  }
  s->previous = v;
  s->have_previous = true;
  s->data[s->next] = v.value;
  s->next = (s->next + 1) % 64;
  if (s->count < 64) {
    ++s->count;
    if (s->count < 64)
      return false;
    s->since = 0;
  } else {
    ++s->since;
    if (s->since < 32)
      return false;
    s->since = 0;
  }
  for (size_t i = 0; i < 64; ++i) {
    out[i] = s->data[(s->next + i) % 64];
  }
  ++s->counters.emitted;
  return true;
}
