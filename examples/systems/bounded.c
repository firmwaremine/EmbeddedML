#include "bounded.h"
#include <math.h>
bool prototype_init(prototype *p, const float v[3]) {
  if (!p || !v)
    return false;
  for (unsigned i = 0; i < 3; i++)
    if (!isfinite(v[i]) || fabsf(v[i]) > 4)
      return false;
  for (unsigned i = 0; i < 3; i++)
    p->base[i] = p->current[i] = v[i];
  p->accepted = 0;
  return true;
}
bool prototype_update(prototype *p, const float x[3], bool confirmed) {
  if (!p || !x || !confirmed || p->accepted >= 16)
    return false;
  float candidate[3];
  double distance = 0;
  for (unsigned i = 0; i < 3; i++) {
    if (!isfinite(x[i]) || fabsf(x[i]) > 4 || !isfinite(p->base[i]) ||
        !isfinite(p->current[i]))
      return false;
    candidate[i] = p->current[i] + 0.125f * (x[i] - p->current[i]);
    double d = (double)candidate[i] - p->base[i];
    distance += d * d;
  }
  if (distance > 0.25)
    return false;
  for (unsigned i = 0; i < 3; i++)
    p->current[i] = candidate[i];
  p->accepted++;
  return true;
}
void prototype_rollback(prototype *p) {
  if (p) {
    for (unsigned i = 0; i < 3; i++)
      p->current[i] = p->base[i];
    p->accepted = 0;
  }
}
