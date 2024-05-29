def hex2float(hex_num: str) -> str:
    """
    将25位宽的16进制数转换成对应的定点小数
    :param
        hex_num: 25位16进制数
    :return: 定点小数
    """
    # 将16进制数转换为25位宽的二进制字符串
    binary_num = bin(int(hex_num, 16))[2:].zfill(25)
    # 提取符号位和剩下的23位数
    sign_bit = binary_num[:2]
    value_bits = binary_num[2:]
    # 解释符号位并计算最终结果
    if sign_bit == "11":
        # 负数的情况下，先取反再加一
        inverted_bits = ''.join('1' if bit == '0' else '0' for bit in value_bits)
        value = -(int(inverted_bits, 2) + 1) / 2 ** 22
    else:
        value = int(value_bits, 2) / 2 ** 22

    value = "{:.6f}".format(value)
    return value


def vivado_data_hex2float(vivado_output_path: list) -> list:
    """
    处理vivado的输出，将输出的25位宽的16进制数转换成定点小数
    :param
        vivado_output_path: 存储vivado输出的i值和q值路径
    :return 转换成定点小数后的i值和q值路径
    """
    # 打开文件
    i_values = []
    q_values = []
    with open(vivado_output_path[0], "r") as file_i:
        # 读取文件内容
        lines = file_i.readlines()
        for hex_data in lines:
            i_values.append(str(hex2float(hex_data)))
    with open(vivado_output_path[1], "r") as file_q:
        # 读取文件内容
        lines = file_q.readlines()
        for hex_data in lines:
            q_values.append(str(hex2float(hex_data)))

    file_i_float = vivado_output_path[0][:-4] + '_float.txt'
    file_q_float = vivado_output_path[1][:-4] + '_float.txt'
    # 打开文件以写入模式
    with open(file_i_float, "w") as file_i:
        for i in i_values:
            file_i.write(i + "\n")

    with open(file_q_float, "w") as file_q:
        for q in q_values:
            file_q.write(q + "\n")
    return [file_i_float, file_q_float]


def dvb_compare(vivado_output_path: list, matlab_output_path: list, num: int) -> float:
    """
    对比vivado输出和matlab输出，返回差值
    :param
        vivado_output_path: 存储vivado输出的i值和q值路径
        matlab_output_path: 存储matlab输出的i值和q值路径
        num: 指定比较的数量
    :return: 对比差值
    """
    # 处理vivado的i值和q值，转换成定点小数
    vivado_output_float_path = vivado_data_hex2float(vivado_output_path)
    delta, delta_i, delta_q = 0, 0, 0
    vivado_float_i, vivado_float_q = [], []
    matlab_float_i, matlab_float_q = [], []
    # 读取vivado的i值和q值
    with open(vivado_output_float_path[0]) as vivado_i:
        lines = vivado_i.readlines()
        for i in lines:
            vivado_float_i.append(float(i))
    with open(vivado_output_float_path[1]) as vivado_q:
        lines = vivado_q.readlines()
        for q in lines:
            vivado_float_q.append(float(q))
    # 读取matlab的i值和q值
    with open(matlab_output_path[0]) as matlab_i:
        lines = matlab_i.readlines()
        for i in lines:
            matlab_float_i.append(float(i))
    with open(matlab_output_path[1]) as matlab_q:
        lines = matlab_q.readlines()
        for q in lines:
            matlab_float_q.append(float(q))

    # 计算i值的差值
    try:
        if len(vivado_float_i) != len(matlab_float_i):
            raise ValueError("vivado和matlab的输出长度不同!")
        else:
            for i in range(num):
                delta_i = delta_i + abs(vivado_float_i[i] - matlab_float_i[i])
    except ValueError as e:
        print(e)

    # 计算q值的差值
    try:
        if len(vivado_float_q) != len(matlab_float_q):
            raise ValueError("vivado和matlab的输出长度不同!")
        else:
            for i in range(num):
                delta_q = delta_q + abs(vivado_float_q[i] - matlab_float_q[i])
    except ValueError as e:
        print(e)

    delta = delta_i + delta_q
    return delta


if __name__ == "__main__":
    vivado_output_path = ['data/fir_i_out.txt', 'data/fir_q_out.txt']
    matlab_output_path = ['data/matlab_i_out.txt', 'data/matlab_q_out.txt']
    delta = dvb_compare(vivado_output_path, matlab_output_path, 33372)
    print(delta)