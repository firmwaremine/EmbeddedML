#ifndef EML_H
#define EML_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
/* Original C11 reference kernels. No heap allocation or external model runtime.
 * Input validity is not distribution membership or confidence. */
typedef struct {
  bool valid;
  int label;
  float features[3];
  float distances[3];
} eml_result;
typedef struct {
  bool valid;
  int label;
  float logits[3];
} emln_float_result;
typedef struct {
  bool valid;
  int label;
  int32_t logits[3];
  int clipped_inputs;
  int clipped_hidden;
} emln_integer_result;
eml_result eml_classify(const float *samples, size_t length);
bool emln_standardize(const float *features, float *standardized);
emln_float_result emln_infer_float(const float *standardized);
emln_integer_result emln_infer_integer(const float *standardized);
#endif
