import os
import configparser
import shutil
import struct
import math

global_config = configparser.ConfigParser()
global_config.read("Configs/global_config.ini", "utf-8")
config_folder = global_config["Global"]["config_folder"]

preset_config = configparser.ConfigParser()
preset_config.optionxform = str  # 设置optionxform属性为str，保留原始大小写形式
preset_config.read(config_folder + "/preset.ini", "utf-8")

tmp_config = configparser.ConfigParser()
tmp_config.read(config_folder + "/tmp.ini", "utf-8")

vertex_config = configparser.ConfigParser()
vertex_config.read(config_folder + "/vertex_attr.ini", "utf-8")

# -----------------------------------General--------------------------------------------
mod_name = preset_config["General"]["mod_name"]
reverse_mod_path = preset_config["General"]["reverse_mod_path"]
ib_category_list = preset_config["General"]["ib_category_list"].split(",")
vb_category_list = preset_config["General"]["vb_category_list"].split(",")
element_list = preset_config["General"]["element_list"].split(",")

# -----------------------------------Split--------------------------------------------
repair_tangent = preset_config["Split"].getboolean("repair_tangent")

category_stride_dict = {option: int(value) for option, value in preset_config.items('CategoryStride')}
print(category_stride_dict)
output_folder = reverse_mod_path + "reverse/"
if not os.path.exists(output_folder):
    os.mkdir(output_folder)

output_ib_filename = output_folder + mod_name + ".ib"
output_vb_filename = output_folder + mod_name + ".vb"
output_fmt_filename = output_folder + mod_name + ".fmt"

# ------------------   format    --------------------------
read_dxgi_format = preset_config["General"]["read_dxgi_format"]
write_dxgi_format = preset_config["General"]["write_dxgi_format"]

read_pack_sign = 'H'
write_pack_sign = 'H'
read_pack_stride = 2

if read_dxgi_format == "DXGI_FORMAT_R16_UINT":
    read_pack_stride = 2
    read_pack_sign = 'H'

if read_dxgi_format == "DXGI_FORMAT_R32_UINT":
    read_pack_stride = 4
    read_pack_sign = 'I'

if write_dxgi_format == "DXGI_FORMAT_R16_UINT":
    write_pack_sign = 'H'

if write_dxgi_format == "DXGI_FORMAT_R32_UINT":
    write_pack_sign = 'I'
