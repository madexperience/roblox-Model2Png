import bpy, os, sys, argparse, math, addon_utils
from mathutils import Vector, Euler

# ---------- CLI args ----------
argv = sys.argv
argv = argv[argv.index("--")+1:] if "--" in argv else []

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True, help="Folder with model files")
parser.add_argument("--output", required=True, help="Output folder for PNGs")
parser.add_argument("--res", type=int, default=512, help="Square resolution")
parser.add_argument("--bg", default="transparent", help="transparent | white | black | #RRGGBB")
parser.add_argument("--angle", nargs=2, type=float, default=[60.0, 30.0], help="camera elevation, azimuth in degrees")
parser.add_argument("--margin", type=float, default=1.15, help="ortho scale padding (1.0~1.3)")
parser.add_argument("--ext", nargs="+", choices=["obj","fbx"], default=["obj"],
                    help="File extensions to process (one or more): obj fbx")
args = parser.parse_args(argv)

print("OUTPUT DIR =", repr(os.path.abspath(args.output)))
os.makedirs(args.output, exist_ok=True)

# ---------- util ----------
def clear_scene():
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

def color_from_hex(s):
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(c*2 for c in s)
    r = int(s[0:2], 16)/255.0
    g = int(s[2:4], 16)/255.0
    b = int(s[4:6], 16)/255.0
    return (r,g,b,1.0)

def bbox_world(obj):
    coords = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = Vector((min(c.x for c in coords), min(c.y for c in coords), min(c.z for c in coords)))
    maxs = Vector((max(c.x for c in coords), max(c.y for c in coords), max(c.z for c in coords)))
    size = maxs - mins
    center = (mins + maxs)/2
    return center, size

def look_at(obj, target):
    direction = (target - obj.location).normalized()
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

def set_world_bg(mode):
    if mode.lower() == "transparent":
        bpy.context.scene.render.film_transparent = True
        return
    bpy.context.scene.render.film_transparent = False
    if mode.lower() == "white":
        rgba = (1,1,1,1)
    elif mode.lower() == "black":
        rgba = (0,0,0,1)
    elif mode.startswith("#"):
        rgba = color_from_hex(mode)
    else:
        rgba = (0.05,0.05,0.05,1)
    if not bpy.data.worlds:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world = bpy.context.scene.world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = rgba

def import_any(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    before = set(bpy.data.objects)
    if ext == ".obj":
        addon_utils.enable("io_scene_obj", default_set=True, persistent=False)
        if hasattr(bpy.ops.wm, "obj_import"):          
            bpy.ops.wm.obj_import(filepath=filepath)
        else:                                           
            bpy.ops.import_scene.obj(filepath=filepath, use_smooth_groups=False)
    elif ext == ".fbx":
        addon_utils.enable("io_scene_fbx", default_set=True, persistent=False)
        bpy.ops.import_scene.fbx(filepath=filepath)
    else:                           
        raise RuntimeError(f"Unsupported extension: {ext}")
    after = set(bpy.data.objects)
    return [o for o in after - before]

def find_files(root, exts):
    # exts: ["obj","fbx"] -> (".obj",".fbx")
    suffix = tuple("." + e.lower() for e in exts)
    out = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith(suffix):
                out.append(os.path.join(dirpath, fn))
    out.sort()
    return out

clear_scene()
scene = bpy.context.scene
scene.render.engine = "CYCLES"  
scene.cycles.samples = 64
scene.cycles.use_denoising = True

scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.resolution_x = args.res
scene.render.resolution_y = args.res
scene.render.resolution_percentage = 100

set_world_bg(args.bg)

cam_data = bpy.data.cameras.new("Cam")
cam_data.type = 'ORTHO'
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

sun_data = bpy.data.lights.new(name="Sun", type='SUN')
sun_data.energy = 3.0
sun_obj = bpy.data.objects.new(name="Sun", object_data=sun_data)
scene.collection.objects.link(sun_obj)

elev_deg, azim_deg = args.angle
elev = math.radians(elev_deg)
azim = math.radians(azim_deg)

# ---------- process files ----------
files = find_files(args.input, args.ext)

for idx, path in enumerate(files, 1):
    name = os.path.splitext(os.path.basename(path))[0]
    print(f"[{idx}/{len(files)}] Render {name}")

    try:
        for o in list(bpy.data.objects):
            if o.name not in {"Cam", "Sun"}:
                bpy.data.objects.remove(o, do_unlink=True)

        imported = import_any(path)
        meshes = [o for o in imported if o.type == "MESH"]
        if not meshes:
            print(f"  ! No mesh in {name}")
            continue

        bpy.ops.object.select_all(action='DESELECT')
        for m in meshes:
            m.select_set(True)
            bpy.context.view_layer.objects.active = meshes[0]
        if len(meshes) > 1:
            bpy.ops.object.join()
        obj = bpy.context.view_layer.objects.active

        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        center, size = bbox_world(obj)

        obj.location -= center
        bpy.context.view_layer.update()
        center, size = bbox_world(obj)

        max_xy = max(size.x, size.y)
        cam_data.ortho_scale = max_xy * args.margin

        dist = max(size.length, 1.0) * 2.0
        cam_x = dist * math.cos(elev) * math.cos(azim)
        cam_y = -dist * math.cos(elev) * math.sin(azim)
        cam_z = dist * math.sin(elev)
        cam_obj.location = Vector((cam_x - 100, cam_y, cam_z))
        look_at(cam_obj, Vector((0,0,0)))

        sun_obj.location = cam_obj.location + Vector((2, -1, 3))
        look_at(sun_obj, Vector((0,0,0)))

        out_path = os.path.join(args.output, f"{name}.png")
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)

    except Exception as e:
        print(f"  ! Skipped {name}: {e}")
        continue

print("Done.")
