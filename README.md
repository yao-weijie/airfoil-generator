一个机翼外流场数据集生成器，修改自[论文](http://arxiv.org/abs/1810.08217) [code](https://github.com/thunil/Deep-Flow-Prediction)

# 1.OpenFOAM的安装

0. OpenFOAM有两种安装方式，一种是用官网的已经编译打包好的，缺点不方便更改源码，另一种是下载源码自行编译，优点是方便二次开发，缺点是编译非常耗时。我们只是用来生成数据，采用第一种方式。

1. 安装OpenFOAM和gmsh(网格生成工具)

   ```sh
   sudo sh -c "wget -O - https://dl.openfoam.org/gpg.key | apt-key add -"
   sudo add-apt-repository http://dl.cfdem.cn/ubuntu
   sudo apt update
   sudo apt install openfoam5 gmsh
   source /opt/openfoam5/etc/bashrc
   ```

   青云上我已经打包好了一个OpenFOAM镜像，需要的可以找我。

2. 通过上述方式安装的OpenFOAM在`/opt/openfoam5` 目录中，官方算例在`/opt/openfoam5/tutorials`，，需要的可以拷贝到home目录进行学习

   ```sh
   cp -r /opt/openfoam5/tutorials ~/openfoam5-tutorials
   ```



# 2. 生成器的安装

1. 从gitlab下载源码并安装

   ```sh
   cd
   git clone https://git.idrl.site/lavateinn/airfoil-generator.git
   cd airfoil-generator/
   python -m pip install -U pip
   sudo python setup.py install
   ```

2. 检查是否安装成功，查看生成器支持的参数

   ```sh
   airfoil_generator --help
   ```

3. 后续有新版本发布时，更新生成器

   ```sh
   cd
   cd airfoil-generator
   git pull origin master:master
   sudo python setup.py install
   ```



# 3. 生成器的使用

## 3.1 目录结构

目前的项目目录结构

```
.
├── README.md
├── airfoil_database  翼型数据
├── airfoil_database_test  翼型数据
├── airfoil_generator  生成器源码
├── caseSteadyState  稳态算例模板
├── config.yml  生成器配置文件
├── download_airfoils.sh
├── outputs  默认输出路径
├── requirements.txt
└── setup.py
```

可见算例目录和源码目录在一起的，这边推荐需要生成数据的话另行创建一个工作目录

```sh
cd
mkdir airfoil-workspace
cp -r airfoil-generator/airfoil_database* airfoil-generator/config.yml airfoil-generator/case* -d airfoil-workspace
```

```sh
airfoil-workspace
├── airfoil_database
├── airfoil_database_test
├── caseSteadyState
└── config.yml
```

## 3.2 配置文件

进入`airfoil-workspace` 目录直接执行`airfoil_generator` 就可以生成数据了。

**当前的版本在执行`airfoil_generator` 的时候必须和`config.yml`在相同目录下**

默认配置文件

```yaml
#seed: 3383525914
case-dir: 'caseSteadyState'  # 算例路径
airfoil-database: 'airfoil_database'  # 翼型数据库路径
fixed-airfoil: True # 是否固定一种翼型，为False时在上述路径中随机采样，为True时下面的参数有效
airfoil-name: 'falcon'

freestream-angle:  # 来流角度，均匀采样，如果上下限相等，则为固定值
  - 0
  - 20
freestream-length:  # 来流速度大小，均匀采样，如果上下限相等，则为固定值
  - 0
  - 50

# 流体物性参数
rho: 1  # 密度 kg/m^3
nu: 1e-5 # 运动粘度

# 并行设置
parallel-enable: True
subdomains: 7  # 计算域分解的数量，一般不超过物理核心数

# 后处理
res: 128  # 输出图像的分辨率,暂时不可调
output-raw-mesh: True
output-airfoil-boundary: True

# 输出
n-samples: 2  # 生成的样本数量
output-dir: 'outputs'
output-prefix: 'sample'
```



## 3.3 算例简介

算例来自[论文](http://arxiv.org/abs/1810.08217) [code](https://github.com/thunil/Deep-Flow-Prediction) 

![fJeAQ.png](https://s1.328888.xyz/2022/04/11/fJeAQ.png)

仿真流程：翼型坐标数据文件->生成网格->仿真->后处理，

主要讲一下后处理，导出的数据主要通过后处理获得：

- 采样

  由上图可见整个仿真的计算域是很大的，但是我们只关系机翼周边的一块区域，所以后处理会在机翼周围采样。机翼的$`x`$坐标范围基本在$`[0, 1]`$，采样区域(上图inference region)默认是在$`x \in [-0.5, 1.5), y \in [-0.5, 0.5)`$， 分辨率128。范围和分辨率暂时都不可调。

  导出的数据读出来的图像机翼是竖起来的，可以自行旋转，下面是一个样本例子。

  ![fJiKX.png](https://s1.328888.xyz/2022/04/11/fJiKX.png)

- 机翼表面

  导出机翼表面测点的$`x, y, p`$ 信息，不同翼型的表面测点数量不太一致。**目前导出的机翼表面测点顺序是乱的，需要排序。**

  

## 3.4 导出的数据简介

每个生成的样本都是一个`mat`文件，用`scipy.io`读出来是一个字典。

```python
import scipy.io as scio
data = scio.loadmat('./outputs/sample0.mat')
for k in data:
    print(k)
```

输出数据如下：

```
# part 0 mat格式信息，不用管
__header__
__version__
__globals__

# part 1：来流速度信息，xy两个分量
fsX
fsY

# 采样区域流场中的栅格点的坐标和信息，遇到机翼内部会跳过
grid_x
grid_y
grid_p
grid_u
grid_v

# 上述采样域生成的图像
fx_img
fy_img
mask_img
p_img
Ux_img
Uy_img

# OpenFOAM里整个计算域内所有网格的中心坐标和速度压强
cell_x
cell_y
cell_p
cell_Ux
cell_Uy

# 机翼表面信息，坐标和压强
airfoil_x
airfoil_y
airfoil_p
```

**后续更新中上述mat文件的key-value组织可能有所变化。**



# 4. 后续功能

- 自定义分辨率，采样域
- CST参数化翼型仿真
- 瞬态
- ...





