from ReverseConfig import *


# 读取必须的参数
reverse_ini_path = preset_config["General"]["reverse_ini_path"]
element_list = preset_config["General"]["element_list"].split(",")

# 拆分reverse_ini_path
# C:/Users/Administrator/Desktop/fuhua-RosyBridesmaid-sfw-2/
reverse_mod_path = os.path.dirname(reverse_ini_path) + "/"
# fuhua-RosyBridesmaid.ini
reverse_ini_name = os.path.basename(reverse_ini_path)

mod_name = reverse_ini_name.split(".")[0]
print(mod_name)

print("逆向Mod的Buffer文件所在路径：" + reverse_mod_path)
print("逆向Mod的主ini文件名称：" + reverse_ini_name)


class IniKVPair:
    section_name = ""
    kv_map = {"":""}

    def __str__(self):
        print_str = "SectionName: " + self.section_name + "\n"
        for option_name in self.kv_map:
            option_value = self.kv_map.get(option_name)
            print_str += "OptionName: " + option_name + "\n" + "OptionValue: " + option_value + "\n"
        print_str += "-----------------------------"
        return print_str


reverse_ini_config = configparser.ConfigParser()
reverse_ini_config.optionxform = str  # 设置optionxform属性为str，保留原始大小写形式
reverse_ini_config.read(reverse_ini_path, "utf-8")

# 获取该Mod的配置文件所有内容
reverse_ini_sections = reverse_ini_config.sections()
print(reverse_ini_sections)

# 解析配置文件内容，并放入list备用
ini_kv_pair_list = []
for section_name in reverse_ini_sections:
    options = reverse_ini_config.options(section_name)

    ini_kv_pair = IniKVPair()
    ini_kv_pair.section_name = section_name
    ini_kv_pair.kv_map = {}

    for option_name in options:
        option_value = reverse_ini_config.get(section_name, option_name)
        ini_kv_pair.kv_map[option_name] = option_value

    ini_kv_pair_list.append(ini_kv_pair)

    # print(ini_kv_pair)

# 解析资源文件
'''
这里注意分别计息TextureOverride部分和Resource部分
而且顺序必须为先解析Resource，再解析TextureOverride
'''

# 根据资源类型，将kv_pair分别装入TextureOverride list或Resource list
texture_override_kvpair_list = []
resource_kvpair_list = []

for ini_kv_pair in ini_kv_pair_list:
    section_name = ini_kv_pair.section_name
    if section_name.startswith("TextureOverride"):
        texture_override_kvpair_list.append(ini_kv_pair)
        continue

    if section_name.startswith("Resource"):
        resource_kvpair_list.append(ini_kv_pair)

# 输出查看是否正确
for ini_kv_pair in texture_override_kvpair_list:
    print(ini_kv_pair)

for ini_kv_pair in resource_kvpair_list:
    print(ini_kv_pair)

# 构建对应的数据类型来装载Resource类型


class DataIBResource:
    resource_name = None
    resource_format = None
    resource_filename = None


class DataVBResource:
    resource_name = None
    resource_stride = None
    resource_filename = None


data_ib_resource_list = []
data_vb_resource_list = []

for ini_kv_pair in resource_kvpair_list:

    # 先确定类型是ib文件还是buf文件
    find_stride = False
    find_format = False

    for option_name in ini_kv_pair.kv_map:
        if "stride" == str(option_name).lower():
            find_stride = True
            break

        if "format" == str(option_name).lower():
            find_format = True
            break

    if find_format:
        data_ib_resource = DataIBResource()
        # 设置名称
        data_ib_resource.resource_name = ini_kv_pair.section_name
        # 设置format和filename
        for option_name in ini_kv_pair.kv_map:
            option_value = ini_kv_pair.kv_map.get(option_name)

            if "format" == str(option_name).lower():
                data_ib_resource.resource_format = option_value

            if "filename" == str(option_name).lower():
                data_ib_resource.resource_filename = option_value
        data_ib_resource_list.append(data_ib_resource)
        continue

    if find_stride:
        data_vb_resource = DataVBResource()
        # 设置名称
        data_vb_resource.resource_name = ini_kv_pair.section_name
        # 设置stride和filename
        for option_name in ini_kv_pair.kv_map:
            option_value = ini_kv_pair.kv_map.get(option_name)

            if "stride" == str(option_name).lower():
                data_vb_resource.resource_stride = option_value

            if "filename" == str(option_name).lower():
                data_vb_resource.resource_filename = option_value
        data_vb_resource_list.append(data_vb_resource)

# 接下来需要验证这些Resource文件是否在TextureOverride中使用到了。
# 理论上来讲，一个未混淆过的标准mod是不需要验证的，所以直接跳到下一步


# 现在我们有了IB文件和Buffer文件，接下来要做的就是确定他们的顺序。
# 先输出看看格式是什么样的
for data_ib_resource in data_ib_resource_list:
    print(data_ib_resource.resource_filename)
    print(data_ib_resource.resource_format)

for data_vb_resource in data_vb_resource_list:
    print(data_vb_resource.resource_filename)
    print(data_vb_resource.resource_stride)

# 首先根据TextureOverride IB中的first index的大小，来确定对应的IB文件顺序排序。
# 其次根据TextureOverride VB中的槽位设置，来确定VB文件的顺序排序

# 在IB VB文件的顺序排序设置上，我们需要提供一个预设来快速确定IB文件的顺序。
# 优先读取预设的顺序，如果预设不起作用，再去配置文件里解析
ib_suffix_order = preset_config["ManuallyFix"]["ib_suffix_order"].split(",")
vb_suffix_order = preset_config["ManuallyFix"]["vb_suffix_order"].split(",")


# TODO 增加配置文件解析的代码

# 根据预设，计算出正确顺序的列表


# 读取输入的ib文件的DXGI_FORMAT
format_count_dict = {}
for data_ib_resource in data_ib_resource_list:
    format_count = format_count_dict.get(data_ib_resource.resource_format)
    if format_count is None:
        format_count_dict[data_ib_resource.resource_format] = 1
    else:
        format_count_dict[data_ib_resource.resource_format] = format_count + 1

read_dxgi_format = ""
for dxgi_format in format_count_dict:
    format_count = format_count_dict.get(dxgi_format)
    if format_count == len(data_ib_resource_list):
        read_dxgi_format = dxgi_format
        break

print(read_dxgi_format)

read_pack_sign = 'H'
write_pack_sign = 'H'
read_pack_stride = 2

if read_dxgi_format == "DXGI_FORMAT_R16_UINT":
    read_pack_stride = 2
    read_pack_sign = 'H'
    write_pack_sign = 'H'

if read_dxgi_format == "DXGI_FORMAT_R32_UINT":
    read_pack_stride = 4
    read_pack_sign = 'I'
    write_pack_sign = 'I'



# 拼接每个分类的步长字典
category_stride_dict = {}
for vb_suffix in vb_suffix_order:
    for data_vb_resource in data_vb_resource_list:
        print(vb_suffix)
        print(data_vb_resource.resource_filename)
        print(data_vb_resource.resource_stride)
        if str(data_vb_resource.resource_filename).endswith(vb_suffix + ".buf"):
            category_stride_dict[vb_suffix] = int(data_vb_resource.resource_stride)

            break

print(category_stride_dict)

def get_category_minnum_maxnum_dict_from_ib_file(fc_tmp_ib_file_list):
    # 读取ib文件，并在格式转换后全部堆叠到一起来输出到一个完整的ib文件
    total_num = 0

    tmp_category_minnum_dict = {}
    tmp_category_maxnum_dict = {}
    for ib_num in range(len(fc_tmp_ib_file_list)):
        ib_filename = fc_tmp_ib_file_list[ib_num]

        tmp_ib_file = open(reverse_mod_path + ib_filename, "rb")
        tmp_ib_bytearray = bytearray(tmp_ib_file.read())
        tmp_ib_file.close()

        total_num += len(tmp_ib_bytearray)

        i = 0
        max_count = 0
        min_count = 9999999
        while i < len(tmp_ib_bytearray):
            tmp_byte = struct.pack(write_pack_sign,
                                   struct.unpack(read_pack_sign, tmp_ib_bytearray[i:i + read_pack_stride])[0])
            now_count = int.from_bytes(tmp_byte, "little")
            if now_count >= max_count:
                max_count = now_count
            if now_count <= min_count:
                min_count = now_count
            i += read_pack_stride
        print("min count " + str(min_count) + "   max count " + str(max_count))
        tmp_category_minnum_dict[ib_suffix_order[ib_num]] = min_count
        tmp_category_maxnum_dict[ib_suffix_order[ib_num]] = max_count
    return tmp_category_minnum_dict, tmp_category_maxnum_dict


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


def get_fmt_str_and_stride_from_element_list():
    # 开始组装fmt文件内容
    fc_tmp_fmt_str = ""

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
    fc_tmp_fmt_str = fc_tmp_fmt_str + "stride: " + str(stride) + "\n"
    fc_tmp_fmt_str = fc_tmp_fmt_str + "topology: " + "trianglelist" + "\n"
    fc_tmp_fmt_str = fc_tmp_fmt_str + "format: " + read_dxgi_format + "\n"
    fc_tmp_fmt_str = fc_tmp_fmt_str + element_str

    return fc_tmp_fmt_str, stride


def split_vb_files(fc_tmp_category_offset_dict, fc_tmp_category_maxnum_dict, fc_tmp_vb_file_bytearray,
                   fc_tmp_category_output_name_dict, fc_tmp_stride):
    # 分割VB文件为多个vb文件
    left_offset_num = 0

    for fc_tmp_category in fc_tmp_category_offset_dict:
        print("Processing: " + str(fc_tmp_category))
        fc_tmp_category_maxnum = fc_tmp_category_maxnum_dict.get(fc_tmp_category)
        vb_file_name = fc_tmp_category_output_name_dict.get(fc_tmp_category)[1]
        print(vb_file_name)

        left_offset = left_offset_num
        right_offset = left_offset_num + fc_tmp_stride * (fc_tmp_category_maxnum + 1)

        print("Left: " + str(left_offset / fc_tmp_stride) + "  Right: " + str(right_offset / fc_tmp_stride))
        output_vb_bytearray = fc_tmp_vb_file_bytearray[left_offset:right_offset]

        output_vb_file = open(output_folder + vb_file_name, "wb")
        output_vb_file.write(output_vb_bytearray)
        output_vb_file.close()

        left_offset_num = fc_tmp_stride * (fc_tmp_category_maxnum + 1)


def get_category_vb_filename_dict(fc_tmp_mod_files):
    tmp_category_vb_filename_dict = {}
    for vb_category in vb_suffix_order:
        file_end_str = vb_category + ".buf"

        for filename in fc_tmp_mod_files:
            if filename.endswith(file_end_str):
                tmp_category_vb_filename_dict[vb_category] = filename
    return tmp_category_vb_filename_dict


def get_tmp_ib_file_list(fc_tmp_mod_files):
    tmp_ib_file_list = []
    for ib_category in ib_suffix_order:
        file_end_str = ib_category + ".ib"

        for filename in fc_tmp_mod_files:
            if filename.endswith(file_end_str):
                tmp_ib_file_list.append(filename)
    return tmp_ib_file_list


def get_vb_byte_array(fc_tmp_category_vb_filename_dict):
    vertex_count = 0
    category_vb_bytearray_list_dict = {}

    for category in fc_tmp_category_vb_filename_dict:
        # 获取buf文件名称
        vb_filename = fc_tmp_category_vb_filename_dict.get(category)
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
            category_bytearray_list.append(data[i:i + categorty_stride])
            i += categorty_stride
        vertex_count = len(category_bytearray_list)
        category_vb_bytearray_list_dict[category] = category_bytearray_list

    # Merge them into a final bytearray
    tmp_vb_file_bytearray = bytearray()
    print("vertex count:")
    print(vertex_count)
    print(category_vb_bytearray_list_dict.keys())
    for i in range(vertex_count):
        for category in category_vb_bytearray_list_dict:
            bytearray_list = category_vb_bytearray_list_dict.get(category)
            add_byte = bytearray_list[i]
            tmp_vb_file_bytearray += add_byte

    return tmp_vb_file_bytearray


def get_category_output_name_dict(fc_tmp_fmt_str):
    fc_tmp_category_output_name_dict = {}
    for fc_tmp_category in ib_suffix_order:
        vb_file_name = mod_name + fc_tmp_category + ".vb"
        ib_file_name = mod_name + fc_tmp_category + ".ib"
        fmt_file_name = mod_name + fc_tmp_category + ".fmt"
        fc_tmp_category_output_name_dict[fc_tmp_category] = [ib_file_name, vb_file_name, fmt_file_name]

        # 顺便输出fmt文件
        output_fmt_file = open(output_folder + fmt_file_name, "w")
        output_fmt_file.write(fc_tmp_fmt_str)
        output_fmt_file.close()
    return fc_tmp_category_output_name_dict


def convert_and_output_ib_file(fc_tmp_category_output_name_dict, fc_tmp_category_minnum_dict):
    for category in fc_tmp_category_output_name_dict:
        output_ib_name = fc_tmp_category_output_name_dict.get(category)[0]
        category_minnum = fc_tmp_category_minnum_dict.get(category)
        '''
        这里所谓的offset，就是每个ib文件中出现的最小的数字,
        这里是把原本的Head,Body,Dress的三个ib文件，分别减去其每个ib文件中最小的值，
        使得格式全部变成从0开始的值，这样才能导入blender，
        因为mod格式的ib文件，值是从偏移量那里开始的。
        '''
        original_ib_data = collect_ib_subtract_offset(reverse_mod_path + output_ib_name, category_minnum)
        with open(output_folder + output_ib_name, "wb") as output_ib_file:
            output_ib_file.write(original_ib_data)


def start_reverse():
    # (3) 读取ib文件中，分别最小和最大的数，用于后续转换ib文件时和分割vb文件时提供坐标指示
    category_minnum_dict, category_maxnum_dict = get_category_minnum_maxnum_dict_from_ib_file(ib_file_list)

    # (4) 获取最终要进行分割处理的vb文件内容
    vb_file_bytearray = get_vb_byte_array(category_vb_filename_dict)

    # (5) 获取最终fmt文件内容
    fmt_str, stride = get_fmt_str_and_stride_from_element_list()

    # (6) 组装出要输出的文件名的字典，用于后续处理,顺便还会输出fmt文件
    category_output_name_dict = get_category_output_name_dict(fmt_str)

    # (7) 把每个ib文件转换成特殊格式后再输出
    convert_and_output_ib_file(category_output_name_dict, category_minnum_dict)

    # (8) 将完整的vb文件分割为多个vb文件
    split_vb_files(category_minnum_dict, category_maxnum_dict, vb_file_bytearray, category_output_name_dict, stride)


if __name__ == "__main__":
    '''
    有几个硬参数是灵活变化的，需要在逆向开始前提供
    reverse_mod_path                mod文件所在文件夹
    output_folder                   逆向结果文件输出到哪个目录
    ib_file_list                    ib文件名称列表
    category_vb_filename_dict       {类别:vb文件名称列表}
    '''

    output_folder = reverse_mod_path + "reverse/"
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # (0) 读取mod文件列表
    mod_files = os.listdir(reverse_mod_path)

    # (1) 读取ib文件名称列表
    ib_file_list = get_tmp_ib_file_list(mod_files)

    # (2) 读取类别:vb文件名称列表
    category_vb_filename_dict = get_category_vb_filename_dict(mod_files)

    # 正式启动逆向
    start_reverse()


