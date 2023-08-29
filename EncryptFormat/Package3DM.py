import os


class MigotoMod:
    hash_skip_list = {}
    basic_check = None




class MigotoBuffer:
    format = ""
    ini_file = None
    name_buffers = {}
    ib_buffers = None




class BasicChecks:
    hash_list = {"2030c989673a6153", "636815112e230ec4"}
    content = '''if $costume_mods
  checktextureoverride = vb1
  checktextureoverride = ib
endif'''

class MigotoObject:

    pass


if __name__ == "__main__":
    """
    设计思路：
    制作完成Mod后，使用打包工具打包为.3dm格式，3dmigoto在读取3dm文件时在内存中展开文件并读取。
    
    .3dm格式设计思路
    
    - 元数据区域
    读取元数据区域来决定如何读取后续的区域
    
    
    
    
    - 数据存储区域
    
    """
    print("加密打包工具V1.0 开始运行")

    # 首先确定要从哪里读取mod
    mod_folder = "C:/Users/Administrator/Desktop/Naraka Bladepoint Mod/Mods/崔三娘-海之奇-NSFW/"
    mod_name = mod_folder.split("/")[-2]
    print("Mod名称: " + mod_name)


    mod_file_list = os.listdir(mod_folder)

    # find submod folder
    submod_folder_list = []
    for mod_file_name in mod_file_list:
        submod_folder_path = mod_folder + mod_file_name
        if os.path.isdir(submod_folder_path):
            submod_folder_list.append(submod_folder_path)


    # 设置一个总的basic_check.ini的hash统计
    basic_check_file_list = []

    # 设置一个总的 文件夹名：文件的字典
    modname_bufferfile_dict = {}

    if len(submod_folder_list) != 0:
        # 如果子mod文件夹不为0的话，说明是由多个mod组合为一个mod的，那么将其分别拆开来进行处理。
        for submod_folder in submod_folder_list:

            print("当前处理子Mod文件夹：" + submod_folder)
            submod_filename_list = os.listdir(submod_folder)
            # print(submod_filename_list)

            buffer_file_list = []

            for mod_file_name in submod_filename_list:
                mod_file_abspath = submod_folder + "/" + mod_file_name
                # 如果有basic_check.ini，就把它的绝对路径加入basic_check_file_list里
                if mod_file_name == "basic_check.ini":
                    basic_check_file_list.append(mod_file_abspath)
                else:
                    buffer_file_list.append(mod_file_abspath)

            modname_bufferfile_dict[submod_folder] = buffer_file_list
    else:
        print("没有子mod存在，直接读取当前mod目录")

    print("文件读取完成，buffer内容如下")
    print(modname_bufferfile_dict)
    print("BasicCheck文件列表如下")
    print(basic_check_file_list)

    # NicoMico,元数据部分长度
    # migotoFile = open(mod_folder + mod_name + ".3dm", "wb+")
    migoto_bytearray = b""
    migoto_bytearray += b"NicoMico"
    # 文件标号,起始位置，文件长度的列表














