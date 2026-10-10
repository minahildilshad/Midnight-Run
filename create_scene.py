import json, math
from pathlib import Path
root=Path(__file__).parent
meshes=[]
def mesh(name,verts,faces,color,glow=False):
 meshes.append(dict(name=name,verts=verts,faces=faces,color=color,glow=glow))
def box(name,center,size,color,glow=False):
 x,y,z=center;a,b,c=[v/2 for v in size]
 vs=[[x+sx*a,y+sy*b,z+sz*c] for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 mesh(name,vs,[[0,3,2,1],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7],[4,5,6,7]],color,glow)
def profile(name,rings,color):
 vs=[]
 for x,w,low,high in rings:
  vs.extend([[x,-w,low],[x,w,low],[x,w,high],[x,-w,high]])
 fs=[[3,2,1,0]]
 for j in range(len(rings)-1):
  for k in range(4):fs.append([j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k])
 fs.append(list(range(len(vs)-4,len(vs))))
 mesh(name,vs,fs,color)
def cylinder(name,x,y,z,r,depth,color,n=32):
 vs=[[x+r*math.cos(a*2*math.pi/n),y+d,z+r*math.sin(a*2*math.pi/n)] for d in [-depth/2,depth/2] for a in range(n)]
 fs=[list(range(n-1,-1,-1)),list(range(n,n*2))]
 fs.extend([[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)])
 mesh(name,vs,[list(reversed(f)) for f in fs],color)
paint=[.29,.045,.105];dark=[.025,.028,.045];glass=[.035,.10,.15];metal=[.5,.57,.65]
profile('Sculpted coupe body',[(-2.15,.78,.35,.65),(-1.8,.99,.35,.84),(-.95,1,.35,.91),(.7,1,.35,.89),(1.7,.95,.35,.7),(2.18,.83,.38,.61)],paint)
profile('Cabin',[(-1.22,.85,.86,.9),(-.68,.72,.9,1.49),(.38,.69,.88,1.5),(1.14,.85,.87,.91)],glass)
profile('Roof',[(-.69,.72,1.47,1.51),(.39,.69,1.48,1.52)],[.37,.065,.13])
for sign in [-1,1]:
 y=sign
 # Thin window pillars, handles and sculpted lower sill.
 box('B pillar '+str(sign),(-.1,y*.754,1.19),(.075,.036,.54),paint)
 box('Door handle '+str(sign),(-.48,y*1.008,.77),(.22,.025,.036),metal)
 box('Side skirt '+str(sign),(0,y*1.016,.36),(3.32,.075,.095),dark)
 box('Mirror '+str(sign),(.76,y*1.12,1.02),(.31,.22,.15),paint)
 box('Front LED '+str(sign),(2.187,y*.58,.59),(.022,.48,.065),[.7,.94,1],True)
 box('Rear LED '+str(sign),(-2.158,y*.53,.61),(.023,.48,.055),[1,.035,.08],True)
 for x in [-1.36,1.39]:
  cylinder('Tire',x,y*1.0,.47,.455,.26,[.012,.015,.022])
  cylinder('Alloy',x,y*1.145,.47,.324,.024,[.10,.13,.18])
  cylinder('Hub',x,y*1.17,.47,.085,.028,metal,16)
  for k in range(8):
   a=k*math.pi/4;v=[]
   for r,b in [(.09,a-.16),(.31,a-.09),(.31,a+.09),(.09,a+.16)]:v.append([x+r*math.cos(b),y*1.173,.47+r*math.sin(b)])
   mesh('Spoke',v,[[0,1,2,3]],metal)
box('Front grille',(2.2,0,.425),(.026,1.02,.14),dark)
box('Splitter',(2.18,0,.31),(.14,1.79,.055),[.06,.07,.09])
box('Rear diffuser',(-2.18,0,.32),(.12,1.6,.07),dark)
for y in [-.64,.64]:cylinder('Exhaust',-2.2,y,.39,.06,.12,metal,16)
box('Rear spoiler',(-1.93,0,.97),(.29,1.87,.055),dark)
for y in [-.67,.67]:box('Spoiler support',(-1.88,y,.87),(.055,.055,.2),dark)
box('Hood accent',(1.5,0,.77),(1.08,.06,.018),[.55,.12,.2])
root.joinpath('scene.json').write_text(json.dumps(meshes))
print('Created',len(meshes),'car components')
