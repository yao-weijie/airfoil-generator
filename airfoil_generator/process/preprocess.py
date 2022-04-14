import os
import numpy as np
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile


def set_transfile(case_dir, rho, nu):
    # 设置物性参数
    transFile = ParsedParameterFile(f'{case_dir}/constant/transportProperties')
    transFile['rho'][1] = rho
    transFile['nu'][1] = nu
    transFile.writeFile()
    print(f'set rho={rho}, nu={nu}')


def set_decomposefile(case_dir, args):
    # 设置计算域分解文件
    decomposeParDict = ParsedParameterFile(f'{case_dir}/system/decomposeParDict')
    decomposeParDict['numberOfSubdomains'] = args.subdomains
    decomposeParDict.writeFile()
    print(f'set subdomains={args.subdomains}')


def set_runfile(case_dir, subdomains, parallel_enable):
    cmd = ""
    cmd += "cd ${0%/*} || exit\n"
    cmd += ". $WM_PROJECT_DIR/bin/tools/RunFunctions\n"
    cmd += "application=`getApplication`\n"
    if parallel_enable:
        cmd += "decomposePar -force >> foam.log\n"
        cmd += f"mpirun -np {subdomains} $application -parallel >> foam.log\n"
        cmd += "reconstructPar >> foam.log\n"
    else:
        cmd += "$application >> foam.log\n"

    with open(f'{case_dir}/Allrun', 'w') as f:
        f.write(cmd)


def set_ufile(case_dir, fsX, fsY):
    ufile = ParsedParameterFile(f'{case_dir}/0/U')
    ufile['internalField'] = f'uniform ({fsX:.4f} {fsY:.4f} 0)'
    for bname, bdict in ufile['boundaryField'].items():
        if bdict.get('type') == 'freestream':
            bdict['freestreamValue'] = f'uniform ({fsX:.4f} {fsY:.4f} 0)'
    ufile.writeFile()


def pre_process(args):
    set_transfile(args.case_dir, args.rho, args.nu)
    if args.parallel_enable:
        set_decomposefile(args)
    set_runfile(args, args.case_dir, args.subdomains)


def genMesh(airfoilFile):
    ar = np.loadtxt(airfoilFile, skiprows=1)

    # removing duplicate end point
    if np.max(np.abs(ar[0] - ar[-1])) < 1e-6:
        ar = ar[:-1]
    npoints = ar.shape[0]

    output = ""
    pointIndex = 1000
    for n in range(npoints):
        output += "Point({}) = {{ {}, {}, 0.00000000, 0.005}};\n".format(
            pointIndex, ar[n][0], ar[n][1])
        pointIndex += 1

    with open("airfoil_template.geo", "rt") as inFile:
        with open("airfoil.geo", "wt") as outFile:
            for line in inFile:
                line = line.replace("POINTS", "{}".format(output))
                line = line.replace("LAST_POINT_INDEX",
                                    "{}".format(pointIndex - 1))
                outFile.write(line)

    if os.system("gmsh airfoil.geo -3 -o airfoil.msh > /dev/null") != 0:
        print("error during mesh creation!")
        return -1

    if os.system("gmshToFoam airfoil.msh > /dev/null") != 0:
        print("error during conversion to OpenFoam mesh!")
        return -1

    with open("constant/polyMesh/boundary", "rt") as inFile:
        with open("constant/polyMesh/boundaryTemp", "wt") as outFile:
            inBlock = False
            inAerofoil = False
            for line in inFile:
                if "front" in line or "back" in line:
                    inBlock = True
                elif "aerofoil" in line:
                    inAerofoil = True

                if inBlock and "type" in line:
                    line = line.replace("patch", "empty")
                    inBlock = False
                if inAerofoil and "type" in line:
                    line = line.replace("patch", "wall")
                    inAerofoil = False
                outFile.write(line)
    os.rename("constant/polyMesh/boundaryTemp", "constant/polyMesh/boundary")

    return 0