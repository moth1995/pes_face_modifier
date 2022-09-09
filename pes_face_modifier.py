
bl_info = {
    "name": "PES/WE/JL PC/PS2/PSP and PES2013 PC Face/Hair Modifier Tool",
    "author": "PES Indie Team / Suat CAGDAS  'sxsxsx'",
    "version": (2,0),
    "blender": (2, 6, 7),
    "api": 35853,
    "location": "Under Scene Tab",
    "description": "Import/Export PES/WE/JL PC/PS2/PSP and PES13 PC Face/Hair Model",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "System"}

import bpy,bmesh,zlib,os,struct
from array import array
from bpy.props import *

bpy.types.Scene.face_path = StringProperty(name="Face File",subtype='FILE_PATH',default="Select the Face BIN File from here   --->")
bpy.types.Scene.hair_path = StringProperty(name="Hair File",subtype='FILE_PATH',default="Select the Hair BIN File from here   --->")
bpy.types.Scene.ks_path = StringProperty(name="",subtype='DIR_PATH',default="Set Kitserver dt0c.img Folder from here -->")
bpy.types.Scene.pes_ver = EnumProperty(name="Select PES Version",items=[("pes13","PES 2013 PC"," "), ("pes_psp","PES/WE PSP"," "), ("pes_ps2","PES/WE PS2"," "), ("pes_pc","PES/WE PC"," ")], default="pes_pc")
bpy.types.Scene.uv_sw = BoolProperty(name="", default=False)
bpy.types.Scene.face_vc = IntProperty(name="", default=0)
bpy.types.Scene.hair_vc = IntProperty(name="", default=0) 
tool_id="PES/WE/JL PC/PS2/PSP and PES13 PC Face/Hair Modifier Tool v2.0 - Blender v2.67"
facepath,hairpath,face_id,hair_id = "","","",""
temp_folder = bpy.app[4].split('blender.exe')[0]+'pes_temp\\'
DDSPATH = bpy.app[4].split('blender.exe')[0]+'pes_temp\\nvidia_dds.exe'
DDSPATH = '"'+DDSPATH+'"'
bump = temp_folder+"def_bump.dll"
face_temp = temp_folder+"face_unzlib_temp"
imp_face_dds = temp_folder+"face_tex.dds"
hair_temp = temp_folder+"hair_unzlib_temp"
imp_hair_dds = temp_folder+"hair_tex.dds"
plist,f_plist,h_plist,h_start,f_start,start=[],[],[],0,0,0
pes6f_voff,pes6h_voff,pes6_vc,pes6_vs=0,0,0,0
pes_ps2_f_voff,pes_ps2_h_voff,pes_ps2_vc,pes_ps2_vs = 0, 0, 0, 0
pes_psp_f_voff,pes_psp_h_voff,pes_psp_vc,pes_psp_vs = 0, 0, 0, 0
def unzlib(model):
    
    if model == 'face':
        filepath_imp=facepath
        temp=face_temp
    else:
        filepath_imp=hairpath
        temp=hair_temp
        
    data1 = open(filepath_imp, 'rb')
    data1.seek(16,0)
    if bpy.context.scene.pes_ver == "pes_pc" or bpy.context.scene.pes_ver == "pes_ps2" or bpy.context.scene.pes_ver == "pes_psp":
        data1.seek(16,1)  
    data2=data1.read()
    data3=zlib.decompress(data2,32)
    out=open(temp,"wb")
    out.write(data3)
    out.flush()
    out.close()
    
    return open(temp,"rb")

def zlib_comp(self,model):
    
    if model == 'face':
        filepath_exp=facepath
        temp=face_temp
    else:
        filepath_exp=hairpath
        temp=hair_temp
    
    exp1=open(temp, 'rb').read()
    exp2=zlib.compress(exp1,9)
    s1,s2=len(exp1),len(exp2)
    exp=open(filepath_exp,"wb")
    if bpy.context.scene.pes_ver == 'pes13':
        exp.write(struct.pack("I",0x57010100))
        exp.write(struct.pack("4s","ESYS".encode()))
    else:
        exp.write(struct.pack("I",0x00010600))
    exp.write(struct.pack("I",s2))
    exp.write(struct.pack("I",s1))
    if bpy.context.scene.pes_ver == "pes_pc" or bpy.context.scene.pes_ver == "pes_ps2" or bpy.context.scene.pes_ver == "pes_psp":
        exp.write(struct.pack("20s","".encode()))
    exp.write(exp2)
    copyright = "Made by Suat CAGDAS 'sxsxsx'"
    if bpy.context.scene.pes_ver == "pes_pc" or bpy.context.scene.pes_ver == "pes_ps2" or bpy.context.scene.pes_ver == "pes_psp":
        exp.write(struct.pack("16s","".encode()))
        copyright = "Made by PES Indie Team"
    exp.write(struct.pack("I50sI28s",0,
                              tool_id.encode(),
                              0,copyright.encode()))
    exp.flush()
    exp.close()

def pes_psp_exp(self,model):
    
    global pes_psp_f_voff,pes_psp_h_voff,pes_psp_vc,pes_psp_vs

    if model == 'face':
        temp=face_temp
        obname='PES_PSP_Face'
        pes_psp_vc=bpy.context.scene.face_vc
        pes_psp_voff=pes_psp_f_voff
    else:
        temp=hair_temp
        obname='PES_PSP_Hair'
        pes_psp_vc=bpy.context.scene.hair_vc
        pes_psp_voff=pes_psp_h_voff

    ### Export Model ###

    ex6_file=open(temp,"r+b")

    for ob in bpy.data.objects:
        if ob.name[:9] == obname:
            if ob.hide == 0:
                bpy.context.scene.objects.active=ob

    ac_ob=bpy.context.active_object
    data=ac_ob.data

    if len(data.vertices) != pes_psp_vc:
        print("")
        self.report( {"ERROR"}, "Vertex Count is Not Equal with Base Model !!\nDont delete or add any vertices !!\nTry Import again Base Model !!\nInfo: Base Model is always last imported model...  " )
        return 0

    uvlayer=data.uv_layers.active.data 
    vidx_list,exp_uvlist=[],[]

    for poly in data.polygons:
        for idx in range(poly.loop_start, poly.loop_start + poly.loop_total):
            if data.loops[idx].vertex_index not in vidx_list:
                vidx_list.append(data.loops[idx].vertex_index)
                exp_uvlist.append((uvlayer[idx].uv[0],uvlayer[idx].uv[1]))

    ex6_file.seek(8,0)
    offset_file_1 = struct.unpack("<I", ex6_file.read(4))[0]
    parts_info_offset = 32
    vertex_in_part_offset = 72
    ex6_file.seek(offset_file_1 + parts_info_offset,0)
    total_parts, part_start_offset = struct.unpack("<II", ex6_file.read(8))
    part_start_offset += offset_file_1
    factor = -0.001553
    factor_uv = 0.000244
    i = 0
    vertex_count = 0
    while i < total_parts:
        #print("part ",i, " offset: ", part_start_offset)
        ex6_file.seek(part_start_offset,0)
        part_size = struct.unpack("<I", ex6_file.read(4))[0]

        ex6_file.seek(4,1)
        vertex_start_address = struct.unpack("<I", ex6_file.read(4))[0]
        ex6_file.read(8)
        vertex_start_address += part_start_offset
        ex6_file.seek(vertex_in_part_offset,1)

        vertex_in_piece = struct.unpack("<H", ex6_file.read(2))[0]
        ex6_file.seek(vertex_start_address, 0)

        for j in range(vertex_in_piece):
            x,y,z=data.vertices[vertex_count + j].co
            x,y,z = round(x/factor*-1), round(y/factor), round((z)/factor)
            for t in vidx_list:
                if t == j + vertex_count:
                    u,v = exp_uvlist[vidx_list.index(t)][0],exp_uvlist[vidx_list.index(t)][1]
                    u, v = round((u)/factor_uv), round((1 - v) / factor_uv)
                    ex6_file.write(struct.pack("2h",u,v))
                    ex6_file.read(4)
                    ex6_file.write(struct.pack("3h",y,z,x))

        part_start_offset += part_size
        i += 1
        vertex_count += vertex_in_piece

    ex6_file.flush()
    ex6_file.close()

    zlib_comp(self,model)

    return 1

def pes_psp_imp(self,context,model):
    
    if model == 'face':
        obname="PES_PSP_Face"
        imgfile=facepath        
    else:
        obname="PES_PSP_Hair"
        imgfile=hairpath
        
    global pes_psp_h_voff,pes_psp_f_voff,pes_psp_vc,pes_psp_vs
    
    vlist,tlist,flist,edges,uvlist=[],[],[],[],[]
    
    file=unzlib(model) 
    
    file.seek(8,0)
    offset_file_1 = struct.unpack("<I", file.read(4))[0]
    parts_info_offset = 32
    vertex_in_part_offset = 72
    file.seek(offset_file_1 + parts_info_offset,0)
    total_parts, part_start_offset = struct.unpack("<II", file.read(8))
    part_start_offset += offset_file_1
    factor = -0.001553
    factor_uv = 0.000244
    i = 0
    vertex_count = 0
    aux_list = []
    while i < total_parts:
        #print("part ",i, " offset: ", part_start_offset)
        file.seek(part_start_offset,0)
        part_size = struct.unpack("<I", file.read(4))[0]

        file.seek(4,1)
        vertex_start_address, tri_start_address, tri_list_size = struct.unpack("<III", file.read(12))
        #file.seek(part_info_start + vertex_in_part_offset,1)
        vertex_start_address += part_start_offset
        if tri_start_address != 0:
            tri_start_address += part_start_offset
        file.seek(vertex_in_part_offset,1)

        vertex_in_piece = struct.unpack("<H", file.read(2))[0]
        file.seek(vertex_start_address, 0)
        for j in range(vertex_in_piece):
            u,v = struct.unpack("<hh", file.read(4))
            if u < 0: u = u + 32768
            if v < 0: v = v + 32768
            uvlist.append(((u) * factor_uv, 1 - (v) * factor_uv))
            file.read(4)
            y, z, x = struct.unpack("<hhh", file.read(6))
            vlist.append(((x * factor *-1), ((y * factor)), (z * factor)))

        #"""
        #if vertex_in_piece%2!=0:
            # if the number of vertes is not pair then we need to incress the movement of bytes by two
            #file.seek(2,1)
        # Skip normals
        #file.seek(4,1)
        #file.seek(vertex_in_piece*6,1)
        
        #if vertex_in_piece%2!=0:
            # if the number of vertes is not pair then we need to incress the movement of bytes by two
            #file.seek(2,1)
            
        #file.seek(4,1)
        #for j in range(vertex_in_piece):
        if tri_start_address != 0:
            file.seek(tri_start_address, 0)

            tri_data = file.read(tri_list_size * 2)
            tstrip_index_list = [idx + vertex_count for idx in struct.unpack("<%dH" % tri_list_size, tri_data)]
            for f in range(len(tstrip_index_list)-2):
                if (tstrip_index_list[f] != tstrip_index_list[f+1]) and (tstrip_index_list[f+1] != tstrip_index_list[f+2]) and (tstrip_index_list[f+2] != tstrip_index_list[f]):
                    flist.append((tstrip_index_list[f+2],tstrip_index_list[f+1],tstrip_index_list[f]))

        part_start_offset += part_size
        i += 1
        vertex_count += vertex_in_piece

    pes_psp_vc,pes_psp_vs=vertex_count,0
    if model == 'face':
        bpy.context.scene.face_vc=pes_psp_vc
        pes_psp_f_voff=0
    else:
        bpy.context.scene.hair_vc=pes_psp_vc
        pes_psp_h_voff=0
    
    file.flush()
    file.close()
    faces=flist
    mesh = bpy.data.meshes.new(obname)
    mesh.from_pydata(vlist, edges, faces)
    
    from bpy_extras import object_utils
    object_utils.object_data_add(context, mesh, operator=None)
    
    me=bpy.context.active_object.data
    bpy.ops.mesh.uv_texture_add('EXEC_SCREEN')
    bm = bmesh.new() 
    bm.from_mesh(me) 
    uv_layer = bm.loops.layers.uv.verify()
    
    for f in range(len(bm.faces)):
        for i in range(len(bm.faces[f].loops)):
            fuv=bm.faces[f].loops[i][uv_layer]
            fuv.uv = uvlist[faces[f][i]]
    bm.to_mesh(me)
    bm.free()
    
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.editmode_toggle()
    
    ac_ob=bpy.context.active_object
    ac_ob.location=(0,0,0)
    
    imgid=bpy.path.display_name_from_filepath(imgfile)+'.png'
    imgfile=imgfile[:-4]+'.png'
    
    if os.access(imgfile,0) == 1:
    
        bpy.ops.image.open(filepath=imgfile,relative_path=False)
        img=bpy.data.images[imgid]
        uvdata=me.uv_textures[0].data
        for face in uvdata:
            face.image=img
    
    add_mat(ac_ob,model)



def pes_ps2_exp(self,model):

    global pes_ps2_f_voff,pes_ps2_h_voff,pes_ps2_vc,pes_ps2_vs

    if model == 'face':
        temp=face_temp
        obname='PES_PS2_Face'
        pes_ps2_vc=bpy.context.scene.face_vc
        pes_ps2_voff=pes_ps2_f_voff
    else:
        temp=hair_temp
        obname='PES_PS2_Hair'
        pes_ps2_vc=bpy.context.scene.hair_vc
        pes_ps2_voff=pes_ps2_h_voff

    ### Export Model ###

    ex6_file=open(temp,"r+b")

    for ob in bpy.data.objects:
        if ob.name[:9] == obname:
            if ob.hide == 0:
                bpy.context.scene.objects.active=ob

    ac_ob=bpy.context.active_object
    data=ac_ob.data

    if len(data.vertices) != pes_ps2_vc:
        print("")
        self.report( {"ERROR"}, "Vertex Count is Not Equal with Base Model !!\nDont delete or add any vertices !!\nTry Import again Base Model !!\nInfo: Base Model is always last imported model...  " )
        return 0

    uvlayer=data.uv_layers.active.data 
    vidx_list,exp_uvlist=[],[]

    for poly in data.polygons:
        for idx in range(poly.loop_start, poly.loop_start + poly.loop_total):
            if data.loops[idx].vertex_index not in vidx_list:
                vidx_list.append(data.loops[idx].vertex_index)
                exp_uvlist.append((uvlayer[idx].uv[0],uvlayer[idx].uv[1]))

    ex6_file.seek(8,0)
    offset_file_1 = struct.unpack("<I", ex6_file.read(4))[0]
    parts_info_offset = 32
    vertex_in_part_offset = 88
    ex6_file.seek(offset_file_1 + parts_info_offset,0)
    total_parts, part_start_offset = struct.unpack("<II", ex6_file.read(8))
    part_start_offset += offset_file_1

    factor = -0.001553
    factor_uv = 0.000244 
    i = 0
    vertex_count = 0
    vertices_texture = []
    while i < total_parts:
        #print("part ",i, " offset: ", part_start_offset)
        ex6_file.seek(part_start_offset,0)
        part_size = struct.unpack("<I", ex6_file.read(4))[0]

        #print("part #", i)
        ex6_file.seek(4,1)
        part_info_start = struct.unpack("<I", ex6_file.read(4))[0]-12
        ex6_file.seek(part_info_start+vertex_in_part_offset,1)


        vertex_in_piece = struct.unpack("<I", ex6_file.read(4))[0]
        ex6_file.seek(8,1)
        for j in range(vertex_in_piece):
            x,y,z=data.vertices[vertex_count + j].co
            x,y,z = round(x/factor), round(y/factor), round((z)/factor)
            ex6_file.write(struct.pack("3h",y,z,x*-1))
            for t in vidx_list:
                if t == j + vertex_count:
                    u,v = exp_uvlist[vidx_list.index(t)][0],exp_uvlist[vidx_list.index(t)][1]
                    vertices_texture.append((u,v))

        #"""
        if vertex_in_piece%2!=0:
            # if the number of vertes is not pair then we need to incress the movement of bytes by two
            ex6_file.seek(2,1)
        # here we skip the normals
        ex6_file.seek(4,1)
        ex6_file.seek(vertex_in_piece*6,1)

        if vertex_in_piece%2!=0:
            # if the number of vertes is not pair then we need to incress the movement of bytes by two
            ex6_file.seek(2,1)

        ex6_file.seek(4,1)
        for j in range(vertex_in_piece):
            u, v = round((vertices_texture[vertex_count + j][0])/factor_uv), round((1 - vertices_texture[vertex_count + j][1]) / factor_uv)
            ex6_file.write(struct.pack("2h",u,v))

        part_start_offset += part_size
        i += 1
        vertex_count += vertex_in_piece

    ex6_file.flush()
    ex6_file.close()

    zlib_comp(self,model)

    return 1

def pes_ps2_imp(self,context,model):
    
    if model == 'face':
        obname="PES_PS2_Face"
        imgfile=facepath        
    else:
        obname="PES_PS2_Hair"
        imgfile=hairpath
        
    global pes_ps2_h_voff,pes_ps2_f_voff,pes_ps2_vc,pes_ps2_vs
    
    vlist,tlist,flist,edges,uvlist=[],[],[],[],[]
    
    file=unzlib(model) 
    
    file.seek(8,0)
    offset_file_1 = struct.unpack("<I", file.read(4))[0]
    parts_info_offset = 32
    vertex_in_part_offset = 88
    file.seek(offset_file_1 + parts_info_offset,0)
    total_parts, part_start_offset = struct.unpack("<II", file.read(8))
    part_start_offset += offset_file_1
    factor = -0.001553
    factor_uv = 0.000244
    i = 0
    vertex_count = 0
    while i < total_parts:
        #print("part ",i, " offset: ", part_start_offset)
        file.seek(part_start_offset,0)
        part_size = struct.unpack("<I", file.read(4))[0]

        file.seek(4,1)
        part_info_start = struct.unpack("<I", file.read(4))[0]-12
        file.seek(part_info_start + vertex_in_part_offset,1)
        

        vertex_in_piece = struct.unpack("<I", file.read(4))[0]
        file.seek(8,1)
        for j in range(vertex_in_piece):
            y, z, x = struct.unpack("<hhh", file.read(6))
            vlist.append((((x*-1) * factor), ((y * factor)), (z * factor)))
        #"""
        if vertex_in_piece%2!=0:
            # if the number of vertes is not pair then we need to incress the movement of bytes by two
            file.seek(2,1)
        # Skip normals
        file.seek(4,1)
        file.seek(vertex_in_piece*6,1)
        
        if vertex_in_piece%2!=0:
            # if the number of vertes is not pair then we need to incress the movement of bytes by two
            file.seek(2,1)
            
        file.seek(4,1)
        for j in range(vertex_in_piece):
            u,v = struct.unpack("<hh", file.read(4))
            uvlist.append((u * factor_uv, 1 - v * factor_uv))

        tri_strip_list_idx = file.read(8)
        if tri_strip_list_idx != bytes([0x01, 0x00, 0x00, 0x05, 0x01, 0x01, 0x00, 0x01]):
            self.report( {"ERROR"}, "Triangles identifier doesn't match must be a wrong model or an error with this script, read was: " + str(tri_strip_list_idx) )
        file.read(2)
        tri_list_size = (struct.unpack("<H", file.read(2))[0] - 27904) * 8
        tri_data = file.read(tri_list_size)
        tstrip_index_list = [int(idx/4) for idx in struct.unpack("<%dh" % int(len(tri_data)/2), tri_data)]

        for f in range(len(tstrip_index_list)-2):
            if(tstrip_index_list[f]<0 and tstrip_index_list[f+1]<0 and tstrip_index_list[f+2]>=0):
                if (tstrip_index_list[f] != tstrip_index_list[f+1]) and (tstrip_index_list[f+1] != tstrip_index_list[f+2]) and (tstrip_index_list[f+2] != tstrip_index_list[f]):
                    flist.append((8192 + tstrip_index_list[f] + vertex_count - 1, 8192 + tstrip_index_list[f+1] + vertex_count - 1, tstrip_index_list[f+2] + vertex_count - 1))
            elif(tstrip_index_list[f]<=0 and tstrip_index_list[f+1]>=0 and tstrip_index_list[f+2]>=0):
                if (tstrip_index_list[f] != tstrip_index_list[f+1]) and (tstrip_index_list[f+1] != tstrip_index_list[f+2]) and (tstrip_index_list[f+2] != tstrip_index_list[f]):
                    flist.append((8192 + tstrip_index_list[f] + vertex_count - 1, tstrip_index_list[f+1] + vertex_count - 1, tstrip_index_list[f+2] + vertex_count - 1))
            elif(tstrip_index_list[f+2]>=0 and tstrip_index_list[f+1]>=0 and tstrip_index_list[f]>0):
                if (tstrip_index_list[f+2] != tstrip_index_list[f+1]) and (tstrip_index_list[f+0] != tstrip_index_list[f+2]) and (tstrip_index_list[f+2] != tstrip_index_list[f]):    
                    flist.append((tstrip_index_list[f] + vertex_count - 1, tstrip_index_list[f+1] + vertex_count - 1, tstrip_index_list[f+2] + vertex_count - 1))
            else:
                continue

        part_start_offset += part_size
        i += 1
        vertex_count += vertex_in_piece

    pes_ps2_vc,pes_ps2_vs=vertex_count,0
    if model == 'face':
        bpy.context.scene.face_vc=pes_ps2_vc
        pes_ps2_f_voff=0
    else:
        bpy.context.scene.hair_vc=pes_ps2_vc
        pes_ps2_h_voff=0
    
    file.flush()
    file.close()
    faces=flist
    mesh = bpy.data.meshes.new(obname)
    mesh.from_pydata(vlist, edges, faces)
    
    from bpy_extras import object_utils
    object_utils.object_data_add(context, mesh, operator=None)
    
    me=bpy.context.active_object.data
    bpy.ops.mesh.uv_texture_add('EXEC_SCREEN')
    bm = bmesh.new() 
    bm.from_mesh(me) 
    uv_layer = bm.loops.layers.uv.verify()
    
    for f in range(len(bm.faces)):
        for i in range(len(bm.faces[f].loops)):
            fuv=bm.faces[f].loops[i][uv_layer]
            fuv.uv = uvlist[faces[f][i]]
    bm.to_mesh(me)
    bm.free()
    
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.editmode_toggle()
    
    ac_ob=bpy.context.active_object
    ac_ob.location=(0,0,0)
    
    imgid=bpy.path.display_name_from_filepath(imgfile)+'.png'
    imgfile=imgfile[:-4]+'.png'
    
    if os.access(imgfile,0) == 1:
    
        bpy.ops.image.open(filepath=imgfile,relative_path=False)
        img=bpy.data.images[imgid]
        uvdata=me.uv_textures[0].data
        for face in uvdata:
            face.image=img
    
    add_mat(ac_ob,model)


def pes6_exp(self,model):
    
    global pes6f_voff,pes6h_voff,pes6_vc,pes6_vs
    
    if model == 'face':
        temp=face_temp
        obname='PES_PC_Face'
        pes6_vc=bpy.context.scene.face_vc
        pes6_voff=pes6f_voff
    else:
        temp=hair_temp
        obname='PES_PC_Hair'
        pes6_vc=bpy.context.scene.hair_vc
        pes6_voff=pes6h_voff
    
    ### Export Model ###
    
    ex6_file=open(temp,"r+b")
    ex6_file.seek(pes6_voff,0)
    
    for ob in bpy.data.objects:
        if ob.name[:9] == obname:
            if ob.hide == 0:
                bpy.context.scene.objects.active=ob
                
    ac_ob=bpy.context.active_object
    data=ac_ob.data
    
    if len(data.vertices) != pes6_vc:
        print("")
        self.report( {"ERROR"}, "Vertex Count is Not Equal with Base Model !!\nDont delete or add any vertices !!\nTry Import again Base Model !!\nInfo: Base Model is always last imported model...  " )
        return 0
    
    uvlayer=data.uv_layers.active.data 
    vidx_list,exp_uvlist=[],[]
   
    for poly in data.polygons:
        for idx in range(poly.loop_start, poly.loop_start + poly.loop_total):
            if data.loops[idx].vertex_index not in vidx_list:
                vidx_list.append(data.loops[idx].vertex_index)
                exp_uvlist.append((uvlayer[idx].uv[0],uvlayer[idx].uv[1]))
    
    for e in range(len(data.vertices)):
        x,y,z=data.vertices[e].co
        x,y,z=x*40,y*(-40),z*(-40)
        x,y,z=round(x,8),round(y,8),round(z,8)
        ex6_file.write(struct.pack("3f",y,z,x))
        for t in vidx_list:
            if t == e:
                u,v = exp_uvlist[vidx_list.index(t)][0],exp_uvlist[vidx_list.index(t)][1]
                u,v = round(u,6),round(v,6)
        ex6_file.seek(pes6_vs-20,1)
        ex6_file.write(struct.pack("2f",u,1-v))
        
    ex6_file.flush()
    ex6_file.close()
    
    zlib_comp(self,model)
    
    return 1

def pes6_imp(self,context,model):
    
    if model == 'face':
        obname="PES_PC_Face"
        imgfile=facepath        
    else:
        obname="PES_PC_Hair"
        imgfile=hairpath
        
    global pes6h_voff,pes6f_voff,pes6_vc,pes6_vs
    
    vlist,tlist,flist,edges,uvlist=[],[],[],[],[]
    
    file=unzlib(model) 
    
    file.seek(8,0)
    off1=array('I')
    off1.fromfile(file,1)
    off1=off1[0]
    file.seek(off1+16,0)
    off2=array('I')
    off2.fromfile(file,2)
    off2,idx_off=off2[0],off2[1]+off1
    
    file.seek(off1+off2+8,0)
    
    vc=array('H')
    vc.fromfile(file,2)
    vc,vs=vc[0],vc[1]
    pes6_vc,pes6_vs=vc,vs
    file.seek(4,1)
    if model == 'face':
        bpy.context.scene.face_vc=pes6_vc
        pes6f_voff=file.tell()
    else:
        bpy.context.scene.hair_vc=pes6_vc
        pes6h_voff=file.tell()
    
    for v in range(vc):
        vert=array('f')
        vert.fromfile(file,3)
        x,y,z=vert
        x,y,z=x*(-0.025),y*(-0.025),z*(0.025)
        vlist.append((z,x,y))
        file.seek(vs-20,1)
        uv=array('f')
        uv.fromfile(file,2)
        u,v=uv
        uvlist.append((u,1-v))
       
    file.seek(idx_off,0)
    tris=array('H')
    tris.fromfile(file,1)   
    for t in range(tris[0]):
        idx=array('H')
        idx.fromfile(file,1)
        tlist.append(idx[0])
        
    for f in range(0,(len(tlist)-2),1):
        if (tlist[f] != tlist[f+1]) and (tlist[f+1] != tlist[f+2]) and (tlist[f+2] != tlist[f]):
            flist.append((tlist[f+2],tlist[f+1],tlist[f]))
            
    file.flush()
    file.close()
    faces=flist
    mesh = bpy.data.meshes.new(obname)
    mesh.from_pydata(vlist, edges, faces)
    
    from bpy_extras import object_utils
    object_utils.object_data_add(context, mesh, operator=None)
    
    me=bpy.context.active_object.data
    bpy.ops.mesh.uv_texture_add('EXEC_SCREEN')
    bm = bmesh.new() 
    bm.from_mesh(me) 
    uv_layer = bm.loops.layers.uv.verify()
    
    for f in range(len(bm.faces)):
        for i in range(len(bm.faces[f].loops)):
            fuv=bm.faces[f].loops[i][uv_layer]
            fuv.uv = uvlist[faces[f][i]]
    bm.to_mesh(me)
    bm.free()
    
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.editmode_toggle()
    
    ac_ob=bpy.context.active_object
    ac_ob.location=(0,0,0)
    
    imgid=bpy.path.display_name_from_filepath(imgfile)+'.png'
    imgfile=imgfile[:-4]+'.png'
    
    if os.access(imgfile,0) == 1:
    
        bpy.ops.image.open(filepath=imgfile,relative_path=False)
        img=bpy.data.images[imgid]
        uvdata=me.uv_textures[0].data
        for face in uvdata:
            face.image=img
    
    add_mat(ac_ob,model)
    




def export_mesh(self,model):
    
    global imp_face_dds,imp_hair_dds
    
    if model == 'face':
        temp=face_temp
        dxt=" -fast -nocuda -bc1 "
        new_dds='new_face_tex.dds'
        imp_dds=imp_face_dds
        obname='Face'
        ex_plist=f_plist
    else:
        temp=hair_temp
        dxt=" -fast -alpha -nocuda -bc3 "
        new_dds='new_hair_tex.dds'
        imp_dds=imp_hair_dds
        obname='Hair'
        ex_plist=h_plist
    
    ### Export Model ###
    
    ex_file=open(temp,"r+b")
    
    ex_file.seek(8,0)
    off1=array('I')
    off1.fromfile(ex_file,1)
    ex_file.seek(off1[0]+40,0)
    ex_file.seek(12,1)
    part_off=array('I')
    part_off.fromfile(ex_file,1)
    start=off1[0]+part_off[0]
    ex_file.seek(start,0)
    
    for ob in bpy.data.objects:
        if ob.name[:4] == obname:
            if ob.hide == 0:
                bpy.context.scene.objects.active=ob
                
    ac_ob=bpy.context.active_object
    data=ac_ob.data
    
    vc,slist=0,[0]
    
    for v in ex_plist:
        vc=vc+v[1]
        slist.append(v[1]+max(slist))
    slist.pop()
        
    if len(data.vertices) != vc:
        print("")
        self.report( {"ERROR"}, "Vertex Count is Not Equal with Base Model !!\nDont delete or add any vertices !!\nTry Import again Base Model !!\nInfo: Base Model is always last imported model...  " )
        return 0
    
    uvlayer=data.uv_layers.active.data
    im = data.uv_textures[0].data[0].image   
    vidx_list,exp_uvlist=[],[]
   
    for poly in data.polygons:
        for idx in range(poly.loop_start, poly.loop_start + poly.loop_total):
            if data.loops[idx].vertex_index not in vidx_list:
                vidx_list.append(data.loops[idx].vertex_index)
                exp_uvlist.append((uvlayer[idx].uv[0],uvlayer[idx].uv[1]))
    
    #slist=[(0,8),(8,38),(38,46),(46,722),(722,750)]
    
    for i in range(len(ex_plist)):
        ex_file.seek(start+(64*i),0)
        ex_file.seek(ex_plist[i][0],1)
        g=slist[i]+ex_plist[i][1]
        for e in range(slist[i],g,1):
            x,y,z=data.vertices[e].co
            x,y,z=x*0.1,y*-0.1,z*0.1
            x,y,z=round(x,8),round(y,8),round(z,8)
            ex_file.write(struct.pack("3f",x,z,y))
            for t in vidx_list:
                if t == e:
                    u,v = exp_uvlist[vidx_list.index(t)][0],exp_uvlist[vidx_list.index(t)][1]
                    u,v = round(u,6),round(v,6)
            if ex_plist[i][2] == 88:
                ex_file.seek(60,1)
            else:
                ex_file.seek(ex_plist[i][2]-20,1)
            ex_file.write(struct.pack("2f",u,1-v))
            if ex_plist[i][2] == 88:
                ex_file.seek(8,1)
    
    ### Convert Tex to DDS and Export it ###
      
    f_img=bpy.data.images[im.name]
    f_img_path=f_img.filepath
    
    w,h = f_img.size[0], f_img.size[1]
    
    if not (w in [256,512,1024,2048] and h in [256,512,1024,2048]):
        print("")
        self.report( {"ERROR"}, " Texture Size is Bad !!" )
        return 0
    
    if f_img_path[-4:] in ['.png','.tga']:  ##  Convert TGA,PNG to DDS
        f_img.save()
        input=bpy.path.abspath(f_img_path)
        output=temp_folder+new_dds
        output2='"'+output+'"'
        input2='"'+input+'"'
        print("")
        os.system('"'+DDSPATH+dxt+" "+input2+" "+output2+'"')  
        print("")
        if os.access(output,0) == 1:
            print("DDS Convertion OK...")
            dds_out=open(temp_folder+new_dds,"rb").read()
            os.remove(temp_folder+new_dds)
        else:
            print("")
            self.report( {"ERROR"}, "DDS Convertion Failed.. !! \nBad file path or file name !! \nCheck out System Console !! \nInfo: Exported original texture.. ")
            dds_out=open(imp_dds,"rb").read()
       
    elif f_img_path[-4:] == '.dds':
        dds_out=open(f_img_path,"rb").read()
    else:
        print("")
        self.report( {"ERROR"},"Wrong Texture Format !!\nUse PNG,TGA or DDS !!\nInfo: Exported original texture..  ")
        dds_out=open(imp_dds,"rb").read()
    
    ex_file.flush()
    ex_file.close()
    ex_file1=open(temp,"r+b")  
    ex_file1.seek(8,0)
    off_1=array('I')
    off_1.fromfile(ex_file1,4)
    
    ex_file1.seek(20,0)
    ex_file1.write(struct.pack("4I",off_1[0],off_1[1],off_1[2],off_1[3]))
    ex_file1.seek(off_1[0],0)
    t_data=ex_file1.read(off_1[0]+off_1[1])
    ex_file1.flush()
    ex_file1.close()
    ex_file2=open(temp,"wb")
    if model == 'face':
        ex_file2.write(struct.pack("14I",4,8,56,off_1[1],0xFFFFFFF0,56,off_1[1],0xFFFFFFF0,(56+off_1[1]),0,0,0,0,0))
    else:
        ex_file2.write(struct.pack("14I",3,8,56,off_1[1],0xFFFFFFF0,56,off_1[1],0xFFFFFFF0,(56+off_1[1]),0,0,0,0,0))
    ex_file2.write(t_data)
    ex_file2.flush()
    ex_file2.close()
    ex_file=open(temp,"r+b")
   
    ex_file.seek(32,0)
    dds_off=array("I")
    dds_off.fromfile(ex_file,1)
    ex_file.write(struct.pack("2I",len(dds_out)+16,0xFFFFFFF0))
    if model == 'face':
        ex_file.write(struct.pack("3I",((len(dds_out)+16)+dds_off[0]),87552,0xFFFFFFF0))
    ex_file.seek(dds_off[0],0)
    ex_file.write(struct.pack("4sI","WE00".encode(),0xFF000000))
    ex_file.write(struct.pack("2I",len(dds_out),0x00100000))
    ex_file.write(dds_out)
    if model == 'face':
        b_data=open(bump,"rb").read()
        ex_file.write(b_data)
    
    ex_file.flush()
    ex_file.close()
        
    zlib_comp(self,model)
    
    return 1
       
def add_mesh(model):
    
    global imp_face_dds,imp_hair_dds,f_plist,h_plist,plist,start,h_start,f_start
    
    if model == 'face':
        texname="face_tex"
        imp_dds=imp_face_dds
    else:
        texname="hair_tex"
        imp_dds=imp_hair_dds    
    
    file=unzlib(model)
    
    ### Import Tex DDS from BIN File ###
    
    file.seek(32,0)
    dds_offset=array('I')
    dds_offset.fromfile(file,2)
    file.seek(dds_offset[0]+16,0)
    dds_data=file.read(dds_offset[1]-16)
    dds=open(imp_dds,"wb")
    dds.write(dds_data)
    dds.flush()
    dds.close()
    bpy.ops.image.open(filepath=imp_dds,relative_path=False)
    for im in bpy.data.images:
        if len(im.name) > 8:
            if im.name[:8] in ['face_tex','hair_tex']:
                im.name=im.name[:8]
            
    bpy.path.abspath(bpy.data.images[texname].filepath)
    bpy.data.images[texname].filepath=imp_dds
           
    ### Import Model from BIN File ###
    
    vlist,flist,uvlist=[],[],[]
    file.seek(8,0)
    off1=array('I')
    off1.fromfile(file,1)
    file.seek(off1[0]+40,0)
    spc=array('I')
    spc.fromfile(file,1)
    file.seek(8,1)
    part_off=array('I')
    part_off.fromfile(file,1)
    start=off1[0]+part_off[0]
    file.seek(start,0)
    for a in range(spc[0]):
        v_off=array('I')
        v_off.fromfile(file,2)
        vc=array('B')
        vc.fromfile(file,2)
        file.seek(22,1)
        f_off=array('I')
        f_off.fromfile(file,2)
        file.seek(24,1)
        plist.append((v_off[0],v_off[1],vc[1],f_off[0],f_off[1]))
          
    file.seek(start,0)
    
    for i in range(len(plist)):
        file.seek(start+(64*i),0)
        file.seek(plist[i][0],1)
        for v in range(plist[i][1]):
            vert=array('f')
            vert.fromfile(file,3)
            x,y,z=vert
            x,y,z=x*10,y*10,z*-10
            x,y,z=round(x,8),round(y,8),round(z,8)
            vlist.append((x,z,y))
            if plist[i][2] == 88:
                file.seek(60,1)
            else:
                if bpy.context.scene.uv_sw:
                    file.seek(36,1)
                else:    
                    file.seek(plist[i][2]-20,1)
            uv=array('f')
            uv.fromfile(file,2)
            u,v=uv
            u,v=round(u,6),round(v,6)
            uvlist.append((u,1-v))
            if plist[i][2] == 88 or bpy.context.scene.uv_sw:
                file.seek(8,1)
    
    x=0
    tlist=[]
    for t in range(len(plist)):
        file.seek(start+(64*t)+32,0)
        file.seek(plist[t][3],1)
        
        for f in range(plist[t][4]):
            face=array('H')
            face.fromfile(file,1)
            tlist.append(face[0]+x)
     
        for p in range(0,(len(tlist)-2),1):
            if (tlist[p] != tlist[p+1]) and (tlist[p+1] != tlist[p+2]) and (tlist[p+2] != tlist[p]):
                flist.append((tlist[p+2],tlist[p+1],tlist[p]))
        x=max(tlist)+1
        tlist=[]
            
    file.flush()         
    file.close()    
    
    if model == 'face':
        f_plist=plist
        f_start=start
    else:
        h_plist=plist
        h_start=start
    
    return vlist, flist, uvlist

def add_mat(ac_ob,model):
    
    if model == 'face':
        obname="Face"
        texname="face_tex"
    else:
        obname="Hair"
        texname="hair_tex"
    
    ### Add Material ###
    if len(bpy.data.materials) == 0:
        bpy.ops.material.new()
    matname='mat_face/hair'
    bpy.data.materials[0].name=matname
    bpy.data.materials[matname].use_face_texture=1 
    bpy.data.materials[matname].game_settings.use_backface_culling = 0
    bpy.data.materials[matname].game_settings.alpha_blend='CLIP'
    bpy.data.materials[matname].use_face_texture_alpha=1
    
    bpy.context.active_object.data.materials.append(bpy.data.materials[matname])
    bpy.context.scene.game_settings.material_mode = 'MULTITEXTURE'
    if bpy.context.scene.pes_ver != 'pes_pc' and bpy.context.scene.pes_ver != 'pes_ps2' and bpy.context.scene.pes_ver != 'pes_psp':
        bpy.data.images[texname].reload()
    bpy.context.scene.uv_sw = 0
    if model == 'face':
        bpy.context.scene.face_vc = len(ac_ob.data.vertices)
    else:
        bpy.context.scene.hair_vc = len(ac_ob.data.vertices) 

def import_mesh(self, context, model):
        
        if model == 'face':
            obname="Face"
            texname="face_tex"
        else:
            obname="Hair"
            texname="hair_tex"
            
        verts, faces, uvlist = add_mesh(model)
        edges=[]
        mesh = bpy.data.meshes.new(obname)
        mesh.from_pydata(verts, edges, faces)
        
        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=None)
        
        me=bpy.context.active_object.data
        bpy.ops.mesh.uv_texture_add('EXEC_SCREEN')
        bm = bmesh.new() 
        bm.from_mesh(me) 
        uv_layer = bm.loops.layers.uv.verify()
        
        for f in range(len(bm.faces)):
            for i in range(len(bm.faces[f].loops)):
                fuv=bm.faces[f].loops[i][uv_layer]
                fuv.uv = uvlist[faces[f][i]]
        bm.to_mesh(me)
        bm.free()
        
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.editmode_toggle()
        
        ac_ob=bpy.context.active_object
        
        uv = ac_ob.data.uv_textures[0]
        img = bpy.data.images[texname]
        for face in uv.data:
            face.image = img
        
        ac_ob.location=(0,0,0)
           
        add_mat(ac_ob,model)  

class Face_Modifier_PA(bpy.types.Panel):
    bl_label = "PES/WE/JL PC/PS2/PSP and PES2013 PC Face/Hair Modifier"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    
    
    def draw(self, context):
        
        global facepath,hairpath,face_id,hair_id
        
        obj = bpy.context.active_object
        if obj:
            if obj.active_material:
                game = obj.active_material.game_settings
        scn = bpy.context.scene
        layout = self.layout
        
        for i in range(2):
            row=layout.row()
        row.label()
        row.prop(scn,"pes_ver",text="Game",icon='GAME')
        
        if scn.pes_ver == 'pes_pc' or scn.pes_ver == 'pes_ps2' or scn.pes_ver == 'pes_psp':
            for i in range(4):
                row=layout.row()
            box=layout.box()
            box.label(text="PES/WE PC/PS2/PSP Mode Supports Only 3D Model Import/Export",icon='INFO')
            box.label(text="Put Textures in Same Folder with Same Filename",icon='INFO')
            box.label(text="Ex: messi_face.bin = messi_face.png (Auto-Import)",icon='INFO') 
        
        ## Face Panel
        for i in range(4):
            row=layout.row()
        box=layout.box()
        box.label(text="Face BIN File :")
        box.prop(scn,"face_path",text="")
        facepath=bpy.path.abspath(scn.face_path)
        face_id=bpy.path.display_name_from_filepath(facepath)+'.bin'
        row=box.row(align=0)
        if facepath[-4:] != '.bin':
            row.enabled=0
        row.operator("face.operator",text="Import Face").face_opname="import_face"
        row.operator("face.operator",text="Export Face").face_opname="export_face"
        row=box.row(align=0)
        
        ## Hair Panel
        for i in range(3):
            row=layout.row()
        box=layout.box()
        box.label(text="Hair BIN File :")
        box.prop(scn,"hair_path",text="")
        hairpath=bpy.path.abspath(scn.hair_path)
        hair_id=bpy.path.display_name_from_filepath(hairpath)+'.bin'
        row=box.row(align=0)
        if hairpath[-4:] != '.bin':
            row.enabled=0
        row.operator("face.operator",text="Import Hair").face_opname="import_hair"
        row.operator("face.operator",text="Export Hair").face_opname="export_hair"
        row=box.row(align=0)
        if obj:
            if obj.active_material:
                row=box.row(align=0)
                row.prop(game, "alpha_blend", text="Hair Alpha Mode")
                row=box.row(align=0)
            if bpy.context.mode == 'OBJECT':
                for i in range(3):
                    row = layout.row()
                if len(obj.data.uv_textures):
                    if scn.pes_ver == 'pes13':
                        box=layout.box()
                        box.label(text="Act.Obj. Assigned UVMap Tex = "+obj.data.uv_textures[0].data[0].image.name,icon="IMAGE_DATA")
            else:
                for i in range(3):
                    row = layout.row()
                if obj.name[:4] == 'Face' or obj.name[:11] == 'PES_PC_Face' or obj.name[:12] == 'PES_PS2_Face' or obj.name[:12] == 'PES_PSP_Face':
                    vco=scn.statistics().split('Verts:')[1][:8].split('/')[1][:3]
                    if vco == str(scn.face_vc):
                        box=layout.box()
                        box.label(text="Face Base Model Vertex Count = "+str(scn.face_vc),icon='INFO')     
                    else:
                        box=layout.box()
                        box.label(text="Vertex Count is Not Equal with Face Base Model !!",icon='ERROR')
                elif obj.name[:4] == 'Hair' or obj.name[:11] == 'PES_PC_Hair' or obj.name[:12] == 'PES_PS2_Hair' or obj.name[:12] == 'PES_PSP_Hair':
                    vco=scn.statistics().split('Verts:')[1][:8].split('/')[1][:3]
                    if vco == str(scn.hair_vc):
                        box=layout.box()
                        box.label(text="Hair Base Model Vertex Count = "+str(scn.hair_vc),icon='INFO')     
                    else:
                        box=layout.box()
                        box.label(text="Vertex Count is Not Equal with Hair Base Model !!",icon='ERROR')   
                    
        for i in range(4):
            row = layout.row()
        row.label(text="Auto-Set Kitserver dt0c.img Folder for Export :")
        row=layout.row()    
        row.alignment='EXPAND'
        split=row.split(percentage=0.25)
        col = split.column()
        col.operator("face.operator",text="Set KServ").face_opname="set_ks"
        split=split.split(percentage=1.0)
        col=split.column()   
        col.prop(scn,"ks_path",text="")
        
        for i in range(7):
            row = layout.row()
        box=layout.box()
        box.label(tool_id,icon="INFO")
        box.label("Made by Suat CAGDAS 'sxsxsx', Ported to PS2 and PSP by PES Indie Team",icon="INFO")
        box.operator("wm.url_open",text="Go to Evo-Web Official Thread",icon="URL").url="https://evoweb.uk/threads/pes-we-jl-blender-2-67-face-hair-modifier-add-on.91658"
        for i in range(5):
            row = layout.row()
        
class Face_Modifier_OP(bpy.types.Operator):
    
    bl_idname = "face.operator"
    bl_label = "Add Face"
    
    face_opname = StringProperty()
    
    @classmethod
    def poll(cls, context):
        return context.mode=="OBJECT"
    
    def execute(self, context):
        
        global plist,facepath,hairpath,face_id,hair_id
        scn=bpy.context.scene
        
        if self.face_opname=="import_face":
            if os.access(facepath,0) == 1 and facepath[-4:] == '.bin':
                model="face"
                plist=[]
                if scn.pes_ver == "pes13":
                    import_mesh(self, context, model)
                    return {'FINISHED'}
                elif scn.pes_ver == "pes_ps2":
                    pes_ps2_imp(self, context, model)    
                    return {'FINISHED'}
                elif scn.pes_ver == "pes_psp":
                    pes_psp_imp(self, context, model)    
                    return {'FINISHED'}
                else:
                    pes6_imp(self, context, model)    
                    return {'FINISHED'}
            else:
                print("")
                self.report( {"ERROR"}, " File Not Found: No Selected File, Wrong Filepath or File does not Exist !!" )
                return {'FINISHED'}
        
        elif self.face_opname=="export_face":
            model='face'
            if scn.pes_ver == 'pes13':
                run=export_mesh(self,model)
                str=" and Texture "
            elif scn.pes_ver == "pes_ps2":
                run=pes_ps2_exp(self,model)
                str=" "
            elif scn.pes_ver == "pes_psp":
                run=pes_psp_exp(self,model)
                str=" "
            else:
                run=pes6_exp(self,model)
                str=" "
            if run:
                print("")
                self.report( {"INFO"}, " Face Model"+str+"Exported Successfully..." )
                print(tool_id)
                print("Made by Suat CAGDAS 'sxsxsx'")
                print("")
                return {'FINISHED'}
            else:
                print("")
                return {'FINISHED'}
                     
        elif self.face_opname=="import_hair":
            if os.access(hairpath,0) == 1:
                model="hair"
                plist=[]
                if scn.pes_ver == "pes13":
                    import_mesh(self, context, model)
                    return {'FINISHED'}
                elif scn.pes_ver == "pes_ps2":
                    pes_ps2_imp(self, context, model)    
                    return {'FINISHED'}
                elif scn.pes_ver == "pes_psp":
                    pes_psp_imp(self, context, model)    
                    return {'FINISHED'}
                else:
                    pes6_imp(self, context, model)    
                    return {'FINISHED'}
            else:
                print("")
                self.report( {"ERROR"}, " File Not Found: No Selected File, Wrong Filepath or File does not Exist !!" )
                return {'FINISHED'}
        
        elif self.face_opname=="export_hair":
            model='hair'
            if scn.pes_ver == 'pes13':
                run=export_mesh(self,model)
                str=" and Texture "
            elif scn.pes_ver == "pes_ps2":
                run=pes_ps2_exp(self,model)
                str=" "
            elif scn.pes_ver == "pes_psp":
                run=pes_psp_exp(self,model)
                str=" "
            else:
                run=pes6_exp(self,model)
                str=" "
            if run:
                print("")
                self.report( {"INFO"}, " Hair Model"+str+"Exported Successfully..." )
                print(tool_id)
                print("Made by Suat CAGDAS 'sxsxsx'")
                print("")
                return {'FINISHED'}
            else:
                print("")
                return {'FINISHED'}

        elif self.face_opname=="set_ks":
            bpy.context.scene.face_path=bpy.context.scene.ks_path+face_id
            bpy.context.scene.hair_path=bpy.context.scene.ks_path+hair_id
            return {'FINISHED'}

def register():
    bpy.utils.register_module(__name__)
    pass

def unregister():
    bpy.utils.unregister_module(__name__)
    pass

if __name__ == "__main__":
    register()
 