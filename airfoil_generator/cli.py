import os
import time
from pathlib import Path
import math
import random
import scipy.io as scio

from .utils import get_args, read_database, makeDirs
from .preprocess import (
    genMesh,
    set_transfile,
    set_ufile,
    set_decomposefile,
    set_runfile,
)
from .postprocess import (
    coord2img,
    get_airfoil_data,
    get_grid_data,
    get_raw_mesh
)

def main():
    args = get_args('config.yml')

    here = Path('./').absolute()
    case_dir = Path(args.case_dir).absolute()
    makeDirs(args.output_dir)

    set_transfile(case_dir, args.rho, args.nu)
    if args.parallel_enable:
        set_decomposefile(case_dir, args)
    files = read_database(args.airfoil_database)

    for n in range(args.n_samples):
        t0 = time.time()
        print(f"\nRun {n}:")

        # 设置流场参数
        length = random.uniform(args.freestream_length[0], args.freestream_length[1])
        angle = random.uniform(args.freestream_angle[0], args.freestream_angle[1]) # 单位：度
        fsX = math.cos(angle / 180 * math.pi) * length
        fsY = math.sin(angle / 180 * math.pi) * length
        set_ufile(case_dir, fsX, fsY)
        print(f"\tUsing len {length:.2f} angle {angle:.2f}")
        print(f"\tResulting freestream vel x,y: {fsX:.2f},{fsY:.2f}")

        # 画网格
        if args.fixed_airfoil:
            fname = f'{args.airfoil_name}.dat'
        else:
            fname = random.choice(files)
        fpath = here / f'{args.airfoil_database}/{fname}'
        print(f"\tusing {fpath}")

        os.chdir(case_dir)
        if genMesh(str(fpath)) != 0:
            print("\tmesh generation failed, aborting")
            os.chdir(str(here))
            continue

        set_runfile(case_dir, args.subdomains, args.parallel_enable)
        # 运行仿真
        os.system("sh ./Allclean > foam.log")
        os.system("sh ./Allrun >> foam.log")

        # 后处理
        if args.output_raw_mesh:
            os.system("postProcess -func writeCellCentres -noZero >> foam.log")
        if args.output_airfoil_boundary:
            os.system("postProcess -func 'components(U)' -noZero >> foam.log")

        os.chdir(str(here))

        # 外部流场，图片形式
        data_img = coord2img(fsX, fsY, args)
        grid_data = get_grid_data(args)

        data_dict = {
            'fsX': fsX,
            'fsY': fsY,
            **data_img,
            **grid_data,
        }

        if args.output_raw_mesh:
            raw_mesh_data = get_raw_mesh(args)
            data_dict.update(raw_mesh_data)
        if args.output_airfoil_boundary:
            airfoil_data = get_airfoil_data(args)
            data_dict.update(airfoil_data)

        save_path = f'{args.output_dir}/{args.output_prefix}{n}.mat'
        scio.savemat(save_path, data_dict)
        print("\tdone")
        t1 = time.time()
        print(f'\t{t1-t0:.2f}s')


if __name__ == '__main__':
    main()
