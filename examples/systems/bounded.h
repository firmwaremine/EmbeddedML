#ifndef EML_BOUNDED_H
#define EML_BOUNDED_H
#include <stdbool.h>
#include <stdint.h>
/* Caller-owned single-thread state; no persistence, concurrency or label
 * oracle. */
typedef struct {
  float base[3], current[3];
  unsigned accepted;
} prototype;
bool prototype_init(prototype *p, const float initial[3]);
/* Only independently confirmed labels; alpha=1/8, feature [-4,4],
   at most 16 accepted updates, radius <=0.5 from fixed base. */
bool prototype_update(prototype *p, const float sample[3], bool confirmed);
void prototype_rollback(prototype *p);
#endif
