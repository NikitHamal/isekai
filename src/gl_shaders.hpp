// GLSL 330 sources: Cook-Torrance GGX PBR forest shader, sky dome, HUD/FX overlay.
#pragma once
namespace isekai {
static const char* kPbrVS = R"(#version 330 core
layout(location=0) in vec3 aP; layout(location=1) in vec3 aN; layout(location=2) in vec2 aUV; layout(location=3) in vec4 aT;
uniform mat4 uM; uniform mat4 uVP; out vec3 vWP; out vec3 vN; out vec2 vUV; out vec4 vT;
void main(){ vec4 w = uM*vec4(aP,1.0); vWP=w.xyz; vN=mat3(uM)*aN; vT=vec4(mat3(uM)*aT.xyz,aT.w); vUV=aUV; gl_Position=uVP*w; })";
static const char* kPbrFS = R"(#version 330 core
in vec3 vWP; in vec3 vN; in vec2 vUV; in vec4 vT; out vec4 oC;
uniform sampler2D uAlb; uniform sampler2D uNrm; uniform sampler2D uMR; uniform sampler2D uEm; uniform vec4 uHas; uniform vec4 uBase; uniform vec3 uEmF;
uniform vec3 uTint; uniform float uEmBoost; uniform vec3 uCam; uniform float uTime; uniform int uGround;
uniform vec3 uLP[8]; uniform vec3 uLC[8]; uniform float uLR[8]; uniform int uNL; uniform vec3 uHoriz; uniform vec3 uZenith;
const float PI=3.14159265;
float hash(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float vnoise(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f); return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y); }
float D(float nh,float a){ float a2=a*a; float d=nh*nh*(a2-1.0)+1.0; return a2/(PI*d*d); }
float Gs(float nv,float nl,float r){ float k=(r+1.0)*(r+1.0)/8.0; return (nv/(nv*(1.0-k)+k))*(nl/(nl*(1.0-k)+k)); }
vec3 brdf(vec3 N,vec3 V,vec3 L,vec3 rad,vec3 alb,float rough,float met){
  vec3 H=normalize(V+L); float nl=max(dot(N,L),0.0), nv=max(dot(N,V),1e-3), nh=max(dot(N,H),0.0), vh=max(dot(V,H),0.0);
  vec3 F0=mix(vec3(0.04),alb,met); vec3 F=F0+(1.0-F0)*pow(1.0-vh,5.0); float a=max(rough*rough,0.02);
  vec3 spec=D(nh,a)*Gs(nv,nl,rough)*F/(4.0*nv*max(nl,1e-3)); vec3 kd=(1.0-F)*(1.0-met);
  return (kd*alb/PI+spec)*rad*nl; }
vec3 aces(vec3 x){ return clamp((x*(2.51*x+0.03))/(x*(2.43*x+0.59)+0.14),0.0,1.0); }
void main(){
  vec3 alb=uBase.rgb; float rough=0.7, met=0.0; vec3 N=normalize(vN); vec3 V=normalize(uCam-vWP); vec3 em=vec3(0.0);
  if(uGround==1){ float n=vnoise(vWP.xz*1.7)*0.6+vnoise(vWP.xz*6.0)*0.4; float path=smoothstep(2.6,1.6,abs(vWP.x+0.25*sin(vWP.z*0.35)));
    vec3 grass=mix(vec3(0.07,0.20,0.04),vec3(0.20,0.34,0.07),n); vec3 dirt=mix(vec3(0.20,0.14,0.08),vec3(0.34,0.25,0.14),n); alb=mix(grass,dirt,path); rough=0.95; N=vec3(0,1,0); }
  else {
    if(uHas.x>0.5) alb=pow(texture(uAlb,vUV).rgb,vec3(2.2))*uBase.rgb;
    if(uHas.z>0.5){ vec3 mr=texture(uMR,vUV).rgb; rough=clamp(mr.g,0.05,1.0); met=mr.b; }
    if(dot(N,V)<0.0) N=-N;
    if(uHas.y>0.5){ vec3 T=normalize(vT.xyz); T=normalize(T-N*dot(N,T)); vec3 B=cross(N,T)*vT.w; vec3 t=texture(uNrm,vUV).xyz*2.0-1.0; N=normalize(T*t.x+B*t.y+N*t.z); }
    if(uHas.w>0.5) em=pow(texture(uEm,vUV).rgb,vec3(2.2))*uEmF*uEmBoost; }
  alb*=uTint; vec3 sunDir=normalize(vec3(0.45,0.8,0.35)); vec3 col=brdf(N,V,sunDir,vec3(3.2,2.7,2.1),alb,rough,met);
  vec3 amb=mix(vec3(0.06,0.09,0.04),uZenith*0.55,N.y*0.5+0.5); col+=alb*amb*(1.0-met*0.6)+ mix(vec3(0.0),uHoriz*0.2,pow(1.0-max(dot(N,V),0.0),3.0))*(0.3+met);
  for(int i=0;i<uNL;i++){ vec3 d=uLP[i]-vWP; float dist=length(d); float att=clamp(1.0-pow(dist/uLR[i],2.0),0.0,1.0); att*=att/(1.0+dist*dist*0.35);
    col+=brdf(N,V,d/dist,uLC[i]*att,alb,rough,met); }
  col+=em; float dist=length(uCam-vWP); float fog=1.0-exp(-pow(dist*0.016,1.25)); col=mix(col,uHoriz*0.85,clamp(fog,0.0,1.0));
  col=aces(col*0.85); oC=vec4(pow(col,vec3(1.0/2.2)),1.0); })";
static const char* kSkyVS = R"(#version 330 core
out vec2 vP; void main(){ vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2); vP=p*2.0-1.0; gl_Position=vec4(vP,0.9999,1.0); })";
static const char* kSkyFS = R"(#version 330 core
in vec2 vP; out vec4 oC; uniform vec3 uF; uniform vec3 uR; uniform vec3 uU; uniform vec2 uTan; uniform vec3 uHoriz; uniform vec3 uZenith;
void main(){ vec3 d=normalize(uF+vP.x*uTan.x*uR+vP.y*uTan.y*uU); float h=clamp(d.y,0.0,1.0);
  vec3 c=mix(uHoriz*0.9,uZenith,pow(h,0.55)); c=mix(c,vec3(0.10,0.22,0.08)*1.6,smoothstep(0.0,-0.25,d.y));
  float s=max(dot(d,normalize(vec3(0.45,0.8,0.35))),0.0); c+=vec3(1.0,0.8,0.5)*(pow(s,64.0)*0.8+pow(s,6.0)*0.18);
  c=pow(clamp(c*0.95,0.0,1.0),vec3(1.0/2.0)); oC=vec4(c,1.0); })";
static const char* kHudVS = R"(#version 330 core
layout(location=0) in vec2 aP; layout(location=1) in vec2 aUV; layout(location=2) in vec4 aC; uniform vec2 uRes; out vec2 vUV; out vec4 vC;
void main(){ vUV=aUV; vC=aC; gl_Position=vec4(aP.x/uRes.x*2.0-1.0,1.0-aP.y/uRes.y*2.0,0.0,1.0); })";
static const char* kHudFS = R"(#version 330 core
in vec2 vUV; in vec4 vC; out vec4 oC; void main(){ vec4 c=vC; if(vUV.x<1.5){ float r=length(vUV); c.a*=pow(clamp(1.0-r,0.0,1.0),1.6); } oC=c; })";
}  // namespace isekai
