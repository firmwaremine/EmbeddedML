#ifndef FIRMWAREMINE_KWS_H
#define FIRMWAREMINE_KWS_H
#include <stdint.h>
/* Single-owner reference: static scratch is not reentrant. Input: 16000 mono int16 samples.
   No allocations. Output: 1176 raw log-mel values, five logits. */
void kws_features(const int16_t *pcm,float *features);
int kws_predict(const float *features,float *logits);
int kws_run(const int16_t *pcm,float *features,float *logits);
float kws_confidence(const float *logits,int label);
#endif
