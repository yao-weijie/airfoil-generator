import configargparse
import random


def str2bool(v):
    if v.lower() in ('true', '1'):
        return True
    elif v.lower() in ('false', '0'):
        return False
    else:
        raise configargparse.ArgumentTypeError('Unsupported value encountered.')


def get_args(parser: configargparse.ArgumentParser):
    parser._config_file_parser = configargparse.YAMLConfigFileParser()

    parser.add_argument('--config', is_config_file=True, default='config.yml', help='config file path')

    parser.add_argument('--seed', type=int, default=random.randint(0,2**32-1), help='随机种子')
    parser.add_argument('--case-dir', type=str, default='caseSteadyState', help='case路径')

    # 机翼设置
    parser.add_argument('--airfoil-database', type=str, default='airfoil_database', help='翼型数据库')
    parser.add_argument('--fixed-airfoil', type=str2bool, default=True, help='是否固定翼型')
    parser.add_argument('--airfoil-name', type=str, default='falcon', help='固定的翼型名称')

    # 来流设置
    parser.add_argument('--freestream-angle', type=float, nargs='+', help='来流角度范围')
    parser.add_argument('--freestream-length', type=float, nargs='+', help='来流角度大小范围')

    # 物性参数
    parser.add_argument('--rho', type=float, default=1, help='流体密度')
    parser.add_argument('--nu', type=float, default=1e-5, help='流体运动粘度')

    # 并行设置
    parser.add_argument('--parallel-enable', type=str2bool, default=False, help='并行设置')
    parser.add_argument('--subdomains', type=int, default=4, help='计算域分解数量')

    # 后处理
    parser.add_argument('--res', type=int, default=128, help='输出图像分辨率')
    parser.add_argument('--output-raw-mesh', type=str2bool, default=True, help='是否输出网格数据')
    parser.add_argument('--output-airfoil-boundary', type=str2bool, default=True, help='是否输出机翼表面数据')

    # 输出设置
    parser.add_argument('--n-samples', type=int, default=2, help='生成样本的数量')
    parser.add_argument('--output-dir', type=str, default='outputs', help='数据输出路径')
    parser.add_argument('--output-prefix', type=str, default='sample', help='输出样本前缀')


    # return args
    return parser


def make_config(args, output_path):
    pass
