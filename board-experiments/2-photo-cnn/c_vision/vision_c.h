#ifndef VISION_C_H
#define VISION_C_H
/* Fixed 96x96 NCHW normalized float input. No runtime allocation. Not reentrant with a shared arena. */
#define VISION_ARENA_FLOATS 101376
#define VISION_INPUT_FLOATS 27648
typedef void (*vision_observer)(int layer,const float *values,int count);
int vision_run(const float*input,const float*weights,float*arena,float*output,vision_observer observer);
#endif
