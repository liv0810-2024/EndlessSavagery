"""Repair animation exports and render full-cycle previews. No gameplay edits."""
from pathlib import Path
import math
import bpy
from mathutils import Vector, Quaternion

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'ArtSource'

def rotate(arm, name, angle, axis=(1,0,0)):
    b=arm.pose.bones.get(name)
    if b:
        b.rotation_mode='QUATERNION'
        b.rotation_quaternion=Quaternion(b.bone.matrix_local.to_quaternion().inverted() @ Vector(axis), angle)

def reset(arm):
    for b in arm.pose.bones:
        b.rotation_mode='QUATERNION'; b.rotation_quaternion=Quaternion(); b.location=(0,0,0); b.scale=(1,1,1)

def animate(arm, name, count, pose):
    arm.animation_data_clear()
    for a in list(bpy.data.actions): bpy.data.actions.remove(a)
    action=bpy.data.actions.new(name); action.use_fake_user=True
    arm.animation_data_create(); arm.animation_data.action=action
    for f in range(count+1):
        reset(arm); pose(f/count)
        for b in arm.pose.bones:
            for prop in ('rotation_quaternion','location','scale'):
                b.keyframe_insert(prop,frame=f+1,group=b.name)
    bpy.context.scene.render.fps=30
    bpy.context.scene.frame_start=1; bpy.context.scene.frame_end=count+1
    bpy.context.scene.frame_set(1)

def export(path, objects):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'ARMATURE','MESH','EMPTY'},
        axis_forward='-Z',axis_up='Y',apply_scale_options='FBX_SCALE_ALL',add_leaf_bones=False,
        bake_anim=True,bake_anim_use_all_actions=False,bake_anim_use_nla_strips=False,
        bake_anim_simplify_factor=0,bake_anim_step=1,path_mode='COPY',embed_textures=True)

def studio(size, target):
    for o in list(bpy.data.objects):
        if o.type in {'CAMERA','LIGHT'}:bpy.data.objects.remove(o,do_unlink=True)
    scene=bpy.context.scene
    scene.world=bpy.data.worlds.new('DeliveryStudio')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.07,.08,.11,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.45
    bpy.ops.object.camera_add(location=Vector(target)+Vector((4,-6,4.3)))
    cam=bpy.context.object;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.type='ORTHO';cam.data.ortho_scale=size;scene.camera=cam
    for loc,energy,color in [((3,-4,6),650,(1,.87,.72)),((-4,-1,3),480,(.55,.65,1)),((2,4,5),900,(.6,.3,1))]:
        bpy.ops.object.light_add(type='AREA',location=loc)
        l=bpy.context.object;l.data.energy=energy;l.data.color=color;l.data.shape='DISK';l.data.size=4
        l.rotation_euler=(Vector(target)-l.location).to_track_quat('-Z','Y').to_euler()
    scene.render.engine='CYCLES';scene.cycles.samples=16
    scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='AgX'

def save_preview(folder, stem, count):
    bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene;scene.frame_set(1)
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/(stem+'.blend')))
    frames=folder/'PreviewFrames';frames.mkdir(exist_ok=True)
    for f in range(1,count+1):
        scene.frame_set(f);scene.render.filepath=str(frames/f'{f:03}.png');bpy.ops.render.render(write_still=True)

def monsters():
    for name,count in [('WildernessSlime',24),('ShadowWolf',18),('StoneGuardian',30)]:
        folder=ART/'Monsters'/name
        bpy.ops.wm.open_mainfile(filepath=str(folder/(name+'.blend')))
        arm=next(o for o in bpy.data.objects if o.type=='ARMATURE')
        def pose(t):
            p=t*2*math.pi;s=math.sin(p)
            if name=='WildernessSlime':
                arm.pose.bones['Body'].scale=(1+.07*s,1+.07*s,1-.11*s)
                rotate(arm,'Body',.06*s)
                rotate(arm,'Core',.12*s,axis=(0,0,1))
            elif name=='ShadowWolf':
                rotate(arm,'Spine',.045*s,axis=(0,0,1));rotate(arm,'Head',.04*math.sin(2*p))
                rotate(arm,'Tail',.12*s,axis=(0,0,1))
                for side,sign in [('L',1),('R',-1)]:
                    for leg,offset in [('Front',0),('Rear',math.pi)]:
                        step=sign*math.sin(p+offset)
                        rotate(arm,f'{leg}Leg.{side}',.32*step)
                        b=arm.pose.bones[f'{leg}Leg.{side}']
                        b.location=b.bone.matrix_local.to_quaternion().inverted() @ Vector((0,0,.065*max(0,step)))
            else:
                rotate(arm,'Hips',.025*s,axis=(0,0,1));rotate(arm,'Chest',-.02*s,axis=(0,0,1))
                for side,sign in [('L',1),('R',-1)]:
                    rotate(arm,f'Leg.{side}',.20*sign*s)
                    rotate(arm,f'Arm.{side}',-.17*sign*s)
        animate(arm,name+'_Walk',count,pose)
        meshes=[o for o in bpy.data.objects if o.type=='MESH']
        export(ROOT/'Assets'/'Characters'/'Monsters'/name/(name+'_Animated.fbx'),[arm]+meshes)
        studio(2.2 if name=='WildernessSlime' else 3.5,(0,0,.5 if name=='WildernessSlime' else 1))
        save_preview(folder,name,count)

def dash():
    folder=ART/'AshenWatcher'
    bpy.ops.wm.open_mainfile(filepath=str(folder/'AshenWatcher.blend'))
    arm=bpy.data.objects['AshenWatcher_Rig']
    # Use the original rig axes, not pose-local axes interpreted as world axes.
    def pose(t):
        envelope=math.sin(math.pi*t)**.65
        lean=.42*envelope
        rotate(arm,'Hips',.12*envelope);rotate(arm,'Spine',lean*.65);rotate(arm,'Chest',lean*.35)
        rotate(arm,'Head',-.23*envelope)
        for side,sign in [('L',1),('R',-1)]:
            rotate(arm,'Thigh.'+side,sign*.4*envelope)
            rotate(arm,'Shin.'+side,-.28*envelope)
            rotate(arm,'Foot.'+side,.12*envelope)
            rotate(arm,'UpperArm.'+side,-sign*.42*envelope)
            rotate(arm,'Forearm.'+side,.20*envelope)
            rotate(arm,'Cape.'+side,.27*envelope)
            rotate(arm,'CapeSide.'+side,.2*envelope)
        rotate(arm,'Cape.Center',.3*envelope)
    animate(arm,'AshenWatcher_Dash',18,pose)
    # Meshes are parented to the model empty, with armature modifiers: include them.
    meshes=[o for o in bpy.data.objects if o.type=='MESH' and any(m.type=='ARMATURE' and m.object==arm for m in o.modifiers)]
    assert meshes,'No skinned player meshes'
    export(ROOT/'Assets/Characters/AshenWatcher/AshenWatcher_Dash.fbx',[arm]+meshes)
    studio(3,(0,0,1))
    save_preview(folder,'AshenWatcher_Dash',18)

def material(name,color,emission=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1)
    n.inputs['Metallic'].default_value=.7 if not emission else .15
    n.inputs['Roughness'].default_value=.35
    if emission:
        n.inputs['Emission Color'].default_value=(*color,1);n.inputs['Emission Strength'].default_value=emission
    return m

def orbit():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    folder=ART/'VFX/PlayerOrbitBlades'
    bronze=material('Orbit_Bronze',(.3,.15,.055))
    violet=material('Orbit_Blade',(.42,.12,1),2)
    white=material('Orbit_Edge',(.8,.5,1),3)
    trail=material('Orbit_Trail',(.17,.035,.45),1)
    root=bpy.data.objects.new('PlayerOrbitBlades_Model',None);bpy.context.collection.objects.link(root)
    pivot=bpy.data.objects.new('OrbitPivot',None);bpy.context.collection.objects.link(pivot);pivot.parent=root
    def ribbon(name,start,span,outer,width,mat,fade=False):
        vs=[];fs=[];cols=[]
        for j in range(33):
            t=j/32;a=start-span*(1-t)
            w=width*math.sin(math.pi*t)**.8
            for r in (outer-w,outer):vs.append((r*math.cos(a),r*math.sin(a),.65))
            cols.extend([(1,1,1,t*.55 if fade else 1)]*2)
        for j in range(32):fs.append((j*2,j*2+1,j*2+3,j*2+2))
        me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
        c=me.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
        for d,v in zip(c.data,cols):d.color=v
        o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.parent=pivot;me.materials.append(mat)
        return o
    for i in range(4):
        a=i*math.pi/2
        ribbon(f'ArcBlade_{i+1}',a,.65,2.48,.26,violet)
        ribbon(f'BladeEdge_{i+1}',a,.65,2.49,.035,white)
        ribbon(f'TaperedTrail_{i+1}',a-.52,1.0,2.40,.19,trail,True)
        for offset,sz in [(0,(.16,.25,.065)),(.13,(.075,.22,.045)),(-.13,(.075,.22,.045))]:
            angle=a-.36
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=((2.22+offset)*math.cos(angle),(2.22+offset)*math.sin(angle),.65))
            o=bpy.context.object;o.name=f'BronzeMount_{i+1}';o.scale=sz;o.rotation_euler[2]=angle
            bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.parent=pivot;o.data.materials.append(bronze)
    scene=bpy.context.scene;scene.render.fps=30;scene.frame_start=1;scene.frame_end=25
    for f in range(25):
        pivot.rotation_euler[2]=2*math.pi*f/24;pivot.keyframe_insert('rotation_euler',frame=f+1,index=2)
    pivot.animation_data.action.name='PlayerOrbitBlades_Orbit'
    scene.frame_set(1)
    export(ROOT/'Assets/VFX/PlayerOrbitBlades/PlayerOrbitBlades.fbx',[root,pivot]+[o for o in bpy.data.objects if o.type=='MESH'])
    studio(6.3,(0,0,.5));save_preview(folder,'PlayerOrbitBlades',24)

if __name__=='__main__':
    monsters();dash();orbit();print('REPAIRED_COMBAT_EXPORTS_COMPLETE')
