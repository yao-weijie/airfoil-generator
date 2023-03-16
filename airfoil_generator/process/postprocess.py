import numpy as np
import scipy.io as scio
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile


def read_sample(case_dir, xrange, yrange, res):
    ufile = f"{case_dir}/postProcessing/internalCloud/500/cloud_U.xy"
    pfile = f"{case_dir}/postProcessing/internalCloud/500/cloud_p.xy"

    points = np.loadtxt(ufile)
    # 计算图像上的坐标
    px = points[:, 0]
    py = points[:, 1]
    coord_x = (px - xrange[0]) / (xrange[1] - xrange[0]) * (res[0] - 1)
    coord_y = (py - yrange[0]) / (yrange[1] - yrange[0]) * (res[1] - 1)
    # 之前中心的两条线,是这里四舍五入造成的误差
    coord_x = np.around(coord_x).astype(int)
    coord_y = np.around(coord_y).astype(int)

    ux = points[:, 3]
    uy = points[:, 4]
    p = np.loadtxt(pfile)[:, 3]
    outputs = np.zeros((3, int(res[0]), int(res[1])))
    for i, (x, y) in enumerate(zip(coord_x, coord_y)):
        outputs[0, x - 1, y - 1] = ux[i]
        outputs[1, x - 1, y - 1] = uy[i]
        outputs[2, x - 1, y - 1] = p[i]

    return outputs


# case_dir = '/home/yao/work/airfoil-generator/caseSteadyState/'
# xrange = [-0.5, 1.5]
# yrange = [-1.0, 1.0]
# res = [512, 512]

# read_sample(case_dir, xrange, yrange, res)


def coord2img(
    freestreamX,
    freestreamY,
    args,
):
    # output layout channels:
    # [0] freestream field X + boundary
    # [1] freestream field Y + boundary
    # [2] binary mask for boundary
    # [3] pressure output
    # [4] velocity X output
    # [5] velocity Y output
    dir = f"{args.case_dir}/postProcessing/internalCloud/500/"
    res = args.res
    npOutput = np.zeros((6, res, res), dtype=np.float32)

    pfile = f"{dir}/cloud_p.xy"
    ar = np.loadtxt(pfile)
    curIndex = 0

    for y in range(res):
        for x in range(res):
            xf = (x / res - 0.5) * 2 + 0.5
            yf = (y / res - 0.5) * 2
            if abs(ar[curIndex][0] - xf) < 1e-4 and abs(ar[curIndex][1] - yf) < 1e-4:
                npOutput[3][x][y] = ar[curIndex][3]
                curIndex += 1
                # fill input as well
                npOutput[0][x][y] = freestreamX
                npOutput[1][x][y] = freestreamY
            else:
                npOutput[3][x][y] = 0
                # fill mask
                npOutput[2][x][y] = 1.0

    ufile = f"{dir}/cloud_U.xy"
    ar = np.loadtxt(ufile)
    curIndex = 0

    for y in range(res):
        for x in range(res):
            xf = (x / res - 0.5) * 2 + 0.5
            yf = (y / res - 0.5) * 2
            if abs(ar[curIndex][0] - xf) < 1e-4 and abs(ar[curIndex][1] - yf) < 1e-4:
                npOutput[4][x][y] = ar[curIndex][3]
                npOutput[5][x][y] = ar[curIndex][4]
                curIndex += 1
            else:
                npOutput[4][x][y] = 0
                npOutput[5][x][y] = 0

    # data_img = {
    #     "fsX_img": npOutput[0],
    #     "fsY_img": npOutput[1],
    #     "mask_img": npOutput[2],
    #     "p_img": npOutput[3],
    #     "Ux_img": npOutput[4],
    #     "Uy_img": npOutput[5],
    # }
    return npOutput


def get_airfoil_data(case_dir):
    # 机翼上测点的压强
    aerofoil_p = np.loadtxt(
        f"{case_dir}/postProcessing/airfoilBoundary/500/p_aerofoil.raw",
        skiprows=2,
        dtype=np.float32,
    )
    aerofoil_p = sort_points(aerofoil_p[:, [0, 1, 3]])
    airfoil_x = aerofoil_p[:, 0]
    airfoil_y = aerofoil_p[:, 1]
    airfoil_p = aerofoil_p[:, 2]
    airfoil_data = {
        "airfoil_x": airfoil_x,
        "airfoil_y": airfoil_y,
        "airfoil_p": airfoil_p,
    }
    return airfoil_data


def get_grid_data(args):
    # 外部流场的网格节点数据
    cloud_p = np.loadtxt(
        f"{args.case_dir}/postProcessing/internalCloud/500/cloud_p.xy", dtype=np.float32
    )
    cloud_U = np.loadtxt(
        f"{args.case_dir}/postProcessing/internalCloud/500/cloud_U.xy", dtype=np.float32
    )
    grid_x = cloud_p[:, 0]
    grid_y = cloud_p[:, 1]
    grid_p = cloud_p[:, 3]
    grid_u = cloud_U[:, 3]
    grid_v = cloud_U[:, 4]
    grid_data = {
        "grid_x": grid_x,
        "grid_y": grid_y,
        "grid_p": grid_p,
        "grid_Ux": grid_u,
        "grid_Uy": grid_v,
    }

    grid_xyp = cloud_p[:, [0, 1, 3]]
    grid_uv = cloud_U[:, [3, 4]]
    grid_data = np.concatenate([grid_xyp, grid_uv], axis=1)

    return grid_data


def get_raw_mesh(case_dir):
    # 流场中网格的原始数据，网格中心坐标，对应的p,U

    cell_xyz = ParsedParameterFile(
        f"{case_dir}/500/C").content["internalField"]
    cell_p = ParsedParameterFile(f"{case_dir}/500/p").content["internalField"]
    cell_U = ParsedParameterFile(f"{case_dir}/500/U").content["internalField"]

    cell_x = np.array(cell_xyz)[:, 0]
    cell_y = np.array(cell_xyz)[:, 1]
    cell_p = np.array(cell_p)
    cell_Ux = np.array(cell_U)[:, 0]
    cell_Uy = np.array(cell_U)[:, 1]

    raw_mesh_data = {
        "cell_x": cell_x,
        "cell_y": cell_y,
        "cell_p": cell_p,
        "cell_Ux": cell_Ux,
        "cell_Uy": cell_Uy,
    }

    return raw_mesh_data


def sort_points(points):
    """将散乱的点按照机翼表面轮廓的顺序排列
    输入输出都是二维array，每一行都是一个样本点
    排序后最右侧点为起点，绕逆时针一周
    """
    sorted_points = [[], [], []]
    idx = np.argsort(points[:, 0]).tolist()  # 升序
    x = points[idx, 0]
    y = points[idx, 1]
    p = points[idx, 2]

    for i, (_x, _y, _p) in enumerate(zip(x, y, p)):
        if i == 0:
            sorted_points[0].append(x[i])
            sorted_points[1].append(y[i])
            sorted_points[2].append(p[i])
        elif i == 1:
            if _y >= sorted_points[1][-1]:
                sorted_points[0].insert(0, x[i])
                sorted_points[1].insert(0, y[i])
                sorted_points[2].insert(0, p[i])
            else:
                sorted_points[0].append(_x)
                sorted_points[1].append(_y)
                sorted_points[2].append(_p)
        else:
            if abs(_y - sorted_points[1][0]) < abs(_y - sorted_points[1][-1]):
                sorted_points[0].insert(0, x[i])
                sorted_points[1].insert(0, y[i])
                sorted_points[2].insert(0, p[i])
            else:
                sorted_points[0].append(x[i])
                sorted_points[1].append(y[i])
                sorted_points[2].append(p[i])
    return np.array(sorted_points).T


def read(fname, suffix):
    """读取单个文件,返回数据字典

    fname: 文件完整路径
    suffix: 文件名后缀, 可选mat和npz, mat字典不可嵌套, npz字典可嵌套
    """
    if suffix == "mat":
        data = scio.loadmat(fname)
    elif suffix == "npz":
        data = np.load(fname, allow_pickle=True)["data"][()]
    else:
        raise "unsupported suffix: {suffix}"

    return data
