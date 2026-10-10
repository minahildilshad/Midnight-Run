"""Run in Blender's Scripting workspace. Creates and saves a complete animated scene.
Keep scene.json next to this script. Blender 4.2+ or 5.x recommended.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
# When run in the Text Editor, use its filepath to locate scene.json.
text=bpy.context.space_data.text if bpy.context.space_data and bpy.context.space_data.type=='TEXT_EDITOR' else None
root=Path(bpy.path.abspath(text.filepath)).parent if text and text.filepath else Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=32
scene.render.resolution_x=1280;scene.render.resolution_y=720;scene.render.resolution_percentage=100
scene.render.fps=24;scene.frame_start=1;scene.frame_end=192
scene.world.color=(.025,.03,.055)
materials={}
def material(name,col,glow=False,metallic=0):
 key=(tuple(col),glow,metallic)
 if key in materials:return materials[key]
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True
 bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*col,1);bs.inputs['Metallic'].default_value=metallic;bs.inputs['Roughness'].default_value=.28 if metallic else .48
 if glow:
  bs.inputs['Emission Color'].default_value=(*col,1);bs.inputs['Emission Strength'].default_value=5
 materials[key]=m;return m
def cube(name,loc,scale,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(mat);return o
for item in json.loads(root.joinpath('scene.json').read_text()):
 data=bpy.data.meshes.new(item['name']);data.from_pydata(item['verts'],[],item['faces']);data.update()
 o=bpy.data.objects.new(item['name'],data);scene.collection.objects.link(o)
 o.data.materials.append(material(item['name'],item['color'],item['glow'],.7 if item['name'] not in ['Tire','Cabin'] else .15))
 bevel=o.modifiers.new('Soft manufactured edges','BEVEL');bevel.width=.025 if item['name']!='Spoke' else .004;bevel.segments=3
 if item['name']=='Spoke':
  cx=1.39 if sum(v[0] for v in item['verts'])/4>0 else -1.36
  for v in o.data.vertices:v.co-=Vector((cx,0,.47))
  o.location=(cx,0,.47)
  for frame in range(1,193):
   o.rotation_euler[1]=(frame-1)/24*7/.455;o.keyframe_insert(data_path='rotation_euler',frame=frame)
floor=material('Wet graphite',(.025,.032,.048),metallic=.6)
cube('Road',(0,0,-.11),(250,20,.2),floor)
for y,col in [(-3,(.15,.65,1)),(3,(1,.06,.26))]:
 cube('Neon runway',(0,y,.008),(240,.035,.015),material('Neon',col,True))
dashmat=material('Lane paint',(.27,.31,.4))
for x in range(-60,61,6):
 for y in [-1.9,1.9]:
  o=cube('Moving lane marker',(x,y,.008),(1.7,.06,.01),dashmat)
  for frame in range(1,193):
   o.location.x=x+((frame-1)/24*7)%6;o.keyframe_insert(data_path='location',frame=frame)
def area(name,loc,power,color,size):
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
area('Cool softbox',(3,-4,6),1500,(.65,.8,1),5)
area('Magenta rim',(-3,3,3),1900,(1,.15,.37),4)
area('Overhead strip',(0,0,6),1100,(1,.87,.76),3)
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='Cinematic orbit';scene.camera=cam;cam.data.lens=36
cam.data.dof.use_dof=True;cam.data.dof.aperture_fstop=5.6
bpy.ops.object.empty_add(location=(0,0,.73));target=bpy.context.object;target.name='Camera focus';cam.data.dof.focus_object=target
for frame in range(1,193):
 t=(frame-1)/24;u=t/8;a=math.radians(-32-122*(u*u*(3-2*u)));r=7.15-.65*math.sin(u*math.pi)
 cam.location=(r*math.cos(a),r*math.sin(a),2.45+.3*math.sin(u*math.pi));cam.rotation_euler=(target.location-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.keyframe_insert(data_path='location',frame=frame);cam.keyframe_insert(data_path='rotation_euler',frame=frame)
# PNG sequence is robust across Blender versions. Encode with the README command.
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(root/'frames'/'frame_')
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(root/'Midnight_Run.blend'))
print('Scene ready. Use Render > Render Animation to produce the PNG frames.')
