import numpy as np
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 或者 ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
# 让 x 轴和 y 轴都显示为普通数字，而不是科学计数法
plt.ticklabel_format(style='plain', useOffset=False, axis='both')
def positive_normalize(arr):
    result = (arr > 0).astype(int)
    return result

def negative_normalize(arr):
    result = (arr < 0).astype(int)
    return result

class APDLData:
    def __init__(self, file_path, N, element_length, Izz, W_top, W_bot, elastic_Modulus):
        """
        初始化 APDLData 类实例

        参数:
        - file_path: 数据文件的完整路径
        - N: 每边的节点数，文件中应有 N*N 行数据
        """
        self.Izz = Izz
        self.W_top = W_top
        self.W_bot = W_bot
        self.elastic_Modulus = elastic_Modulus
        self.element_length = element_length
        self.file_path = file_path
        self.N = N
        self.line_number = 4

        self.line_distributed_load = 10.5 * 1e3 * self.line_number
        self.line_concentrated_load = 320 * 1e3 * self.line_number
        self.live_disp_coefficient = 1.0
        self.live_force_coefficient = 1.4
        self.dead_disp_coefficient = 1.0
        self.dead_force_coefficient = 1.2

        self.displacement = None  # 位移矩阵
        self.moment = None  # 弯矩矩阵
        self.shear = None  # 剪力矩阵

        self.dead_load_displacement  = np.zeros(self.N + 1)
        self.dead_load_moment = np.zeros(self.N + 1)
        self.dead_load_shear = np.zeros(self.N + 1)
        self.dead_load_top_stress = np.zeros(self.N + 1)
        self.dead_load_bot_stress = np.zeros(self.N + 1)

        self.live_load_displacement = np.zeros((2,self.N + 1)) #0 最大值，1最小值
        self.live_load_moment = np.zeros((2,self.N + 1)) #0 最大值，1最小值
        self.live_load_shear = np.zeros((2,self.N + 1)) #0 最大值，1最小值
        self.live_load_top_stress = np.zeros((2, self.N + 1))  # 0 最大值，1最小值
        self.live_load_bot_stress = np.zeros((2, self.N + 1))  # 0 最大值，1最小值

        self.combined_moment = np.zeros((2, self.N + 1))  # 0 最大值，1最小值
        self.combined_displacement = np.zeros((2, self.N + 1))  # 0 最大值，1最小值
        self.combined_shear = np.zeros((2, self.N + 1))  # 0 最大值，1最小值
        self.combined_top_stress = np.zeros((2, self.N + 1))  # 0 最大值，1最小值
        self.combined_bot_stress = np.zeros((2, self.N + 1))  # 0 最大值，1最小值



    def read_and_validate(self):
        """
        读取文件，并检查数据合法性：
        1. 检查文件是否有 N*N 行、4 列数据
        2. 检查每个连续的 N 行（即一个块）中第一列是否保持一致

        若数据合法，则将第二、第三、第四列分别存储为 N×N 的矩阵，
        每个矩阵的第 i 行第 j 列分别表示荷载作用在 i 节点处，响应在 j 节点处的数据。
        """
        try:
            data = np.loadtxt(self.file_path)
        except Exception as e:
            raise ValueError(f"数据文件读取失败：{e}")

        expected_rows = self.N * self.N
        if data.shape[0] != expected_rows:
            raise ValueError(f"数据行数错误：预期 {expected_rows} 行，但实际有 {data.shape[0]} 行。")
        if data.shape[1] != 4:
            raise ValueError("数据列数错误：预期有 4 列。")

        # 检查每个块中第一列是否一致
        for i in range(self.N):
            block = data[i * self.N: (i + 1) * self.N, 0]
            if not np.allclose(block, block[0]):
                raise ValueError(
                    f"数据合法性检查失败：第 {i + 1} 个块（行 {i * self.N + 1} 到 {(i + 1) * self.N}）中第一列数据不一致。")

        # 存储位移、弯矩和剪力数据到矩阵中
        self.displacement = data[:, 1].reshape((self.N, self.N))
        self.moment = data[:, 2].reshape((self.N, self.N))
        self.shear = data[:, 3].reshape((self.N, self.N))

        # 可选：将节点号转换为整数（取每个块中的第一个节点号）
        self.node_ids = data[::self.N, 0].astype(int)

    def get_displacement_value(self, load_node, response_node):
        """
        根据输入的荷载节点和响应节点（1开始编号），返回位移值。

        参数:
        - load_node: 荷载作用的节点号（从1开始）
        - response_node: 响应节点号（从1开始）

        返回:
        - 对应节点组合的位移值
        """
        if load_node < 1 or load_node > self.N or response_node < 1 or response_node > self.N:
            raise ValueError("节点号必须在1到N之间")
        # 将1开始的节点号转换为0开始的索引
        return self.displacement[load_node - 1, response_node - 1]

    def get_moment_value(self, load_node, response_node):
        """
        根据输入的荷载节点和响应节点（1开始编号），返回弯矩值。

        参数:
        - load_node: 荷载作用的节点号（从1开始）
        - response_node: 响应节点号（从1开始）

        返回:
        - 对应节点组合的弯矩值
        """
        if load_node < 1 or load_node > self.N or response_node < 1 or response_node > self.N:
            raise ValueError("节点号必须在1到N之间")
        return self.moment[load_node - 1, response_node - 1]

    def get_shear_value(self, load_node, response_node):
        """
        根据输入的荷载节点和响应节点（1开始编号），返回剪力值。

        参数:
        - load_node: 荷载作用的节点号（从1开始）
        - response_node: 响应节点号（从1开始）

        返回:
        - 对应节点组合的剪力值
        """
        if load_node < 1 or load_node > self.N or response_node < 1 or response_node > self.N:
            raise ValueError("节点号必须在1到N之间")
        return self.shear[load_node - 1, response_node - 1]

    def evaluate_dead_load(self, dead_load):
        equivalent_node_load = dead_load * self.element_length
        half_equivalent_node_load = equivalent_node_load / 2.0

        for j in range(1,self.N+1):#j处的弯矩大小
            sum_displacement = 0
            sum_moment = 0
            sum_shear = 0
            for i in range(1, self.N):
                if i == 1 or i == self.N:
                    sum_displacement = sum_displacement + self.get_displacement_value(i, j) * half_equivalent_node_load
                    sum_moment = sum_moment + self.get_moment_value(i, j) * half_equivalent_node_load
                    sum_shear = sum_shear + self.get_shear_value(i,j) * half_equivalent_node_load
                else:
                    sum_displacement = sum_displacement + self.get_displacement_value(i, j) * equivalent_node_load
                    sum_moment = sum_moment + self.get_moment_value(i, j) * equivalent_node_load
                    sum_shear = sum_shear + self.get_shear_value(i, j) * equivalent_node_load
            sum_displacement = sum_displacement / self.elastic_Modulus / self.Izz
            self.dead_load_moment[j] = sum_moment
            self.dead_load_shear[j] = sum_shear
            self.dead_load_displacement[j] = sum_displacement

        self.dead_load_top_stress = self.dead_load_moment / (-self.W_top)
        self.dead_load_bot_stress = self.dead_load_moment / self.W_bot



    def evaluate_envelope_curve(self):
        equivalent_node_load = self.line_distributed_load * self.element_length

        for i in range(0, self.N):#计算第i处的弯矩最大值最小值

            moment_influence_line = self.moment[:, i]#影响线
            max_moment_influence_value = np.max(moment_influence_line)#影响线最大处
            min_moment_influence_value = np.min(moment_influence_line)  # 影响线最大处
            moment_positive_normalized = positive_normalize(moment_influence_line)#影响线正的取1，其他取0
            moment_negative_normalized = negative_normalize(moment_influence_line)  # 影响线负的取1，其他取0
            max_moment = np.sum(moment_influence_line * moment_positive_normalized * equivalent_node_load) + max_moment_influence_value * self.line_concentrated_load
            min_moment = np.sum(moment_influence_line * moment_negative_normalized * equivalent_node_load) + min_moment_influence_value * self.line_concentrated_load

            shear_influence_line = self.shear[:, i]  # 影响线
            max_shear_influence_value = np.max(shear_influence_line)  # 影响线最大处
            min_shear_influence_value = np.min(shear_influence_line)  # 影响线最大处
            shear_positive_normalized = positive_normalize(shear_influence_line)  # 影响线正的取1，其他取0
            shear_negative_normalized = negative_normalize(shear_influence_line)  # 影响线负的取1，其他取0
            max_shear = np.sum(shear_influence_line * shear_positive_normalized * equivalent_node_load) + max_shear_influence_value * self.line_concentrated_load
            min_shear = np.sum(shear_influence_line * shear_negative_normalized * equivalent_node_load) + min_shear_influence_value * self.line_concentrated_load

            displacement_influence_line = self.displacement[:, i]  # 影响线
            max_displacement_influence_value = np.max(displacement_influence_line)  # 影响线最大处
            min_displacement_influence_value = np.min(displacement_influence_line)  # 影响线最大处
            displacement_positive_normalized = positive_normalize(displacement_influence_line)  # 影响线正的取1，其他取0
            displacement_negative_normalized = negative_normalize(displacement_influence_line)  # 影响线负的取1，其他取0
            max_displacement = np.sum(displacement_influence_line * displacement_positive_normalized * equivalent_node_load) + max_displacement_influence_value * self.line_concentrated_load
            min_displacement = np.sum(displacement_influence_line * displacement_negative_normalized * equivalent_node_load) + min_displacement_influence_value * self.line_concentrated_load

            self.live_load_moment[0][i + 1] = max_moment
            self.live_load_moment[1][i + 1] = min_moment
            self.live_load_shear[0][i + 1] = max_shear
            self.live_load_shear[1][i + 1] = min_shear
            self.live_load_displacement[0][i + 1] = max_displacement / self.elastic_Modulus / self.Izz
            self.live_load_displacement[1][i + 1] = min_displacement / self.elastic_Modulus / self.Izz

            self.live_load_top_stress = self.live_load_moment / (-self.W_top)
            self.live_load_bot_stress = self.live_load_moment / self.W_bot


    def combine_live_and_dead(self):
        self.combined_moment = self.live_force_coefficient * self.live_load_moment + self.dead_force_coefficient * self.dead_load_moment
        self.combined_shear = self.live_force_coefficient * self.live_load_shear + self.dead_force_coefficient * self.dead_load_shear
        self.combined_top_stress = self.combined_moment / (-self.W_top)
        self.combined_bot_stress = self.combined_moment / self.W_bot

        self.combined_displacement = self.live_disp_coefficient * self.live_load_displacement + self.dead_disp_coefficient * self.dead_load_displacement

    def plot_series(self, x, data, labels=None, title="Multi-Series Plot",
                    xlabel="X-Axis(m)", ylabel="Y-Axis", grid=True,
                    linewidth=1.5, figsize=(10, 6)):
        """
        绘制多序列的折线图

        参数:
        - x: 1D数组，形状为 (N,)，表示横轴坐标
        - data: 2D数组，形状为 (M, N)，表示 M 个序列的数据
        - labels: 列表，长度 M，每个序列的标签（默认为 Series 1, Series 2...）
        - title: 图表标题
        - xlabel/yabel: 坐标轴标签
        - grid: 是否显示网格
        - linewidth: 线条宽度
        - figsize: 图表尺寸
        """
        # 检查数据维度是否匹配
        if x.shape[0] != data.shape[1]:
            raise ValueError("x 的长度必须与 data 的列数一致")

        # 创建画布和坐标轴
        plt.figure(figsize=figsize)

        # 自动生成标签（如果未提供）
        if labels is None:
            labels = [f"Series {i + 1}" for i in range(data.shape[0])]
        elif len(labels) != data.shape[0]:
            raise ValueError("labels 的长度必须与 data 的行数一致")

        # 绘制每个序列
        for i, (row, label) in enumerate(zip(data, labels)):
            plt.plot(x, row, label=label, linewidth=linewidth)

        # 添加装饰元素
        plt.xlim(0, self.element_length*(self.N-1))
        plt.title(title, fontsize=12)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(grid)
        plt.legend()
        plt.tight_layout()
        plt.show()



# 使用示例：
if __name__ == '__main__':
    # 假设文件存储在 'C:\Projects\APDLProjects\homework03\data.txt'
    file_path = r"C:\Projects\APDLProjects\homework03\data.txt"
    N = 91  # 可根据实际情况修改
    element_length = 1.0
    Izz = 0.2
    elastic_Modulus = 2.0e5 * 1e6 #MPa应乘10的6次方
    data_parser = APDLData(file_path=file_path,
                           N=N,
                           element_length=element_length,
                           Izz=Izz,
                           W_top=0.3,
                           W_bot=0.2,
                           elastic_Modulus=elastic_Modulus)
    data_parser.read_and_validate()
    data_parser.evaluate_dead_load(200*1000)
    data_parser.evaluate_envelope_curve()
    data_parser.combine_live_and_dead()
    x_arr = np.linspace(0, element_length * (N-1), N)
    x_arr = np.insert(x_arr, 0, 0)
    data_parser.plot_series(x_arr, data_parser.combined_moment)

    for i in range(1,N+1):
        #print(data_parser.dead_load_shear[i])
        print(f"{data_parser.combined_moment[0][i]:.8f}\t{data_parser.combined_moment[1][i]:.8f}")




