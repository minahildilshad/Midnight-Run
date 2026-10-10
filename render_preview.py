import json, math, subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
from pathlib import Path
root=Path(__file__).parent;out=root.parent/'deliverables';out.mkdir(exist_ok=True)
W,H=960,540;S=1.5;RW,RH=int(W*S),int(H*S);FPS=24;N=192
meshes=json.loads(root.joinpath('scene.json').read_text())
def camera(t):
 # Ease through a wide front reveal into a close side/rear orbit.
 u=t/8;a=math.radians(-32-122*(u*u*(3-2*u)));r=7.15-.65*math.sin(u*math.pi)
 eye=np.array([r*math.cos(a),r*math.sin(a),2.45+.3*math.sin(u*math.pi)])
 target=np.array([0,0,.73]);f=target-eye;f/=np.linalg.norm(f)
 right=np.cross(f,[0,0,1]);right/=np.linalg.norm(right);up=np.cross(right,f)
 return eye,np.array([right,up,f])
def project(v,eye,mat):
 p=(np.array(v)-eye)@mat.T;z=p[:,2]
 return np.column_stack((RW*.5+p[:,0]/z*RW*.91,RH*.46-p[:,1]/z*RW*.91)),z
def font(size):
 return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',int(size*S))
titlefont=font(22);smallfont=font(9);largefont=font(43)
yy,xx=np.mgrid[0:RH,0:RW];g=np.exp(-((xx-RW*.65)**2/(RW*.55)**2+(yy-RH*.28)**2/(RH*.65)**2))
bg=np.stack([8+g*15,10+g*12,20+g*27],axis=2).astype('uint8')
vignette=np.clip(1-.5*((xx-RW/2)**2/(RW*.7)**2+(yy-RH/2)**2/(RH*.8)**2),.45,1)
light=np.array([.3,-.65,1.]);light/=np.linalg.norm(light)
def render(t):
 eye,mat=camera(t);im=Image.fromarray(bg.copy());draw=ImageDraw.Draw(im);glow=Image.new('RGB',(RW,RH));gd=ImageDraw.Draw(glow)
 # Road plane and long runway lines.
 q,z=project([[-120,-8,0],[120,-8,0],[120,8,0],[-120,8,0]],eye,mat)
 # Fill floor below perspective horizon without projecting behind the camera.
 draw.rectangle((0,RH*.5,RW,RH),fill=(12,15,24))
 for y,c in [(-3,(54,115,153)),(3,(161,43,104)),(-5,(28,45,70)),(5,(28,45,70))]:
  points=[]
  for x in np.linspace(-70,70,150):
   p,z=project([[x,y,.008]],eye,mat)
   if z[0]>.8:points.append(tuple(p[0]))
  if len(points)>1:draw.line(points,fill=c,width=2);gd.line(points,fill=c,width=4)
 # White dashes stream under the stationary tracked car.
 offset=(t*7)%6
 for x in np.arange(-50,50,6):
  for y in [-1.9,1.9]:
   p,z=project([[x+offset,y,.01],[x+offset+1.7,y,.01]],eye,mat)
   if min(z)>.8:draw.line([tuple(v) for v in p],fill=(64,71,86),width=3)
 # Soft contact shadow, drawn before the vehicle.
 p,z=project([[2.5*math.cos(a),1.35*math.sin(a),.025] for a in np.linspace(0,math.pi*2,60)],eye,mat)
 shadow=Image.new('RGBA',(RW,RH));sd=ImageDraw.Draw(shadow);sd.polygon([tuple(v) for v in p],fill=(0,0,0,155));shadow=shadow.filter(ImageFilter.GaussianBlur(12*S));im=Image.alpha_composite(im.convert('RGBA'),shadow).convert('RGB');draw=ImageDraw.Draw(im)
 faces=[]
 for m in meshes:
  verts=np.array(m['verts'],dtype=float)
  # Wheel spokes rotate about their local axle.
  if m['name']=='Spoke':
   cx=1.39 if verts[:,0].mean()>0 else -1.36;a=-t*7/.455;c,s=math.cos(a),math.sin(a);dx=verts[:,0]-cx;dz=verts[:,2]-.47;verts[:,0]=cx+dx*c-dz*s;verts[:,2]=.47+dx*s+dz*c
  if m['name']=='Spoke' and eye[1]*verts[:,1].mean()<0:continue
  p,z=project(verts,eye,mat)
  for f in m['faces']:
   if min(z[f])<.2:continue
   v=verts[f];n=np.cross(v[1]-v[0],v[2]-v[0]);norm=np.linalg.norm(n)
   if norm<1e-9:continue
   n/=norm
   if np.dot(n,eye-v.mean(axis=0))<0:
    if m['name']!='Spoke':continue
    n=-n
   base=np.array(m['color']);shade=.36+.62*max(0,float(np.dot(n,light)))
   view=eye-v.mean(axis=0);view/=np.linalg.norm(view);halfv=light+view;halfv/=np.linalg.norm(halfv)
   spec=max(0,float(np.dot(n,halfv)))**45
   if m['glow']:col=np.minimum(255,base*255)
   else:col=np.minimum(255,base*255*shade+spec*110+np.array([8,9,18])*max(0,1-n[2])*.45)
   faces.append((-1 if m['name']=='Spoke' else z[f].mean(),[tuple(v) for v in p[f]],tuple(col.astype(int)),m['glow']))
 faces.sort(key=lambda f:-f[0])
 for depth,p,col,emit in faces:
  draw.polygon(p,fill=col)
  if emit:gd.polygon(p,fill=col)
 # Local light bloom and subtle photographic vignette.
 bloom=glow.filter(ImageFilter.GaussianBlur(10*S));arr=np.asarray(im).astype(float)+np.asarray(bloom)*.7;arr=np.clip(arr*vignette[:,:,None],0,255).astype('uint8');im=Image.fromarray(arr);draw=ImageDraw.Draw(im)
 draw.text((44*S,35*S),'M I D N I G H T   R U N',font=titlefont,fill=(228,224,233));draw.text((45*S,70*S),'A  S T U D Y  I N  M O T I O N',font=smallfont,fill=(142,145,169))
 draw.line((45*S,102*S,99*S,102*S),fill=(217,72,116),width=2)
 draw.text((45*S,468*S),'01  /  AFTER HOURS',font=smallfont,fill=(160,155,171));draw.text((788*S,468*S),'CGI MOTION STUDY',font=smallfont,fill=(160,155,171))
 # Letterbox, with a soft fade at the beginning and end.
 draw.rectangle((0,0,RW,15*S),fill=(4,5,10));draw.rectangle((0,RH-15*S,RW,RH),fill=(4,5,10))
 fade=min(1,t/.4,(8-t)/.45)
 if fade<1:im=Image.blend(Image.new('RGB',im.size,(4,5,10)),im,max(0,fade))
 return im.resize((W,H),Image.Resampling.LANCZOS)
if __name__=='__main__':
 import sys
 if '--still' in sys.argv:
  render(1.8).save(out/'Midnight_Run_Preview.png');print('Saved still');sys.exit()
 cmd=['ffmpeg','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(out/'Midnight_Run.mp4')]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
 for i in range(N):
  p.stdin.write(render(i/FPS).tobytes())
  if i%48==0:print(f'Rendered {i}/{N}',flush=True)
 p.stdin.close();assert p.wait()==0
 print('Rendered 8-second MP4',flush=True)
