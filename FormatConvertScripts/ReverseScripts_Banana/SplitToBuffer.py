from ReverseConfig import *


# https://github.com/Vectorized/Python-KD-Tree
# A brute force solution for finding the original tangents is O(n^2), and isn't good enough since n can get quite
#   high in many models (upwards of a minute calculation time in some cases)
# So we use a simple KD structure to perform quick nearest neighbor lookups
# (Copied from GIMI repository: https://github.com/SilentNightSound/GI-Model-Importer)
# (just for don't make another wheel)
class KDTree(object):
    """
    Usage:
    1. Make the KD-Tree:
        `kd_tree = KDTree(points, dim)`
    2. You can then use `get_knn` for k nearest neighbors or
       `get_nearest` for the nearest neighbor
    points are be a list of points: [[0, 1, 2], [12.3, 4.5, 2.3], ...]
    """

    def __init__(self, points, dim, dist_sq_func=None):
        """Makes the KD-Tree for fast lookup.
        Parameters
        ----------
        points : list<point>
            A list of points.
        dim : int
            The dimension of the points.
        dist_sq_func : function(point, point), optional
            A function that returns the squared Euclidean distance
            between the two points.
            If omitted, it uses the default implementation.
        """

        if dist_sq_func is None:
            dist_sq_func = lambda a, b: sum((x - b[i]) ** 2
                                            for i, x in enumerate(a))

        def make(points, i=0):
            if len(points) > 1:
                points.sort(key=lambda x: x[i])
                i = (i + 1) % dim
                m = len(points) >> 1
                return [make(points[:m], i), make(points[m + 1:], i),
                        points[m]]
            if len(points) == 1:
                return [None, None, points[0]]

        def add_point(node, point, i=0):
            if node is not None:
                dx = node[2][i] - point[i]
                for j, c in ((0, dx >= 0), (1, dx < 0)):
                    if c and node[j] is None:
                        node[j] = [None, None, point]
                    elif c:
                        add_point(node[j], point, (i + 1) % dim)

        import heapq
        def get_knn(node, point, k, return_dist_sq, heap, i=0, tiebreaker=1):
            if node is not None:
                dist_sq = dist_sq_func(point, node[2])
                dx = node[2][i] - point[i]
                if len(heap) < k:
                    heapq.heappush(heap, (-dist_sq, tiebreaker, node[2]))
                elif dist_sq < -heap[0][0]:
                    heapq.heappushpop(heap, (-dist_sq, tiebreaker, node[2]))
                i = (i + 1) % dim
                # Goes into the left branch, then the right branch if needed
                for b in (dx < 0, dx >= 0)[:1 + (dx * dx < -heap[0][0])]:
                    get_knn(node[b], point, k, return_dist_sq,
                            heap, i, (tiebreaker << 1) | b)
            if tiebreaker == 1:
                return [(-h[0], h[2]) if return_dist_sq else h[2]
                        for h in sorted(heap)][::-1]

        def walk(node):
            if node is not None:
                for j in 0, 1:
                    for x in walk(node[j]):
                        yield x
                yield node[2]

        self._add_point = add_point
        self._get_knn = get_knn
        self._root = make(points)
        self._walk = walk

    def __iter__(self):
        return self._walk(self._root)

    def add_point(self, point):
        """Adds a point to the kd-tree.

        Parameters
        ----------
        point : array-like
            The point.
        """
        if self._root is None:
            self._root = [None, None, point]
        else:
            self._add_point(self._root, point)

    def get_knn(self, point, k, return_dist_sq=True):
        """Returns k nearest neighbors.
        Parameters
        ----------
        point : array-like
            The point.
        k: int
            The number of nearest neighbors.
        return_dist_sq : boolean
            Whether to return the squared Euclidean distances.
        Returns
        -------
        list<array-like>
            The nearest neighbors.
            If `return_dist_sq` is true, the return will be:
                [(dist_sq, point), ...]
            else:
                [point, ...]
        """
        return self._get_knn(self._root, point, k, return_dist_sq, [])

    def get_nearest(self, point, return_dist_sq=True):
        """Returns the nearest neighbor.
        Parameters
        ----------
        point : array-like
            The point.
        return_dist_sq : boolean
            Whether to return the squared Euclidean distance.
        Returns
        -------
        array-like
            The nearest neighbor.
            If the tree is empty, returns `None`.
            If `return_dist_sq` is true, the return will be:
                (dist_sq, point)
            else:
                point
        """
        l = self._get_knn(self._root, point, 1, return_dist_sq, [])
        return l[0] if len(l) else None


# -----------------------------------General--------------------------------------------
mod_name = preset_config["General"]["mod_name"]
ib_category_list = preset_config["General"]["ib_category_list"].split(",")
reverse_mod_path = preset_config["General"]["reverse_mod_path"]

# -----------------------------------Split--------------------------------------------
repair_tangent = preset_config["Split"]["repair_tangent"]

# 这里的part_names需要用mod_name和ib_category_list中的每个元素做拼接得到。
part_names = []
for category in ib_category_list:
    part_name = mod_name + category
    part_names.append(part_name)

# 这里的格式仅用于读取逆向mod后导出的文件，所以和reverse的格式设置是分开的，以便应对多种情况
read_ib_format = preset_config["Split"]["read_ib_format"]
write_ib_format = preset_config["Split"]["write_ib_format"]

# SplitBufferPath
split_buffer_path = reverse_mod_path + "Split/"
if not os.path.exists(split_buffer_path):
    os.mkdir(split_buffer_path)


# calculate the stride,here must use tmp_element_list from tmp.ini
tmp_element_list = preset_config["General"]["element_list"].split(",")

# 因为下面这两个dict只有分割和生成配置文件时会用到，所以不放在Tailor_Util中
# Calculate every replace_vb_slot's element_list,used in config file generate step and Split step.
category_element_list = {}
# format: {'vb0': ['POSITION'],'vb1':['NORMAL','TANGENT'],...}
for element_name in tmp_element_list:
    # You need to put it back to the slot which slot it been extract from,so here we use [extract_vb_file]
    category = vertex_config[element_name]["category"]
    slot_element_list = category_element_list.get(category)
    if slot_element_list is None:
        category_element_list[category] = [element_name]
    else:
        slot_element_list.append(element_name)
        category_element_list[category] = slot_element_list

# 根据vb_slot_element_list 获取一个步长字典，例如: {"vb0":40,"vb1":12,"vb2":24}
category_stride_dict = {}
categories = list(category_element_list.keys())
for categpory in categories:
    slot_elements = category_element_list.get(categpory)
    slot_stride = 0
    for slot_element in slot_elements:
        slot_stride_single = vertex_config[slot_element].getint("byte_width")
        slot_stride = slot_stride + slot_stride_single
    category_stride_dict[categpory] = slot_stride

# 获取所有的vb槽位
category_list = list(category_element_list.keys())


resource_ib_partnames = []
for part_name in part_names:
    name = "Resource_" + mod_name + "_" + part_name
    resource_ib_partnames.append(name)

position_category = preset_config["Split"]["position_category"]


def get_original_tangent_v2(points, tangents, position_input):
    position = position_input

    lookup = {}
    for x, y in zip(points, tangents):
        lookup[x] = y

    tree = KDTree(points, 3)

    i = 0
    while i < len(position):
        if len(points[0]) == 3:
            x, y, z = struct.unpack("f", position[i:i + 4])[0], struct.unpack("f", position[i + 4:i + 8])[0], \
                struct.unpack("f", position[i + 8:i + 12])[0]
            result = tree.get_nearest((x, y, z))[1]
            tx, ty, tz, ta = [struct.pack("f", a) for a in lookup[result]]
            position[i + 24:i + 28] = tx
            position[i + 28:i + 32] = ty
            position[i + 32:i + 36] = tz
            position[i + 36:i + 40] = ta
            i += 40
        else:
            x, y, z = struct.unpack("e", position[i:i + 2])[0], struct.unpack("e", position[i + 2:i + 4])[0], \
                struct.unpack("e", position[i + 4:i + 6])[0]
            result = tree.get_nearest((x, y, z))[1]
            tx, ty, tz, ta = [(int(a * 255)).to_bytes(1, byteorder="big") for a in lookup[result]]

            position[i + 24:i + 25] = tx
            position[i + 25:i + 26] = ty
            position[i + 26:i + 27] = tz
            position[i + 27:i + 28] = ta
            i += 28
    return position


def collect_ib(filename, offset):
    # 默认打包为DXGI_FORMAT_R16_UINT格式
    read_pack_sign = 'H'
    read_pack_stride = 2
    write_pack_sign = 'H'

    if read_ib_format == "DXGI_FORMAT_R16_UINT":
        read_pack_sign = 'H'
        read_pack_stride = 2

    if read_ib_format == "DXGI_FORMAT_R32_UINT":
        read_pack_sign = 'I'
        read_pack_stride = 4

    if write_ib_format == "DXGI_FORMAT_R16_UINT":
        write_pack_sign = 'H'

    if write_ib_format == "DXGI_FORMAT_R32_UINT":
        write_pack_sign = 'I'

    ib = bytearray()
    with open(filename, "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            ib += struct.pack(write_pack_sign, struct.unpack(read_pack_sign, data[i:i + read_pack_stride])[0] + offset)
            i += read_pack_stride
    return ib


def collect_vb_Unity(vb_file_name, collect_stride, ignore_tangent=True):
    print("Start to collect vb info from: " + vb_file_name)
    print("Collect_stride: " + str(collect_stride))
    print(category_element_list)
    print(category_stride_dict)

    position_width = vertex_config["POSITION"].getint("byte_width")
    normal_width = vertex_config["NORMAL"].getint("byte_width")
    print("Prepare position_width: " + str(position_width))
    print("Prepare normal_width: " + str(normal_width))

    # 这里定义一个dict{vb0:bytearray(),vb1:bytearray()}类型，来依次装载每个vb中的数据
    # 其中vb0需要特殊处理TANGENT部分
    collect_vb_slot_bytearray_dict = {}

    # 这里需要额外收集一个只有POSITION的bytearray和一个只有TANGENT的数组，里面是turple类型，turple里面装着float类型的数
    position_float_list = []
    tangent_float_list = []

    with open(vb_file_name, "rb") as f:
        data = bytearray(f.read())
        i = 0
        while i < len(data):
            # print(vb_slot_stride_dict)  {'vb0': 40, 'vb1': 20, 'vb2': 32}

            # 遍历vb_slot_stride_dict，依次处理
            for vb_category in category_stride_dict:
                vb_stride = category_stride_dict.get(vb_category)

                vb_slot_bytearray = bytearray()
                # vb0一般装的是POSITION数据，所以需要特殊处理
                if vb_category == position_category:
                    # 先收集正常的所需的三个元素
                    if ignore_tangent:
                        # 先添加POSITION和NORMAL
                        vb_slot_bytearray += data[i:i + position_width + normal_width]

                        # 这里的忽略Tangent机制，原理是使用Normal替代TANGENT以达到更加近似的效果,但效果远不如KDTree修复
                        vb_slot_bytearray += data[i + position_width:i + position_width + normal_width] + bytearray(
                            struct.pack("f", 1))
                    else:
                        # 否则就全部添加上，暂时不管TANGENT了
                        vb_slot_bytearray += data[i:i + vb_stride]

                    # 再专门收集position和tangent,同时要转换成List<Turple(float,float,float)>的形式
                    pox = struct.unpack("f", data[i:i+4])[0]
                    poy = struct.unpack("f", data[i+4:i+8])[0]
                    poz = struct.unpack("f", data[i+8:i+normal_width])[0]
                    position_turple = (pox, poy, poz)
                    position_float_list.append(position_turple)

                    tox = struct.unpack("f", data[i + position_width + normal_width:i + position_width + normal_width + 4])[0]
                    toy = struct.unpack("f", data[i + position_width + normal_width + 4:i + position_width + normal_width + 8])[0]
                    toz = struct.unpack("f", data[i + position_width + normal_width + 8:i + position_width + normal_width + 12])[0]
                    toa = struct.unpack("f", data[i + position_width + normal_width + 12:i + position_width + normal_width + 16])[0]
                    tangent_float_list.append((tox, toy, toz, toa))

                else:
                    vb_slot_bytearray += data[i:i + vb_stride]

                # print("collecting vb_slot:")
                # print(vb_stride_slot)
                #
                # print("collected vb_slot_bytearray: ")
                # print(len(vb_slot_bytearray))

                # 追加到收集的vb信息中
                original_vb_slot_bytearray = collect_vb_slot_bytearray_dict.get(vb_category)
                if original_vb_slot_bytearray is None:
                    original_vb_slot_bytearray = bytearray()
                collect_vb_slot_bytearray_dict[vb_category] = original_vb_slot_bytearray + vb_slot_bytearray

                # 更新步长
                i += vb_stride
    print(len(position_float_list))
    print(len(tangent_float_list))
    return collect_vb_slot_bytearray_dict, position_float_list, tangent_float_list



def split_ib_vb_file():
    # 首先计算步长
    stride = 0
    for element in tmp_element_list:
        stride = stride + int(vertex_config[element].getint("byte_width"))

    # collect vb
    offset = 0

    # 这里定义一个总体的vb_slot_bytearray_dict
    vb0_slot_bytearray_dict = {}

    # vb filename
    for part_name in part_names:
        vb_filename = split_buffer_path + part_name + ".vb"

        ignore_tangent = False

        if repair_tangent == "simple":
            ignore_tangent = True

        # 这里获取了vb0:bytearray() 这样的字典
        vb_slot_bytearray_dict = {}

        vb_slot_bytearray_dict, position_float_list, tangent_float_list = collect_vb_Unity(vb_filename, stride,
                                                                                               ignore_tangent=ignore_tangent)

        for vb_slot_categpory in vb_slot_bytearray_dict:
            print("category:")
            print(vb_slot_categpory)
            vb_byte_array = vb_slot_bytearray_dict.get(vb_slot_categpory)

            # 获取总的vb_byte_array:
            vb0_byte_array = vb0_slot_bytearray_dict.get(vb_slot_categpory)
            # 如果为空就初始化一下
            if vb0_byte_array is None:
                vb0_byte_array = bytearray()

            vb0_byte_array = vb0_byte_array + vb_byte_array
            vb0_slot_bytearray_dict[vb_slot_categpory] = vb0_byte_array

        # calculate nearest TANGENT,we use GIMI's method
        # see: https://github.com/SilentNightSound/GI-Model-Importer/pull/84
        if repair_tangent == "nearest":

            # 获取position
            position_vb_array = vb0_slot_bytearray_dict.get(position_category)
            position_new = get_original_tangent_v2(position_float_list, tangent_float_list, position_vb_array)
            vb0_slot_bytearray_dict[position_category] = position_new

        # collect ib
        ib_filename = split_buffer_path + part_name + ".ib"
        print("ib_filename: " + ib_filename)
        ib_buf = collect_ib(ib_filename, offset)
        with open(split_buffer_path + part_name + "_new.ib", "wb") as ib_buf_file:
            ib_buf_file.write(ib_buf)

        # After collect ib, set offset for the next time's collect
        print(offset)
        offset = len(vb0_slot_bytearray_dict.get(position_category)) // 40

    # write vb buf to file.
    for categpory in vb0_slot_bytearray_dict:
        vb0_byte_array = vb0_slot_bytearray_dict.get(categpory)

        with open(split_buffer_path + mod_name + categpory + ".buf", "wb") as byte_array_file:
            byte_array_file.write(vb0_byte_array)

    # set the draw number used in VertexLimitRaise
    draw_numbers = len(vb0_slot_bytearray_dict.get(position_category)) // 40
    tmp_config.set("Ini", "draw_numbers", str(draw_numbers))
    tmp_config.write(open(config_folder + "/tmp.ini", "w"))


if __name__ == "__main__":
    print("Start to split ib and vb file.")
    split_ib_vb_file()



