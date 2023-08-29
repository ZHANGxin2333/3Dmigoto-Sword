import os
import struct


def traverse_folder(folder_path):
    file_list = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = root + "/" + file
            file_list.append(file_path)
    return file_list


class migotoFile:
    file_id = None
    file_buffer = None
    file_buffer_size = None
    file_name = None

    def __init__(self,file_id,file_buffer):
        self.file_id = file_id
        self.file_buffer = file_buffer
        self.file_buffer_size = len(file_buffer)


if __name__ == "__main__":
    print("加密打包工具V1.0 开始运行")

    # 首先确定要从哪里读取mod
    mod_folder = "C:/Users/Administrator/Desktop/Naraka Bladepoint Mod/Mods/崔三娘-海之奇-NSFW/"

    mod_name = mod_folder.split("/")[-2]

    # 递归添加所有文件
    mod_file_list = traverse_folder(mod_folder)

    # 输出查看
    print(mod_file_list)

    # 打包装箱到列表
    migotoFileList = []
    file_id = 0
    for mod_file_abspath in mod_file_list:
        mod_file = open(mod_file_abspath, "rb")
        mod_file_bytes = mod_file.read()
        mod_file.close()
        migoto_file = migotoFile(file_id, mod_file_bytes)
        migotoFileList.append(migoto_file)
        file_id = file_id + 1


    # NicoMico,元数据部分长度

    migoto_bytearray = b""
    migoto_bytearray += b"DESC"
    # 文件标号,文件长度的列表
    for migoto_file in migotoFileList:
        migoto_bytearray += struct.pack("i", migoto_file.file_id)
        migoto_bytearray += struct.pack("i", migoto_file.file_buffer_size)

    migoto_bytearray += b"DATA"
    for migoto_file in migotoFileList:
        migoto_bytearray += migoto_file.file_buffer


    final_file = open(mod_folder + mod_name + ".3dm", "wb+")
    final_file.write(migoto_bytearray)
    final_file.close()









