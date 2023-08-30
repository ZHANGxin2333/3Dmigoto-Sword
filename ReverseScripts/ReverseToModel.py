from ReverseConfig import *


if __name__ == "__main__":
    mod_files = os.listdir(reverse_mod_path)
    print(mod_files)

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

    ib_file = open(output_ib_filename, "wb")
    ib_file_bytearray = bytearray()
    total_num = 0

    category_offset_dict = {}
    for ib_num in range(len(ib_file_list)):
        ib_filename = ib_file_list[ib_num]

        tmp_ib_file = open(reverse_mod_path + ib_filename,"rb")
        tmp_ib_bytearray = bytearray(tmp_ib_file.read())
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
            ib_file_bytearray += tmp_byte
            now_count = int.from_bytes(tmp_byte,"little")
            if now_count >= max_count:
                max_count = now_count
            if now_count <= min_count:
                min_count = now_count
            i += read_pack_stride
        print("min count " + str(min_count) + "   max count " + str(max_count))
        category_offset_dict[ib_category_list[ib_num]] = max_count
        tmp_ib_file.close()

    ib_file.write(ib_file_bytearray)
    ib_file.close()

    # load Position,Texcoord,Blend info into category_vb_bytearray_dict
    vertex_count = 0
    category_vb_bytearray_list_dict = {}
    for category in category_vb_filename_dict:
        vb_filename = category_vb_filename_dict.get(category)

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

    # Merge them into a final bytearray
    vb_file_bytearray = bytearray()
    print("vertex count:")
    print(vertex_count)
    for i in range(vertex_count):
        for category in category_vb_bytearray_list_dict:
            bytearray_list = category_vb_bytearray_list_dict.get(category)
            add_byte = bytearray_list[i]
            vb_file_bytearray += add_byte


    # Write to .vb file
    vb_file = open(output_vb_filename, "wb")
    vb_file.write(vb_file_bytearray)
    vb_file.close()

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

    # Write to .fmt file.
    fmt_file = open(output_fmt_filename, "w")
    fmt_file.write(fmt_str)
    fmt_file.close()

    # Split vb file to seperate part.
    offset = 0
    for category in category_offset_dict:
        category_offset = category_offset_dict.get(category)

        vb_file_name = mod_name + category + ".vb"
        ib_file_name = mod_name + category + ".ib"
        fmt_file_name = mod_name + category + ".fmt"

        output_fmt_file = open(output_folder + fmt_file_name, "w")
        output_fmt_file.write(fmt_str)
        output_fmt_file.close()

        print(vb_file_name)
        # move ib file to reverse folder
        # 只有offset = 0 的能直接复制过去，其他的都要减去offset
        # shutil.copy2(reverse_mod_path + ib_file_name, output_folder + ib_file_name)
        ib_file = open(reverse_mod_path + ib_file_name, "rb")
        ib_file_bytearray = bytearray(ib_file.read())
        ib_file.close()

        i = 0
        new_ib_file_bytearray = bytearray()
        while i < len(ib_file_bytearray):
            tmp_byte = struct.pack(write_pack_sign,
                                   struct.unpack(read_pack_sign, ib_file_bytearray[i:i + read_pack_stride])[0])
            int_num = int.from_bytes(tmp_byte, "little")
            real_num = int(int_num - offset / stride)
            # print(real_num)

            real_byte = int.to_bytes(real_num, signed=False, byteorder="little", length=read_pack_stride)
            # print(tmp_byte)
            # print(real_byte)
            # print(int.to_bytes(int_num, signed=False, byteorder="little",length=4))
            new_ib_file_bytearray += real_byte
            i += read_pack_stride

        new_ib_file = open(output_folder + ib_file_name, "wb")
        new_ib_file.write(new_ib_file_bytearray)
        new_ib_file.close()

        vb_file = open(output_vb_filename, "rb")
        vb_file_bytearray = bytearray(vb_file.read())
        vb_file.close()

        print("len(vb_file_bytearray) / stride")
        print(len(vb_file_bytearray) / stride)

        left_offset = offset
        right_offset = offset + stride * (category_offset + 1)

        print("Left: " + str(left_offset/stride) + "  Right: " + str(right_offset/stride))
        output_vb_bytearray = vb_file_bytearray[left_offset:right_offset]

        print(len(output_vb_bytearray) / stride)
        output_vb_file = open(output_folder + vb_file_name, "wb")
        output_vb_file.write(output_vb_bytearray)
        output_vb_file.close()

        offset = stride * (category_offset + 1)


