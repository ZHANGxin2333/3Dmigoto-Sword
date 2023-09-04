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