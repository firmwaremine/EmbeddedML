#ifndef EML_PERCEPTION_H
#define EML_PERCEPTION_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
/* Policy parameters are illustrative. score is finite [0,1], not confidence.
   Caller serializes state and provides monotonic acquisition times in ms. */
typedef struct {
  unsigned streak;
  bool armed, has_previous, has_emitted;
  uint64_t previous_ms, emitted_ms;
} keyword_gate;
void keyword_gate_init(keyword_gate *s);
/* valid=false or a timing gap resets evidence and rearms, but keeps cooldown.
   Current observation after a timing fault is discarded. */
bool keyword_gate_push(keyword_gate *s, float score, uint64_t time_ms,
                       bool valid);
/* Source is RGB888, top-down, with explicit row stride; no overlap allowed.
   Nearest-neighbor stretch uses top-left floor mapping, not half-pixel centers.
   Dimensions 1..4096. Output is fixed 16x16 RGB bytes. */
bool rgb_resize16(const uint8_t *src, size_t bytes, size_t width, size_t height,
                  size_t stride, uint8_t out[16 * 16 * 3]);
/* Region statistics: mean R/G/B in each of left/right halves, divided by 255.
 */
bool rgb_features(const uint8_t image[16 * 16 * 3], float out[6]);
/* Diagonal standardized squared-distance score, not probability or diagnosis.
   Params: finite mean, strictly-positive scale; all buffers nonoverlapping. */
bool anomaly_score(const float x[3], const float mean[3], const float scale[3],
                   double *out);
/* Fixed six-feature vision classifier, label 0..2 or -1 on invalid input. */
int vision_classify(const float features[6], double distances[3]);
#endif
