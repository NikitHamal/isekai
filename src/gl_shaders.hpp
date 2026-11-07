// GLSL 330 sources: Cook-Torrance GGX PBR + 3x3 PCF sun shadows, splat-mapped terrain, golden-hour atmospheric sky, depth-only shadow pass, HUD/FX overlay.
#pragma once
namespace isekai {
static const char* kShadowVS = R"(#version 330 core
layout(location=0) in vec3 aP; uniform mat4 uM; uniform mat4 uLVP; void main(){ gl_Position=uLVP*uM*vec4(aP,1.0); })";
static const char* kShadowFS = R"(#version 330 core
void main(){})";
static const char* kPbrVS = R"(#version 330 core
layout(location=0) in vec3 aP; layout(location=1) in vec3 aN; layout(location=2) in vec2 aUV; layout(location=3) in vec4 aT;
uniform mat4 uM; uniform mat4 uVP; out vec3 vWP; out vec3 vN; out vec2 vUV; out vec4 vT;
void main(){ vec4 w = uM*vec4(aP,1.0); vWP=w.xyz; vN=mat3(uM)*aN; vT=vec4(mat3(uM)*aT.xyz,aT.w); vUV=aUV; gl_Position=uVP*w; })";
static const char* kPbrFS = R"(#version 330 core
in vec3 vWP; in vec3 vN; in vec2 vUV; in vec4 vT; out vec4 oC;
uniform sampler2D uAlb; uniform sampler2D uNrm; uniform sampler2D uMR; uniform sampler2D uEm; uniform sampler2D uShadow; uniform vec4 uHas; uniform vec4 uBase; uniform vec3 uEmF;
uniform vec3 uTint; uniform float uEmBoost; uniform vec3 uCam; uniform float uTime; uniform int uGround; uniform float uBaseY; uniform mat4 uLVP; uniform vec3 uSun;
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
float shadowAt(vec3 wp, vec3 n){
  vec4 p=uLVP*vec4(wp+n*0.07,1.0); vec3 c=p.xyz/p.w*0.5+0.5; if(c.x<0.0||c.x>1.0||c.y<0.0||c.y>1.0||c.z>1.0) return 1.0;
  vec2 ts=1.0/vec2(textureSize(uShadow,0)); float s=0.0; float bias=0.0006;
  for(int y=-1;y<=1;y++) for(int x=-1;x<=1;x++) s+= (c.z-bias > texture(uShadow,c.xy+vec2(x,y)*ts*1.4).r) ? 0.0 : 1.0;
  return s/9.0; }
float roadX(float z){ return 3.5*sin(z*0.045)+1.5*sin(z*0.11+1.0); }
float sst(float a,float b,float x){ float t=clamp((x-a)/(b-a),0.0,1.0); return t*t*(3.0-2.0*t); }
// Terrain splat: grass/meadow, rocky foothills, mud verge, mortared cobblestone road + plaza. Returns albedo, writes bump height + roughness.
vec3 terrain(vec3 wp, out float hgt, out float rough){
  float x=wp.x, z=wp.z; float d=abs(x-roadX(z)); float rm=max(clamp((3.2-d)/1.2,0.0,1.0), sst(8.0,14.0,z)*(1.0-sst(16.0,22.0,d)));
  float n1=vnoise(wp.xz*0.9), n2=vnoise(wp.xz*4.0), n3=vnoise(wp.xz*0.12), n4=vnoise(wp.xz*18.0);
  vec3 grass=mix(mix(vec3(0.09,0.21,0.04),vec3(0.27,0.40,0.09),n1*0.6+n2*0.4),vec3(0.42,0.37,0.16),sst(0.55,0.9,n3)*0.6)*(0.85+0.3*n4);
  float rk=clamp((wp.y-3.5)/5.0+(n3-0.5)*0.9+(n2-0.5)*0.25,0.0,1.0);
  vec3 rock=mix(vec3(0.33,0.31,0.28),vec3(0.55,0.52,0.46),n2)*(0.8+0.4*n4);
  vec3 col=mix(grass,rock,sst(0.25,0.7,rk)); hgt=n4*0.02+n2*0.03; rough=0.95;
  vec3 mud=mix(vec3(0.20,0.14,0.08),vec3(0.34,0.25,0.15),n2)*(0.8+0.4*n4); col=mix(col,mud,sst(0.05,0.45,rm));
  if(rm>0.45){
    float rowH=0.42; float row=floor(z/rowH); float cu=(x-roadX(z))/0.55+(mod(row,2.0)>0.5?0.5:0.0); float fu=cu-floor(cu), fv=z/rowH-row;
    float edge=min(min(fu,1.0-fu)*0.55,min(fv,1.0-fv)*rowH); float st=hash(vec2(floor(cu),row)); float bev=sst(0.0,0.06,edge);
    vec3 c=mix(vec3(0.38,0.36,0.33),vec3(0.62,0.59,0.52),st)*(0.85+0.3*n4)*(0.6+0.4*bev); float m=sst(0.45,0.8,rm);
    col=mix(col,mix(mud*0.55,c,sst(0.015,0.045,edge)),m); hgt=mix(hgt,bev*0.05+n4*0.01,m); rough=mix(rough,0.82,m); }
  return col; }
void main(){
  vec3 alb=uBase.rgb; float rough=0.7, met=0.0; vec3 N=normalize(vN); vec3 V=normalize(uCam-vWP); vec3 em=vec3(0.0);
  if(uGround==1){ float h,r; alb=terrain(vWP,h,r); rough=r;
    vec3 dpx=dFdx(vWP), dpy=dFdy(vWP); float dhx=dFdx(h), dhy=dFdy(h); vec3 r1=cross(dpy,N), r2=cross(N,dpx); float det=dot(dpx,r1);
    vec3 grad=sign(det)*(dhx*r1+dhy*r2); N=normalize(abs(det)*N-grad*0.9); }
  else {
    if(uHas.x>0.5) alb=pow(texture(uAlb,vUV).rgb,vec3(2.2))*uBase.rgb;
    if(uHas.z>0.5){ vec3 mr=texture(uMR,vUV).rgb; rough=clamp(mr.g,0.05,1.0); met=mr.b; }
    if(dot(N,V)<0.0) N=-N;
    if(uHas.y>0.5){ vec3 T=normalize(vT.xyz); T=normalize(T-N*dot(N,T)); vec3 B=cross(N,T)*vT.w; vec3 t=texture(uNrm,vUV).xyz*2.0-1.0; N=normalize(T*t.x+B*t.y+N*t.z); }
    if(uHas.w>0.5) em=pow(texture(uEm,vUV).rgb,vec3(2.2))*uEmF*uEmBoost; }
  alb*=uTint; vec3 Ng=normalize(vN);
  float sh=shadowAt(vWP,uGround==1?normalize(vN):(dot(Ng,V)<0.0?-Ng:Ng));
  vec3 sunCol=vec3(3.4,2.5,1.55); vec3 col=brdf(N,V,uSun,sunCol*sh,alb,rough,met);
  // horizon ambient occlusion: contact darkening near the base of structures/characters, hemispheric sky/ground bounce
  float ao=(uGround==1)?1.0:mix(0.55,1.0,smoothstep(0.0,2.2,vWP.y-uBaseY));
  vec3 amb=mix(vec3(0.10,0.075,0.05),uZenith*0.55+uHoriz*0.12,N.y*0.5+0.5);
  col+=alb*amb*(1.0-met*0.6)*ao+mix(vec3(0.0),uHoriz*0.2,pow(1.0-max(dot(N,V),0.0),3.0))*(0.3+met)*ao;
  for(int i=0;i<uNL;i++){ vec3 d=uLP[i]-vWP; float dist=length(d); float att=clamp(1.0-pow(dist/uLR[i],2.0),0.0,1.0); att*=att/(1.0+dist*dist*0.35);
    col+=brdf(N,V,d/dist,uLC[i]*att,alb,rough,met); }
  col+=em; float dist=length(uCam-vWP); float fog=1.0-exp(-pow(dist*0.011,1.3));
  float sunAmt=pow(max(dot(normalize(vWP-uCam),uSun),0.0),4.0); vec3 fogC=mix(uHoriz*0.8,vec3(1.0,0.72,0.45),sunAmt*0.6);
  col=mix(col,fogC,clamp(fog,0.0,1.0)); col=aces(col*0.8); oC=vec4(pow(col,vec3(1.0/2.2)),uBase.a); })";
static const char* kSkyVS = R"(#version 330 core
out vec2 vP; void main(){ vec2 p=vec2((gl_VertexID<<1)&2,gl_VertexID&2); vP=p*2.0-1.0; gl_Position=vec4(vP,0.9999,1.0); })";
static const char* kSkyFS = R"(#version 330 core
in vec2 vP; out vec4 oC; uniform vec3 uF; uniform vec3 uR; uniform vec3 uU; uniform vec2 uTan; uniform vec3 uHoriz; uniform vec3 uZenith; uniform vec3 uSun;
float hash(vec2 p){ return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
float vnoise(vec2 p){ vec2 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f); return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+vec2(1,1)),f.x),f.y); }
void main(){ vec3 d=normalize(uF+vP.x*uTan.x*uR+vP.y*uTan.y*uU); float h=clamp(d.y,0.0,1.0); float mu=max(dot(d,uSun),0.0);
  vec3 c=mix(uHoriz*0.95,uZenith,pow(h,0.5));                                  // Rayleigh-like zenith blue
  c+=vec3(1.0,0.45,0.18)*exp(-abs(d.y)*7.0)*(0.25+0.9*pow(mu,3.0));              // golden horizon scattering band
  c+=vec3(1.0,0.75,0.45)*(pow(mu,8.0)*0.35+pow(mu,120.0)*2.2);                  // Mie sun halo + disc
  if(d.y>0.02){ vec2 q=d.xz/(d.y+0.25)*2.2; float cl=clamp((vnoise(q*vec2(1.3,2.5))*0.7+vnoise(q*vec2(3.0,5.0))*0.3-0.52)*3.0,0.0,1.0)*smoothstep(0.02,0.3,d.y)*0.55; c=mix(c,vec3(1.0,0.78,0.6)*1.1+vec3(0.1,0.05,0.0)*mu,cl); }
  if(d.y<0.0) c=mix(c,uHoriz*0.8,clamp(1.0+d.y*4.0,0.0,1.0));
  c=c*0.62; c=clamp((c*(2.51*c+0.03))/(c*(2.43*c+0.59)+0.14),0.0,1.0); oC=vec4(pow(c,vec3(1.0/2.2)),1.0); })";
static const char* kHudVS = R"(#version 330 core
layout(location=0) in vec2 aP; layout(location=1) in vec2 aUV; layout(location=2) in vec4 aC; uniform vec2 uRes; out vec2 vUV; out vec4 vC;
void main(){ vUV=aUV; vC=aC; gl_Position=vec4(aP.x/uRes.x*2.0-1.0,1.0-aP.y/uRes.y*2.0,0.0,1.0); })";
static const char* kHudFS = R"(#version 330 core
in vec2 vUV; in vec4 vC; out vec4 oC; void main(){ vec4 c=vC; if(vUV.x<1.5){ float r=length(vUV); c.a*=pow(clamp(1.0-r,0.0,1.0),1.6); } oC=c; })";
}  // namespace isekai
