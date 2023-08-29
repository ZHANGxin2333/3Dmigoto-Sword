import struct
from ReverseConfig import *


def collect_ib(filename, offset):
    ib = bytearray()
    with open(filename, "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            # Here you must notice!
            # GIMI use R32 will need 1H,but we use R16 will nead H
            ib += struct.pack("I", struct.unpack(unpack_sign, data[i:i + pack_stride])[0] + offset)
            i += pack_stride
    return ib


def collect_vb_Unity(vb_file_name, collect_stride, ignore_tangent=True):
    print("Start to collect vb info from: " + vb_file_name)
    print("Collect_stride: " + str(collect_stride))
    print(category_stride_dict)

    position_width = vertex_config["POSITION"].getint("byte_width")
    normal_width = vertex_config["NORMAL"].getint("byte_width")
    print("Prepare position_width: " + str(position_width))
    print("Prepare normal_width: " + str(normal_width))

    # 这里定义一个dict{vb0:bytearray(),vb1:bytearray()}类型，来依次装载每个vb中的数据
    # 其中vb0需要特殊处理TANGENT部分
    collect_vb_slot_bytearray_dict = {}
    with open(vb_file_name, "rb") as f:
        data = bytearray(f.read())
        i = 0
        while i < len(data):
            # print(vb_slot_stride_dict)  {'vb0': 40, 'vb1': 20, 'vb2': 32}

            # 遍历vb_slot_stride_dict，依次处理
            for vb_stride_slot in category_stride_dict:
                vb_stride = category_stride_dict.get(vb_stride_slot)

                vb_slot_bytearray = bytearray()
                # vb0一般装的是POSITION数据，所以需要特殊处理
                if vb_stride_slot == "vb0":
                    if ignore_tangent:
                        # POSITION and NORMAL
                        vb_slot_bytearray += data[i:i + position_width + normal_width]

                        # TANGENT recalculate use normal value,here we use silent's method.
                        # buy why? what is the mechanism?
                        vb_slot_bytearray += data[i + position_width:i + position_width + normal_width] + bytearray(
                            struct.pack("f", 1))
                    else:
                        print("在处理vb0时,vb_stride必须为40,实际值: " + str(vb_stride))
                        vb_slot_bytearray += data[i:i + vb_stride]
                else:
                        vb_slot_bytearray += data[i:i + vb_stride]

                # print("collecting vb_slot:")
                # print(vb_stride_slot)
                #
                # print("collected vb_slot_bytearray: ")
                # print(len(vb_slot_bytearray))

                # 追加到收集的vb信息中
                original_vb_slot_bytearray = collect_vb_slot_bytearray_dict.get(vb_stride_slot)
                if original_vb_slot_bytearray is None:
                    original_vb_slot_bytearray = bytearray()
                collect_vb_slot_bytearray_dict[vb_stride_slot] = original_vb_slot_bytearray + vb_slot_bytearray

                # 更新步长
                i += vb_stride
    return collect_vb_slot_bytearray_dict


if __name__ == "__main__":
    # 首先计算步长
    stride = 0
    for simple_stride in category_stride_dict.values():
        stride += simple_stride

    # collect vb
    offset = 0

    # 这里定义一个总体的vb_slot_bytearray_dict
    vb0_slot_bytearray_dict = {}

    # vb filename
    for part_name in part_names:
        vb_filename = OutputFolder + part_name + ".vb"

        ignore_tangent = False

        if repair_tangent == "simple":
            ignore_tangent = True

        # 这里获取了vb0:bytearray() 这样的字典
        vb_slot_bytearray_dict = collect_vb_Unity(vb_filename, stride, ignore_tangent=ignore_tangent)


        print(split_str)
        for categpory in vb_slot_bytearray_dict:
            vb_byte_array = vb_slot_bytearray_dict.get(categpory)

            # 获取总的vb_byte_array:
            vb0_byte_array = vb0_slot_bytearray_dict.get(categpory)
            # 如果为空就初始化一下
            if vb0_byte_array is None:
                vb0_byte_array = bytearray()

            vb0_byte_array = vb0_byte_array + vb_byte_array
            vb0_slot_bytearray_dict[categpory] = vb0_byte_array

        # fix_vb_filename = get_filter_filenames(SplitFolder)
        # calculate nearest TANGENT
        if repair_tangent == "nearest":
            # TODO 如何计算TANGENT信息？这始终是一个值得探讨的问题。甚至我觉得这个能单独写一个项目来计算了，所以暂时先不考虑，凑合一下够用了。
            pass
            # position_buf = calculate_tangent_nearest(position_buf, vb_filename)

        # collect ib
        ib_filename = OutputFolder + part_name + ".ib"
        print("ib_filename: " + ib_filename)
        ib_buf = collect_ib(ib_filename, offset)
        with open(OutputFolder + part_name + "_new.ib", "wb") as ib_buf_file:
            ib_buf_file.write(ib_buf)

        # After collect ib, set offset for the next time's collect
        print(offset)
        offset = len(vb0_slot_bytearray_dict.get(position_categoty)) // 40

    # write vb buf to file.
    for categpory in vb0_slot_bytearray_dict:
        vb0_byte_array = vb0_slot_bytearray_dict.get(categpory)

        with open(OutputFolder + mod_name + "_" + categpory + ".buf", "wb") as byte_array_file:
            byte_array_file.write(vb0_byte_array)

    # set the draw number used in VertexLimitRaise
    """
    Where draw xxx,0 comes from?
    It is calculated by the byte length of POSITION file subdivide with POSITION file's stride
    so we could get a vertex number,this is the final number used in [TextureOverrideVertexLimitRaise]

    when you import any -ib.txt and -vb0.txt into blender,blender will add vertex number for you.
    for example if your import vertex number is 18000,then import it into blender and nothing,and just export it
    to .ib and .vb file,and the vertex number will increase to 21000 or higher,so recalculate this when split it
    into .BLEND file is important,and if you calculate it in Merge script ,it will not work well since the vertex
    number is been modified in blender process.
    """
    draw_numbers = len(vb0_slot_bytearray_dict.get(position_categoty)) // 40
    tmp_config.set("Ini", "draw_numbers", str(draw_numbers))
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))


    print("----------------------------------------------------------\r\nAll process done！")

