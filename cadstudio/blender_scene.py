"""Runs INSIDE Blender (or the `bpy` wheel), never imported by cadstudio: renders the tiles of a job.

    blender -b --factory-startup --python-exit-code 1 -P blender_scene.py -- job.json
    python blender_scene.py job.json                      # with the bpy wheel

job.json (written by cadstudio/render.py):
    {"meshes": {"use": "use.npz", "print": "print.npz"},   npz: vertices (n,3) mm, faces (m,3), body (m,) int
     "colors": [[r, g, b], ...], "cap_color": [r, g, b], "samples": 32,
     "tiles": [{"out": "a.png", "mesh": "use", "dir": [x, y, z], "res": [w, h], "ground": true,
                "cut": {"axis": 0, "at": 12.5, "keep": -1} | null, "persp": false}]}

Units stay in mm (1 Blender unit = 1 mm); camera, lights and clipping are scaled from the model size.
Only stdlib + numpy + bpy/bmesh/mathutils, data API instead of operators, so it works headless on CPU.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import bpy  # isort: skip  (the bpy wheel only exposes bmesh/mathutils after bpy is imported)
import bmesh  # isort: skip
import numpy as np
from mathutils import Vector  # isort: skip

SMOOTH_ANGLE = math.radians(30)
MARGIN = 1.12


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.max_bounces = 3
    scene.cycles.use_denoising = True
    scene.render.film_transparent = True
    scene.render.use_persistent_data = True  # keep the BVH between tiles
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    for attribute, value in (("view_transform", "Standard"), ("look", "None")):
        try:  # dynamic enums: names differ between Blender builds
            setattr(scene.view_settings, attribute, value)
        except TypeError:
            pass
    world = bpy.data.worlds.new("studio")
    if world.node_tree is None:
        world.use_nodes = True
    background = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    background.inputs[0].default_value = (1.0, 1.0, 1.0, 1.0)
    background.inputs[1].default_value = 0.32
    scene.world = world
    return scene


def material(name: str, color, roughness: float = 0.6):
    mat = bpy.data.materials.new(name)
    if mat.node_tree is None:
        mat.use_nodes = True
    shader = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    shader.inputs["Base Color"].default_value = (*color, 1.0)
    shader.inputs["Roughness"].default_value = roughness
    return mat


def load_mesh(path: str, name: str, colors, cap_color, cut):
    """npz -> Blender object with one material per body; optional section cut with a capped face."""
    data = np.load(path)
    vertices, faces, body = data["vertices"], data["faces"], data["body"]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices.tolist(), [], faces.tolist())
    count = int(body.max()) + 1 if len(body) else 1
    for index in range(count):
        mesh.materials.append(material(f"{name}-body{index}", colors[index % len(colors)]))
    mesh.materials.append(material(f"{name}-cap", cap_color, roughness=0.9))
    mesh.polygons.foreach_set("material_index", body.astype(np.int32))
    mesh.polygons.foreach_set("use_smooth", np.ones(len(faces), dtype=bool))
    mesh.update()

    if cut:
        normal = Vector((0.0, 0.0, 0.0))
        normal[cut["axis"]] = float(cut["keep"])  # geometry on the `keep` side of the plane survives
        point = Vector((0.0, 0.0, 0.0))
        point[cut["axis"]] = float(cut["at"])
        work = bmesh.new()
        work.from_mesh(mesh)
        result = bmesh.ops.bisect_plane(work, geom=work.verts[:] + work.edges[:] + work.faces[:], dist=1e-5,
                                        plane_co=point, plane_no=-normal, clear_outer=True)
        rim = [e for e in result["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
        if rim:
            filled = bmesh.ops.triangle_fill(work, use_beauty=True, use_dissolve=False, edges=rim, normal=-normal)
            for face in (f for f in filled["geom"] if isinstance(f, bmesh.types.BMFace)):
                face.material_index = count
                face.smooth = False
        work.to_mesh(mesh)
        work.free()
        mesh.update()
    try:
        mesh.set_sharp_from_angle(angle=SMOOTH_ANGLE)  # Blender >= 4.1; older builds stay fully smooth
    except AttributeError:
        pass
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def corners(obj) -> list[Vector]:
    return [obj.matrix_world @ Vector(c) for c in obj.bound_box]


def ground_plane(size: float):
    half = size * 20
    mesh = bpy.data.meshes.new("ground")
    mesh.from_pydata([(-half, -half, 0), (half, -half, 0), (half, half, 0), (-half, half, 0)], [], [(0, 1, 2, 3)])
    mesh.materials.append(material("ground", (0.9, 0.9, 0.9)))
    obj = bpy.data.objects.new("ground", mesh)
    obj.is_shadow_catcher = True
    bpy.context.scene.collection.objects.link(obj)
    return obj


def aim(obj, direction: Vector):
    """Point the object's -Z (camera/light forward) along `direction`, keeping world Z up where possible."""
    if abs(direction.normalized().z) > 0.999:
        # Straight down / up has no "up" to keep: fix the roll so plan views read like a drawing
        # (top: +X right, +Y up; bottom: the part turned over about X, +X still right).
        obj.rotation_euler = (0.0, 0.0, 0.0) if direction.z < 0 else (math.pi, 0.0, 0.0)
        return
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def render_tile(scene, tile, objects, ground, camera, key, fill):
    target = objects[(tile["mesh"], json.dumps(tile.get("cut"), sort_keys=True))]
    for obj in objects.values():
        obj.hide_render = obj is not target
    points = corners(target)
    low = Vector([min(p[i] for p in points) for i in range(3)])
    high = Vector([max(p[i] for p in points) for i in range(3)])
    center, radius = (low + high) / 2, max((high - low).length / 2, 1e-3)

    toward = Vector(tile["dir"]).normalized()  # from the model towards the camera
    aim(camera, -toward)
    camera.location = center + toward * radius * 6
    bpy.context.view_layer.update()
    right = camera.matrix_world.to_3x3() @ Vector((1, 0, 0))
    up = camera.matrix_world.to_3x3() @ Vector((0, 1, 0))
    width, height = tile["res"]
    span_x = max(abs((p - center).dot(right)) for p in points) * 2 * MARGIN
    span_y = max(abs((p - center).dot(up)) for p in points) * 2 * MARGIN
    cam = camera.data
    cam.clip_start, cam.clip_end = radius * 0.05, radius * 20
    if tile.get("persp"):
        cam.type, cam.lens = "PERSP", 85.0
        cam.sensor_fit, cam.sensor_width = "HORIZONTAL", 36.0
        need = max(span_x, span_y * width / height)
        camera.location = center + toward * (need * cam.lens / cam.sensor_width + radius * 0.5)
    else:
        cam.type = "ORTHO"
        cam.ortho_scale = max(span_x, span_y * width / height) if width >= height else max(span_y, span_x * height / width)

    # Lights follow the camera so every view is lit the same way: key from upper left, weak fill from the right.
    aim(key, -(toward * 1.0 + up * 0.7 - right * 0.5).normalized())
    aim(fill, -(toward * 0.7 + up * 0.1 + right * 0.8).normalized())
    ground.location = (center.x, center.y, low.z)
    ground.hide_render = not tile.get("ground", True)

    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 100
    scene.render.filepath = tile["out"]
    bpy.ops.render.render(write_still=True)


def main(job_path: str) -> int:
    job = json.loads(Path(job_path).read_text())
    scene = reset_scene()
    scene.cycles.samples = int(job.get("samples", 32))

    objects = {}
    for tile in job["tiles"]:
        key_name = (tile["mesh"], json.dumps(tile.get("cut"), sort_keys=True))
        if key_name not in objects:
            objects[key_name] = load_mesh(job["meshes"][tile["mesh"]], f"{tile['mesh']}{len(objects)}",
                                          job["colors"], job["cap_color"], tile.get("cut"))
    size = max(max(c[i] for o in objects.values() for c in corners(o)) -
               min(c[i] for o in objects.values() for c in corners(o)) for i in range(3))
    ground = ground_plane(size)

    camera = bpy.data.objects.new("camera", bpy.data.cameras.new("camera"))
    scene.collection.objects.link(camera)
    scene.camera = camera
    lights = []
    for name, energy, angle in (("key", 2.1, 0.5), ("fill", 0.45, 1.0)):
        light = bpy.data.lights.new(name, "SUN")
        light.energy, light.angle = energy, angle
        lights.append(bpy.data.objects.new(name, light))
        scene.collection.objects.link(lights[-1])

    for tile in job["tiles"]:
        render_tile(scene, tile, objects, ground, camera, *lights)
        print(f"@@TILE@@ {tile['out']}", flush=True)
    print(f"@@DONE@@ blender {bpy.app.version_string}", flush=True)
    return 0


if __name__ == "__main__":
    arguments = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    sys.exit(main(arguments[0]))
