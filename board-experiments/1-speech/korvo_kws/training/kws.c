#include "kws.h"
#include "model_data.h"
#include <math.h>
#include <string.h>
#define PI 3.14159265358979323846
/* Single-precision FFT. The ESP32-S3 has a single-precision FPU only, so double
   math runs in software and is about 25 times slower. Twiddle factors come from a
   table built once in double, so rounding does not accumulate along a butterfly
   row. Output is checked against the earlier double-precision build in
   tests/float_parity.c. */
static float re[512],im[512],tw_cos[256],tw_sin[256];
static float power[257],hidden[64],norm[1176];
static int tw_ready;
static void make_twiddles(void){for(int k=0;k<256;k++){tw_cos[k]=(float)cos(2*PI*k/512);tw_sin[k]=(float)-sin(2*PI*k/512);}tw_ready=1;}
void kws_features(const int16_t *pcm,float *features){
 if(!tw_ready)make_twiddles();
 for(int t=0;t<49;t++){
  for(int i=0;i<512;i++){re[i]=i<400?(pcm[t*320+i]/32768.0f)*kws_window[i]:0;im[i]=0;}
  for(unsigned i=1,j=0;i<512;i++){unsigned bit=256;for(;j&bit;bit>>=1)j^=bit;j^=bit;if(i<j){float tmp=re[i];re[i]=re[j];re[j]=tmp;}}
  for(int len=2;len<=512;len*=2){int step=512/len;
   for(int base=0;base<512;base+=len){for(int j=0;j<len/2;j++){
    float wr=tw_cos[j*step],wi=tw_sin[j*step];
    int a=base+j,b=a+len/2;float vr=re[b]*wr-im[b]*wi,vi=re[b]*wi+im[b]*wr;
    re[b]=re[a]-vr;im[b]=im[a]-vi;re[a]+=vr;im[a]+=vi;
   }}
  }
  for(int k=0;k<257;k++)power[k]=re[k]*re[k]+im[k]*im[k];
  for(int m=0;m<24;m++){float e=0;for(int k=0;k<257;k++)e+=kws_bank[m*257+k]*power[k];features[t*24+m]=logf(fmaxf(e,1e-8f));}
 }
}
int kws_predict(const float *features,float *logits){
 /* Normalise once, not once per hidden unit. Same values, 64 times fewer divisions. */
 for(int i=0;i<1176;i++)norm[i]=(features[i]-kws_mean[i])/kws_std[i];
 for(int h=0;h<64;h++){float v=kws_b1[h];for(int i=0;i<1176;i++)v+=kws_w1[h*1176+i]*norm[i];hidden[h]=fmaxf(v,0);}
 int best=0;for(int c=0;c<5;c++){float v=kws_b2[c];for(int h=0;h<64;h++)v+=kws_w2[c*64+h]*hidden[h];logits[c]=v;if(v>logits[best])best=c;}
 return best;
}
int kws_run(const int16_t *pcm,float *features,float *logits){kws_features(pcm,features);return kws_predict(features,logits);}
float kws_confidence(const float *logits,int label){float mx=logits[0];for(int i=1;i<5;i++)if(logits[i]>mx)mx=logits[i];float sum=0;for(int i=0;i<5;i++)sum+=expf(logits[i]-mx);return expf(logits[label]-mx)/sum;}
