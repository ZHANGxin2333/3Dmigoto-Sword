from ReverseConfig import *


def get_original_ib_file():
    # 读取ib文件，并在格式转换后全部堆叠到一起来输出到一个完整的ib文件
    tmp_ib_file_bytearray = bytearray()
    total_num = 0

    tmp_category_offset_dict = {}
    tmp_category_maxnum_dict = {}
    for ib_num in range(len(ib_file_list)):
        ib_filename = ib_file_list[ib_num]

        tmp_ib_file = open(reverse_mod_path + ib_filename, "rb")
        tmp_ib_bytearray = bytearray(tmp_ib_file.read())
        tmp_ib_file.close()
        print("len(tmp_ib_bytearray)")
        print(len(tmp_ib_bytearray))
        total_num += len(tmp_ib_bytearray)
        # 这里需要逆向处理 https://zhuanlan.zhihu.com/p/387421751
        # GIMI 6.0 使用1H GIMI7.0使用1I 但是其实关系不大，关键在于VB处理

        i = 0
        max_count = 0
        min_count = 9999999
        while i < len(tmp_ib_bytearray):
            tmp_byte = struct.pack(write_pack_sign, struct.unpack(read_pack_sign, tmp_ib_bytearray[i:i + read_pack_stride])[0])
            tmp_ib_file_bytearray += tmp_byte
            now_count = int.from_bytes(tmp_byte, "little")
            if now_count >= max_count:
                max_count = now_count
            if now_count <= min_count:
                min_count = now_count
            i += read_pack_stride
        print("min count " + str(min_count) + "   max count " + str(max_count))
        tmp_category_offset_dict[ib_category_list[ib_num]] = min_count
        tmp_category_maxnum_dict[ib_category_list[ib_num]] = max_count
    return tmp_ib_file_bytearray, tmp_category_offset_dict, tmp_category_maxnum_dict


def collect_ib_subtract_offset(filename, offset):
    ib = bytearray()
    with open(filename, "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            ib += struct.pack(write_pack_sign, struct.unpack(read_pack_sign, data[i:i + read_pack_stride])[0] - offset)
            i += read_pack_stride
    return ib



if __name__ == "__main__":
    # 读取mod文件列表
    mod_files = os.listdir(reverse_mod_path)
    print(mod_files)

    # 读取ib文件列表
    ib_file_list = []
    for ib_category in ib_category_list:
        file_end_str = ib_category + ".ib"

        for filename in mod_files:
            if filename.endswith(file_end_str):
                ib_file_list.append(filename)
    print("ib_file_list:")
    print(ib_file_list)

    category_vb_filename_dict = {}
    for vb_category in vb_category_list:
        file_end_str = vb_category + ".buf"

        for filename in mod_files:
            if filename.endswith(file_end_str):
                category_vb_filename_dict[vb_category] = filename
    print("category_vb_filename_dict:")
    print(category_vb_filename_dict)

    # -------------------------------------------------------------------------------
    # 拼接并写出原始的ib文件
    ib_file_bytearray, category_offset_dict, category_maxnum_dict = get_original_ib_file()
    ib_file = open(output_ib_filename, "wb")
    ib_file.write(ib_file_bytearray)
    ib_file.close()


    print("--------------------------------------------------")
    print("load Position,Texcoord,Blend info into category_vb_bytearray_dict")
    # load Position,Texcoord,Blend info into category_vb_bytearray_dict

    # 这里拼接出来的完整vb的UV就已经错乱了
    vertex_count = 0
    category_vb_bytearray_list_dict = {}
    # print(category_vb_filename_dict)
    # {'Position': 'NilouPosition.buf', 'Texcoord': 'NilouTexcoord.buf', 'Blend': 'NilouBlend.buf'}

    for category in category_vb_filename_dict:
        # 获取buf文件名称
        vb_filename = category_vb_filename_dict.get(category)
        # 读取buf文件数据
        tmp_vb_file = open(reverse_mod_path + vb_filename, "rb")
        data = bytearray(tmp_vb_file.read())
        tmp_vb_file.close()

        category_bytearray_list = []
        categorty_stride = category_stride_dict.get(category)
        print(category)
        print(categorty_stride)
        i = 0
        while i < len(data):
            category_bytearray_list.append(data[i:i+categorty_stride])
            i += categorty_stride
        vertex_count = len(category_bytearray_list)
        category_vb_bytearray_list_dict[category] = category_bytearray_list

    print("--------------------------------------------------")

    # Merge them into a final bytearray
    vb_file_bytearray = bytearray()
    print("vertex count:")
    print(vertex_count)
    print(category_vb_bytearray_list_dict.keys())
    for i in range(vertex_count):
        for category in category_vb_bytearray_list_dict:
            bytearray_list = category_vb_bytearray_list_dict.get(category)
            add_byte = bytearray_list[i]
            vb_file_bytearray += add_byte

    # Write to .vb file 这里只是写入到了一个最终的vb文件
    vb_file = open(output_vb_filename, "wb")
    vb_file.write(vb_file_bytearray)
    vb_file.close()

    # 开始组装并写出单独的fmt文件
    fmt_str = ""
    print(element_list)

    stride = 0
    element_str = ""
    for num in range(len(element_list)):
        element_name = element_list[num]
        semantic_name = vertex_config[element_name]["semantic_name"]
        semantic_index = vertex_config[element_name]["semantic_index"]
        format = vertex_config[element_name]["format"]
        input_slot = vertex_config[element_name]["input_slot"]
        byte_width = vertex_config[element_name].getint("byte_width")
        aligned_byte_offset = str(stride)
        stride += byte_width
        input_slot_class = vertex_config[element_name]["input_slot_class"]
        instance_data_step_rate = vertex_config[element_name]["instance_data_step_rate"]

        element_str = element_str + "element[" + str(num) + "]:\n"
        element_str = element_str + "  SemanticName: " + semantic_name + "\n"
        element_str = element_str + "  SemanticIndex: " + semantic_index + "\n"
        element_str = element_str + "  Format: " + format + "\n"
        element_str = element_str + "  InputSlot: " + input_slot + "\n"
        element_str = element_str + "  AlignedByteOffset: " + aligned_byte_offset + "\n"
        element_str = element_str + "  InputSlotClass: " + input_slot_class + "\n"
        element_str = element_str + "  InstanceDataStepRate: " + instance_data_step_rate + "\n"

    # combine final fmt str.
    fmt_str = fmt_str + "stride: " + str(stride) + "\n"
    fmt_str = fmt_str + "topology: " + "trianglelist" + "\n"
    fmt_str = fmt_str + "format: " + write_dxgi_format + "\n"
    fmt_str = fmt_str + element_str

    # Write to .fmt file.  写出到最终fmt文件
    fmt_file = open(output_fmt_filename, "w")
    fmt_file.write(fmt_str)
    fmt_file.close()

    # 组装出要输出的文件名的字典，用于后续处理
    category_output_name_dict = {}
    for category in ib_category_list:
        vb_file_name = mod_name + category + ".vb"
        ib_file_name = mod_name + category + ".ib"
        fmt_file_name = mod_name + category + ".fmt"
        category_output_name_dict[category] = [ib_file_name, vb_file_name, fmt_file_name]

        # 顺便输出fmt文件
        output_fmt_file = open(output_folder + fmt_file_name, "w")
        output_fmt_file.write(fmt_str)
        output_fmt_file.close()

    # Convert every ib file into specific format,and write to reverse folder.
    print("----------------------------------")
    print(category_offset_dict)
    print("----------------------------------")

    for category in category_output_name_dict:
        output_ib_name = category_output_name_dict.get(category)[0]
        category_maxnum = category_offset_dict.get(category)
        '''
        这里所谓的offset，就是每个ib文件中出现的最小的数字,
        这里是把原本的Head,Body,Dress的三个ib文件，分别减去其每个ib文件中最小的值，
        使得格式全部变成从0开始的值，这样才能导入blender，
        因为mod格式的ib文件，值是从偏移量那里开始的。
        '''
        original_ib_data = collect_ib_subtract_offset(reverse_mod_path + output_ib_name, category_maxnum)
        with open(output_folder + output_ib_name, "wb") as output_ib_file:
            output_ib_file.write(original_ib_data)

    # 分割VB文件为BUF文件
    left_offset_num = 0
    print("--------------------------------------------------")
    print(category_offset_dict)
    print(category_maxnum_dict)
    # 读取整体的vb文件
    vb_file = open(output_vb_filename, "rb")
    vb_file_bytearray = bytearray(vb_file.read())
    vb_file.close()

    for category in category_offset_dict:
        print("Processing: " + str(category))
        category_maxnum = category_maxnum_dict.get(category)
        vb_file_name = category_output_name_dict.get(category)[1]
        print(vb_file_name)

        left_offset = left_offset_num
        right_offset = left_offset_num + stride * (category_maxnum + 1)

        print("Left: " + str(left_offset/stride) + "  Right: " + str(right_offset/stride))
        output_vb_bytearray = vb_file_bytearray[left_offset:right_offset]

        print(len(output_vb_bytearray) / stride)
        output_vb_file = open(output_folder + vb_file_name, "wb")
        output_vb_file.write(output_vb_bytearray)
        output_vb_file.close()

        print("---------")
        print("Category:" + str(category))
        print("category_offset:" + str(category_maxnum))
        left_offset_num =  stride * (category_maxnum + 1)
        print("---------")


