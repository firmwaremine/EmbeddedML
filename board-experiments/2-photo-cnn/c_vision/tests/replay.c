#include "vision_c.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
static float *load(const char *path,size_t n){FILE*f=fopen(path,"rb");float*p=malloc(n*sizeof(float));if(!f||!p)exit(2);if(fread(p,sizeof(float),n,f)!=n||fgetc(f)!=EOF)exit(3);fclose(f);return p;}
int main(void){
 float*w=load("weights.f32",929893),*in=load("replay_input.f32",VISION_INPUT_FLOATS),*expected=load("replay_logits.f32",5),*arena=malloc(VISION_ARENA_FLOATS*sizeof(float)),out[5];if(!arena)return 2;
 int pred=vision_run(in,w,arena,out,NULL),best=0;float error=0;
 for(int i=0;i<5;i++){if(!isfinite(out[i]))return 1;if(expected[i]>expected[best])best=i;error=fmaxf(error,fabsf(out[i]-expected[i]));}
 printf("replay label=%d expected=%d max_logit_error=%.8f\n",pred,best,error);
 free(w);free(in);free(expected);free(arena);return pred==best&&error<0.01f?0:1;
}
