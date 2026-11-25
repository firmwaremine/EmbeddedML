/* Compares the single-precision kws.c against the earlier double-precision build
   on every test clip listed on stdin (one raw 16000-sample int16 file per line).
   Build: see the FirmwareMine: float FFT parity task. */
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <stdlib.h>
void kws_features(const int16_t *pcm,float *f);
void kws_features_ref(const int16_t *pcm,float *f);
int kws_predict(const float *f,float *l);
int kws_predict_ref(const float *f,float *l);
int main(void){char path[512];int n=0,agree=0;double fe=0,le=0;
 while(fgets(path,sizeof path,stdin)){path[strcspn(path,"\r\n")]=0;
  FILE*fp=fopen(path,"rb");if(!fp){perror(path);return 2;}
  static int16_t pcm[16000];memset(pcm,0,sizeof pcm);size_t got=fread(pcm,2,16000,fp);(void)got;fclose(fp);
  static float fa[1176],fb[1176];float la[5],lb[5];
  kws_features(pcm,fa);kws_features_ref(pcm,fb);
  int pa=kws_predict(fa,la),pb=kws_predict_ref(fb,lb);
  for(int i=0;i<1176;i++)fe=fmax(fe,fabs(fa[i]-fb[i]));
  for(int i=0;i<5;i++)le=fmax(le,fabs(la[i]-lb[i]));
  agree+=pa==pb;n++;}
 printf("{\"clips\":%d,\"label_agreement\":%d,\"max_logmel_abs_diff\":%.9g,\"max_logit_abs_diff\":%.9g}\n",n,agree,fe,le);
 return agree==n&&fe<.02&&le<.02?0:1;}
