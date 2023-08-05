# 利用neutron和allStructure生成fispact输入文件
# 输入：文件地址，neutron，allStructure
# 输出：无

import os
import re

from .model import Data, ele, Avogadro, defaultInput, defaultArrayx, defaultCollapx, defaultPrintlib


def _mkdir(path):
    # 仅内部调用
    # 在完整路径处新建文件夹
    # path--input--建立文件夹位置
    # *--output--bool,是否成功建立文件夹
    assert type(path) == str, '%s路径不合法' % path
    path = path.strip()
    path = path.rstrip("\\")
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    else:
        return False


def _collapx(text, cell, path, func=None, call=False, clear=False):
    # 仅内部调用
    # 生成FISPACT输入文件collapx.i
    # text--input--初始化文件内容
    # cell--input--材料名称
    # path--input--FISPACT输入文件顶层路径
    assert type(text) == str, 'FISPACT文件内容不合法'
    assert type(cell) == str, '材料名称不合法'
    assert type(path) == str, 'FISPACT输入文件路径%s不合法' % path
    if func:
        assert type(call) == bool, '内部异常，请重新下载软件包'
        assert type(clear) == bool, '内部异常，请重新下载软件包'
    if call:
        func(clear)

    _mkdir(path + '/' + cell)
    mode = re.compile('{[ \t\n]*title[ \t\n]*}')
    text = mode.sub('Irradiation of ' + cell, text)
    with open(path + '/' + cell + '/collapx.i', 'w') as f:
        f.write(text)


def _arrayx(text, cell, path, func=None, call=False, clear=False):
    # 仅内部调用
    # 生成FISPACT输入文件arrayx.i
    # text--input--初始化文件内容
    # cell--input--材料名称
    # path--input--FISPACT输入文件顶层路径
    assert type(text) == str, 'FISPACT文件内容不合法'
    assert type(cell) == str, '材料名称不合法'
    assert type(path) == str, 'FISPACT输入文件路径%s不合法' % path
    if func:
        assert type(call) == bool, '内部异常，请重新下载软件包'
        assert type(clear) == bool, '内部异常，请重新下载软件包'
    if call:
        func(clear)

    _mkdir(path + '/' + cell)
    mode = re.compile('{[ \t\n]*title[ \t\n]*}')
    text = mode.sub('Irradiation of ' + cell, text)
    with open(path + '/' + cell + '/arrayx.i', 'w') as f:
        f.write(text)


def _printlib(text, cell, path, func=None, call=False, clear=False):
    # 仅内部调用
    # 生成FISPACT输入文件printlib.i
    # text--input--初始化文件内容
    # cell--input--材料名称
    # path--input--FISPACT输入文件顶层路径
    assert type(text) == str, 'FISPACT文件内容不合法'
    assert type(cell) == str, '材料名称不合法'
    assert type(path) == str, 'FISPACT输入文件路径%s不合法' % path
    if func:
        assert type(call) == bool, '内部异常，请重新下载软件包'
        assert type(clear) == bool, '内部异常，请重新下载软件包'
    if call:
        func(clear)

    _mkdir(path + '/' + cell)
    mode = re.compile('{[ \t\n]*title[ \t\n]*}')
    text = mode.sub('Irradiation of ' + cell, text)
    with open(path + '/' + cell + '/printlib.i', 'w') as f:
        f.write(text)


def _input(text, neutron, allStructure, cell, genRate, path, func=None, call=False, clear=False):
    # 仅内部调用
    # 生成FISPACT输入文件input.i
    # text--input--初始化文件内容
    # neutron--input--由JMCT输出文件读取的所有材料物质信息
    # allStructure--input--由GDML文件读取的所有材料物质信息
    # cell--input--材料名称
    # genRate--input--光子产生速度
    # path--input--FISPACT输入文件顶层路径
    assert type(neutron) == Data, '物质信息不合法'
    assert type(allStructure) == dict, '结构信息不合法'
    assert type(genRate) == float or type(genRate) == int, '光子产生速度不合法'

    assert type(text) == str, 'FISPACT文件内容不合法'
    assert type(cell) == str, '材料名称不合法'
    assert type(path) == str, 'FISPACT输入文件路径%s不合法' % path
    if func:
        assert type(call) == bool, '内部异常，请重新下载软件包'
        assert type(clear) == bool, '内部异常，请重新下载软件包'
    if call:
        func(clear)
    _mkdir(path + '/' + cell)
    eleDensity = {}
    allDensity = 0.

    for element in allStructure[cell].matGre:
        tmp = element[1] * element[3] / Avogadro
        allDensity += tmp
        eleDensity[element[0]] = tmp
    # 计算DENSITY
    # 单位g/cm^3
    density = '%E' % allDensity
    # 写入MASS
    tmp = float(allStructure[cell].matD) * float(neutron.cellInfo[cell][1])
    # 字符串mass
    mass = '%E' % tmp
    elements = [' %s %f\n' % (ele[element[2]], 100 * eleDensity[element[0]] / allDensity) for element in
                allStructure[cell].matGre]
    tmp = ['%d\n' % len(allStructure[cell].matGre)]
    tmp.extend(elements)
    elements = tmp
    # 字符串elements
    elements = ''.join(elements)[:-1]
    # 计算中子通量
    flux = '%E' % (neutron.cellInfo[cell][0] * genRate)

    # 替换
    mode = re.compile('{[ \t\n]*title[ \t\n]*}')
    text = mode.sub('Irradiation of ' + cell, text)
    mode = re.compile('{[ \t\n]*mass[ \t\n]*}')
    text = mode.sub(mass, text)
    mode = re.compile('{[ \t\n]*density[ \t\n]*}')
    text = mode.sub(density, text)
    mode = re.compile('{[ \t\n]*flux[ \t\n]*}')
    text = mode.sub(flux, text)
    mode = re.compile('{[ \t\n]*elements[ \t\n]*}')
    text = mode.sub(elements, text)

    with open(path + '/' + cell + '/input.i', 'w') as f:
        f.write(text)


def _fluxes(cellInfo, path, cell, func=None, call=False, clear=False):
    assert type(cell) == str, '材料名称不合法%s'%cell
    assert type(path) == str, 'FISPACT输入文件路径%s不合法' % path
    if func:
        assert type(call) == bool, '内部异常，请重新下载软件包'
        assert type(clear) == bool, '内部异常，请重新下载软件包'
    if call:
        func(clear)
    _mkdir(path + '/' + cell)
    fluxes = cellInfo[2]
    fluxes.reverse()
    fluxes = map(lambda s: s + '\n', fluxes)
    with open(path + '/' + cell + '/fluxes', 'w') as f:
        f.writelines(fluxes)


def _genSource(cell, i, neutron, allDistributions, pre, split, func=None, call=False, clear=False):
    # 仅内部调用
    # 用于map操作
    if func:
        assert type(call) == bool, '内部异常，请重新下载软件包'
        assert type(clear) == bool, '内部异常，请重新下载软件包'
        if call:
            func(clear)

    tmp = []
    segments = []
    samProb = []
    distributions = allDistributions[cell][1]
    possibility = allDistributions[cell][0] * neutron.cellInfo[cell][1]
    for distribution in distributions:
        segments.append('%.2f, %.2f, ' % (distribution.leftBound, distribution.rightBound))
        samProb.append('%e, ' % distribution.perc)
    segments = ''.join(segments)
    samProb = ''.join(samProb)
    segments = segments[:-2]
    samProb = samProb[:-2]
    tmp.append('%sSource_%d {\n' % (pre, i))
    tmp.append('%s%sprobability                        = %e\n' % (pre, split, possibility))
    tmp.append('%s%scell_name                          = \"%s\"\n' % (pre, split, cell))
    tmp.append('%s%sprobability_of_energy_distribution = 1\n' % (pre, split))
    tmp.append('%s%senergy_distribution                = \"dist_%d\" \n' % (pre, split, i))
    tmp.append('%s%sdist_%d {\n' % (pre, split, i))
    tmp.append('%s%sdistribution_type  = \"piecewise_uniform_spectrum\"\n' % (pre, split * 2))
    tmp.append('%s%ssegments           = %s\n' % (pre, split * 2, segments))
    tmp.append('%s%ssample_probability = %s\n' % (pre, split * 2, samProb))
    tmp.append('%s%s}\n%s}\n' % (pre, split, pre))
    return ''.join(tmp)


def writef(path, genRate, neutron, allStructure, _inputText=defaultInput, _collapxText=defaultCollapx,
           _arrayxText=defaultArrayx, _printlibText=defaultPrintlib, funcTime=None, funcOne=None, interval=100):
    # 生成FISPACT输入文件
    # ?text--input--初始化文件内容
    # neutron--input--由JMCT输出文件读取的所有材料物质信息
    # allStructure--input--由GDML文件读取的所有材料物质信息
    # genRate--input--光子产生速度
    # path--input--FISPACT输入文件顶层路径
    keys = tuple(neutron.cellInfo.keys())
    length = len(keys)
    if funcTime:
        callTime = max(length // interval, 1)
        # 回调告知总调用次数
        funcOne(length // callTime, length)
        callList = [True if i % callTime == 0 or i == 0 else False for i in range(length)]
        clearList = [False] * length
        clearList[0] = True

        # 每次回调告知进度
        [_input(_inputText, neutron, allStructure, keys[i], genRate, path, funcTime, callList[i], clearList[i]) for i in range(length)]
        [_collapx(_collapxText, keys[i], path, funcTime, callList[i], clearList[i]) for i in range(length)]
        [_arrayx(_arrayxText, keys[i], path, funcTime, callList[i], clearList[i]) for i in range(length)]
        [_fluxes(neutron.cellInfo[keys[i]], path, keys[i], funcTime, callList[i], clearList[i]) for i in range(length)]
        if _printlibText:
            [_printlib(_printlibText, keys[i], path, funcTime, callList[i], clearList[i]) for i in range(length)]
    else:
        [_input(_inputText, neutron, allStructure, keys[i], genRate, path) for i in range(length)]
        [_collapx(_collapxText, keys[i], path) for i in range(length)]
        [_arrayx(_arrayxText, keys[i], path) for i in range(length)]
        [_fluxes(neutron.cellInfo[keys[i]], path, keys[i]) for i in range(length)]
        if _printlibText:
            [_printlib(_printlibText, keys[i], path) for i in range(length)]


def writej(path, text, neutron, allDistributions, funcTime=None, funcOne=None, interval=100):
    # 生成JMCT输入文件
    # path--input--JMCT输入文件位置
    # neutron--input--由JMCT输出文件读取的所有材料物质信息
    # allStructure--input--由GDML文件读取的所有材料物质信息
    # split--input--括号缩进
    split = ' ' * 3
    mode = re.compile('{[ \t\n]*source[ \t\n]*}')

    try:
        pos = mode.search(text).start()
    except Exception as e:
        raise e
    offset = pos - text.rfind('\n', 0, pos) - 1
    pre = offset * ' '
    numOfStus = len(neutron.cellInfo.keys())
    tmp = ['number_of_source = %d\n' % numOfStus]
    tmp.append('%sparticle_type    = 2\n' % pre)
    length = len(neutron.cellInfo)
    keys = tuple(neutron.cellInfo.keys())
    if funcTime:
        callTime = max(length // interval, 1)
        # 回调告知总调用次数
        funcOne(length // callTime, neutron.cellNum)
        funList = [funcTime] * length
        callList = [True if i % callTime == 0 or i == 0 else False for i in range(length)]
        clearList = [False] * length
        clearList[0] = True
        # 每次回调告知进度
        tmp.extend([_genSource(keys[i], i, neutron, allDistributions, pre, split, funcTime, callList[i], clearList[i]) for i in range(length)])
    else:
        tmp.extend(
            [_genSource(keys[i], i, neutron, allDistributions, pre, split) for i in range(length)])

    tmp = ''.join(tmp)
    text = mode.sub(tmp, text)

    with open(path, 'w') as f:
        f.write(text)
