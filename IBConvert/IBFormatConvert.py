import configparser
import struct

# 解析配置文件
preset_config = configparser.ConfigParser()
preset_config.read("Configs/preset.ini", "utf-8")

# 读取ib文件路径
ib_file_path = preset_config["General"]["ib_file_path"]

# 设置读取和输出的格式
read_ib_format = preset_config["General"]["read_ib_format"]
write_ib_format = preset_config["General"]["write_ib_format"]


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


if __name__ == "__main__":
    ib_bytearray = collect_ib(ib_file_path,0)
    new_ib_file = open(ib_file_path + "_" + write_ib_format + ".ib", "wb")
    new_ib_file.write(ib_bytearray)
    new_ib_file.close()