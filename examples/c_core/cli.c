#include "eml.h"
#include "model_data.h"
#include <errno.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
static int read_values(float *x, int n) {
  char token[128];
  for (int i = 0; i < n; ++i) {
    if (scanf("%127s", token) != 1)
      return 0;
    char *end = NULL;
    errno = 0;
    x[i] = strtof(token, &end);
    if (errno || end == token || *end || !isfinite(x[i]))
      return 0;
  }
  return scanf("%127s", token) == EOF;
}
int main(int argc, char **argv) {
  const int neural = argc == 2 && strcmp(argv[1], "neural") == 0;
  if (argc > 2 || (argc == 2 && !neural))
    return 2;
  float x[64] = {0};
  if (!read_values(x, neural ? 3 : 64))
    return 2;
  if (neural) {
    emln_float_result f = emln_infer_float(x);
    emln_integer_result q = emln_infer_integer(x);
    if (!f.valid || !q.valid)
      return 2;
    printf("{\"float_label\":%d,\"integer_label\":%d,\"float_logits\":[%.9g,%."
           "9g,%.9g],\"integer_logits\":[%d,%d,%d],\"clipped_inputs\":%d,"
           "\"clipped_hidden\":%d}\n",
           f.label, q.label, (double)f.logits[0], (double)f.logits[1],
           (double)f.logits[2], (int)q.logits[0], (int)q.logits[1],
           (int)q.logits[2], q.clipped_inputs, q.clipped_hidden);
  } else {
    eml_result r = eml_classify(x, 64);
    if (!r.valid)
      return 2;
    printf("{\"label\":%d,\"name\":\"%s\",\"features\":[%.9g,%.9g,%.9g],"
           "\"distances\":[%.9g,%.9g,%.9g]}\n",
           r.label, eml_labels[r.label], (double)r.features[0],
           (double)r.features[1], (double)r.features[2], (double)r.distances[0],
           (double)r.distances[1], (double)r.distances[2]);
  }
  return 0;
}
