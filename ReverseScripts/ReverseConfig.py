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
read_dxgi_format = preset_config["Format"]["read_dxgi_format"]
write_dxgi_format = preset_config["Format"]["write_dxgi_format"]

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

