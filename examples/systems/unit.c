#include "bounded.h"
#include <math.h>
#include <stdio.h>
#define CHECK(x)                                                               \
  do {                                                                         \
    if (!(x)) {                                                                \
      fprintf(stderr, "failed line %d\n", __LINE__);                           \
      return 1;                                                                \
    }                                                                          \
  } while (0)
int main(void) {
  prototype p;
  float zero[3] = {0, 0, 0}, one[3] = {1, 0, 0}, big[3] = {4, 4, 4};
  CHECK(prototype_init(&p, zero));
  CHECK(!prototype_update(&p, one, false));
  CHECK(p.accepted == 0);
  CHECK(prototype_update(&p, one, true));
  CHECK(p.current[0] == 0.125f && p.accepted == 1);
  CHECK(prototype_update(&p, one, true));
  CHECK(p.current[0] == 0.234375f);
  float before = p.current[0];
  CHECK(!prototype_update(&p, big, true));
  CHECK(p.current[0] == before && p.accepted == 2);
  prototype_rollback(&p);
  CHECK(p.accepted == 0 && p.current[0] == 0);
  for (unsigned i = 0; i < 16; i++)
    CHECK(prototype_update(&p, zero, true));
  CHECK(!prototype_update(&p, zero, true));
  prototype_rollback(&p);
  float bad[3] = {NAN, 0, 0};
  CHECK(!prototype_update(&p, bad, true));
  CHECK(!prototype_init(NULL, zero));
  puts("bounded adaptation: exact updates, atomic rejection, cap, rollback "
       "PASS");
  return 0;
}
