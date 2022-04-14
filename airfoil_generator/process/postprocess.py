import numpy as np
import linecache


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
    dir = f'{args.case_dir}/postProcessing/internalCloud/500/'
    res = args.res
    npOutput = np.zeros((6, res, res), dtype=np.float32)

    pfile = f'{dir}/cloud_p.xy'
    ar = np.loadtxt(pfile)
    curIndex = 0

    for y in range(res):
        for x in range(res):
            xf = (x / res - 0.5) * 2 + 0.5
            yf = (y / res - 0.5) * 2
            if abs(ar[curIndex][0] - xf) < 1e-4 and abs(ar[curIndex][1] -
                                                        yf) < 1e-4:
                npOutput[3][x][y] = ar[curIndex][3]
                curIndex += 1
                # fill input as well
                npOutput[0][x][y] = freestreamX
                npOutput[1][x][y] = freestreamY
            else:
                npOutput[3][x][y] = 0
                # fill mask
                npOutput[2][x][y] = 1.0

    ufile = f'{dir}/cloud_U.xy'
    ar = np.loadtxt(ufile)
    curIndex = 0

    for y in range(res):
        for x in range(res):
            xf = (x / res - 0.5) * 2 + 0.5
            yf = (y / res - 0.5) * 2
            if abs(ar[curIndex][0] - xf) < 1e-4 and abs(ar[curIndex][1] -
                                                        yf) < 1e-4:
                npOutput[4][x][y] = ar[curIndex][3]
                npOutput[5][x][y] = ar[curIndex][4]
                curIndex += 1
            else:
                npOutput[4][x][y] = 0
                npOutput[5][x][y] = 0

    data_img = {
        'fx_img': npOutput[0],
        'fy_img': npOutput[1],
        'mask_img': npOutput[2],
        'p_img':  npOutput[3],
        'Ux_img': npOutput[4],
        'Uy_img': npOutput[5],
    }
    return data_img


def get_airfoil_data(args):
    # 机翼上测点的压强
    aerofoil_p = np.loadtxt(f'{args.case_dir}/postProcessing/airfoilBoundary/500/p_aerofoil.raw', skiprows=2, dtype=np.float32)
    airfoil_x = aerofoil_p[:, 0]
    airfoil_y = aerofoil_p[:, 1]
    airfoil_p = aerofoil_p[:, 3]
    airfoil_data = {
        'airfoil_x': airfoil_x,
        'airfoil_y': airfoil_y,
        'airfoil_p': airfoil_p,
    }
    return airfoil_data


def get_grid_data(args):
    # 外部流场点云采样的原始数据
    cloud_p = np.loadtxt(f'{args.case_dir}/postProcessing/internalCloud/500/cloud_p.xy', dtype=np.float32)
    cloud_U = np.loadtxt(f'{args.case_dir}/postProcessing/internalCloud/500/cloud_U.xy', dtype=np.float32)
    grid_x = cloud_p[:, 0]
    grid_y = cloud_p[:, 1]
    grid_p = cloud_p[:, 3]
    grid_u = cloud_U[:, 3]
    grid_v = cloud_U[:, 4]

    grid_data = {
        'grid_x': grid_x,
        'grid_y': grid_y,
        'grid_p': grid_p,
        'grid_u': grid_u,
        'grid_v': grid_v,
    }
    return grid_data


def get_raw_mesh(args):
    # 流场中网格的原始数据，网格中心坐标，对应的p,U
    nCells = int(linecache.getline(f'{args.case_dir}/500/p', lineno=21))

    cell_x = linecache.getlines(f'{args.case_dir}/500/Cx')[22:22+nCells]
    cell_x = np.array([float(x.strip()) for x in cell_x])

    cell_y = linecache.getlines(f'{args.case_dir}/500/Cy')[22:22+nCells]
    cell_y = np.array([float(y.strip()) for y in cell_y])

    cell_p = linecache.getlines(f'{args.case_dir}/500/p')[22:22+nCells]
    cell_p = np.array([float(p.strip()) for p in cell_p])

    cell_Ux = linecache.getlines(f'{args.case_dir}/500/Ux')[22:22+nCells]
    cell_Ux = np.array([float(Ux.strip()) for Ux in cell_Ux])

    cell_Uy = linecache.getlines(f'{args.case_dir}/500/Uy')[22:22+nCells]
    cell_Uy = np.array([float(Uy.strip()) for Uy in cell_Uy])

    raw_mesh_data = {
        'cell_x': cell_x,
        'cell_y': cell_y,
        'cell_p': cell_p,
        'cell_Ux': cell_Ux,
        'cell_Uy': cell_Uy,
    }
    return raw_mesh_data
