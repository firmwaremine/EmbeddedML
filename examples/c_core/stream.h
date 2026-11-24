#ifndef EML_STREAM_H
#define EML_STREAM_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
typedef struct {
  uint32_t sequence;
  uint64_t time_us;
  float value;
} eml_sample;
typedef struct {
  uint32_t sequence_gaps, timing_faults, nonfinite, emitted;
} eml_stream_counters;
typedef struct {
  float data[64];
  size_t next, count, since;
  bool have_previous;
  eml_sample previous;
  eml_stream_counters counters;
} eml_stream;
void eml_stream_init(eml_stream *s);
bool eml_stream_push(eml_stream *s, eml_sample sample, float *output);
#endif
