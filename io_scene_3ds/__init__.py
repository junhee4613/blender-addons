# SPDX-FileCopyrightText: 2011-2023 Blender Foundation
#
# SPDX-License-Identifier: GPL-2.0-or-later

from bpy_extras.io_utils import (
    ImportHelper,
    ExportHelper,
    orientation_helper,
    axis_conversion,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    StringProperty,
)
import bpy
bl_info = {
    "name": "Autodesk 3DS format",
    "author": "Bob Holcomb, Campbell Barton, Andreas Atteneder, Sebastian Schrand",
    "version": (2, 4, 4),
    "blender": (3, 6, 0),
    "location": "File > Import-Export",
    "description": "3DS Import/Export meshes, UVs, materials, textures, "
                   "cameras, lamps & animation",
    "warning": "Images must be in file folder, "
               "filenames are limited to DOS 8.3 format",
    "doc_url": "{BLENDER_MANUAL_URL}/addons/import_export/scene_3ds.html",
    "category": "Import-Export",
}

if "bpy" in locals():
    import importlib
    if "import_3ds" in locals():
        importlib.reload(import_3ds)
    if "export_3ds" in locals():
        importlib.reload(export_3ds)


@orientation_helper(axis_forward='Y', axis_up='Z')
class Import3DS(bpy.types.Operator, ImportHelper):
    """Import from 3DS file format (.3ds)"""
    bl_idname = "import_scene.max3ds"
    bl_label = 'Import 3DS'
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".3ds"
    filter_glob: StringProperty(default="*.3ds", options={'HIDDEN'})

    constrain_size: FloatProperty(
        name="Constrain",
        description="Scale the model by 10 until it reaches the "
        "size constraint (0 to disable)",
        min=0.0, max=1000.0,
        soft_min=0.0, soft_max=1000.0,
        default=10.0,
    )
    convert_measure: BoolProperty(
        name="Convert Measure",
        description="Convert from millimeters to meters",
        default=False,
    )
    use_image_search: BoolProperty(
        name="Image Search",
        description="Search subdirectories for any associated images "
        "(Warning, may be slow)",
        default=True,
    )
    use_apply_transform: BoolProperty(
        name="Apply Transform",
        description="Workaround for object transformations "
        "importing incorrectly",
        default=True,
    )
    read_keyframe: BoolProperty(
        name="Read Keyframe",
        description="Read the keyframe data",
        default=True,
    )
    use_world_matrix: BoolProperty(
        name="World Space",
        description="Transform to matrix world",
        default=False,
    )

    def execute(self, context):
        from . import import_3ds

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            ))

        global_matrix = axis_conversion(from_forward=self.axis_forward,
                                        from_up=self.axis_up,
                                        ).to_4x4()
        keywords["global_matrix"] = global_matrix

        return import_3ds.load(self, context, **keywords)

    def draw(self, context):
        pass


class MAX3DS_PT_import_include(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Include"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_SCENE_OT_max3ds"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "use_image_search")
        layout.prop(operator, "read_keyframe")


class MAX3DS_PT_import_transform(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Transform"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "IMPORT_SCENE_OT_max3ds"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "constrain_size")
        layout.prop(operator, "convert_measure")
        layout.prop(operator, "use_apply_transform")
        layout.prop(operator, "use_world_matrix")
        layout.prop(operator, "axis_forward")
        layout.prop(operator, "axis_up")


@orientation_helper(axis_forward='Y', axis_up='Z')
class Export3DS(bpy.types.Operator, ExportHelper):
    """Export to 3DS file format (.3ds)"""
    bl_idname = "export_scene.max3ds"
    bl_label = 'Export 3DS'
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".3ds"
    filter_glob: StringProperty(
        default="*.3ds",
        options={'HIDDEN'},
    )

    scale_factor: FloatProperty(
        name="Scale",
        description="Scale factor for all objects",
        min=0.0, max=100000.0,
        soft_min=0.0, soft_max=100000.0,
        default=1.0,
    )
    use_selection: BoolProperty(
        name="Selection Only",
        description="Export selected objects only",
        default=False,
    )
    use_hierarchy: BoolProperty(
        name="Export Hierarchy",
        description="Export hierarchy chunks",
        default=False,
    )
    write_keyframe: BoolProperty(
        name="Write Keyframe",
        description="Write the keyframe data",
        default=False,
    )

    def execute(self, context):
        from . import export_3ds

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "check_existing",
                                            ))
        global_matrix = axis_conversion(to_forward=self.axis_forward,
                                        to_up=self.axis_up,
                                        ).to_4x4()
        keywords["global_matrix"] = global_matrix

        return export_3ds.save(self, context, **keywords)

    def draw(self, context):
        pass


class MAX3DS_PT_export_include(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Include"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENE_OT_max3ds"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = True

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "use_selection")
        layout.prop(operator, "use_hierarchy")
        layout.prop(operator, "write_keyframe")


class MAX3DS_PT_export_transform(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = "Transform"
    bl_parent_id = "FILE_PT_operator"

    @classmethod
    def poll(cls, context):
        sfile = context.space_data
        operator = sfile.active_operator

        return operator.bl_idname == "EXPORT_SCENE_OT_max3ds"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        sfile = context.space_data
        operator = sfile.active_operator

        layout.prop(operator, "scale_factor")
        layout.prop(operator, "axis_forward")
        layout.prop(operator, "axis_up")


# Add to a menu
def menu_func_export(self, context):
    self.layout.operator(Export3DS.bl_idname, text="3D Studio (.3ds)")


def menu_func_import(self, context):
    self.layout.operator(Import3DS.bl_idname, text="3D Studio (.3ds)")


def register():
    bpy.utils.register_class(Import3DS)
    bpy.utils.register_class(MAX3DS_PT_import_include)
    bpy.utils.register_class(MAX3DS_PT_import_transform)
    bpy.utils.register_class(Export3DS)
    bpy.utils.register_class(MAX3DS_PT_export_include)
    bpy.utils.register_class(MAX3DS_PT_export_transform)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(Import3DS)
    bpy.utils.unregister_class(MAX3DS_PT_import_include)
    bpy.utils.unregister_class(MAX3DS_PT_import_transform)
    bpy.utils.unregister_class(Export3DS)
    bpy.utils.unregister_class(MAX3DS_PT_export_include)
    bpy.utils.unregister_class(MAX3DS_PT_export_transform)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()