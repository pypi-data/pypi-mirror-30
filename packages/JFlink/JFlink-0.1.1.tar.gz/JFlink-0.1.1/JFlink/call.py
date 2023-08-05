# -*- coding: utf-8 -*-
import shutil
from pathlib import Path
from subprocess import Popen, PIPE
from time import sleep
from .model import defaultFILES


def copy(src: Path, dst: Path):
    shutil.copy(src, dst)


class CallJm:
    def jmct(self, jinput, gpath='', info=print):
        _input = Path(jinput).resolve()
        # if gpath == '':
        #     _gpath = _input.parent
        # else:
        #     _gpath = gpath
        _gpath = _input.parent

        def _run():
            _p = Popen(['jmct', str(_input)], cwd=str(_gpath), stdout=PIPE)
            self.pid = _p.pid
            while True:
                line = _p.stdout.readline()
                if line:
                    info(line.strip().decode('utf-8'), 3)
                    continue
                sleep(0.01)
                if _p.poll() is None:
                    continue
                self.pid = 0
                return _p.returncode

        def _check():
            _q = Popen('which jmct', shell=True)
            _q.wait()
            return _q.returncode

        if _check() == 0:
            _run()
        else:
            info('jmct环境变量未设置', 3)


class CallFis:
    def __init__(self):
        self.env = ['', '']
        self.group = ['', '', '']
        self.workalone = True

    def fisp(self, _indir, _outdir=None, info=print):
        def _copy(_src: Path, _dst: Path):
            if indir != outdir:
                copy(_src, _dst)

        def _run(msg):
            if self.workalone or not self.isInterruptionRequested():
                info(msg, 3)
                _p = Popen(str(fisppath), cwd=str(outdir), stdout=PIPE)
                self.pid = _p.pid
                while True:
                    line = _p.stdout.readline()
                    if line:
                        info(line.strip().decode('utf-8'), 3)
                        continue
                    sleep(0.01)
                    if _p.poll() is None:
                        continue
                    self.pid = 0
                    return _p.returncode
            else:
                return -1

        # 传入参数处理
        fisppath = Path(self.env[0].strip()).resolve()
        if not fisppath.is_file():
            info('file not found: %s' % fisppath, 3)
            return
        eaf = Path(self.env[1].strip()).resolve()
        indir = Path(_indir).resolve()

        # 可选功能：指定输出目录
        if _outdir is None:
            outdir = indir  # 默认为输入目录
        else:
            outdir = Path(_outdir).resolve()
            if not outdir.exists():
                outdir.mkdir()

        # 生成FILES文件
        files = defaultFILES
        files = files.replace(r'<case>', str(indir))
        files = files.replace(r'<eaf>', str(eaf))
        files = files.replace(r'<0>', self.group[0])
        files = files.replace(r'<1>', self.group[1])
        files = files.replace(r'<2>', self.group[2])
        # self.group[0]: 'n','p','d'
        # self.group[1]: '69', '100', '172', '175', '211', '315', '351'
        # self.group[2]: 'flt', 'fis', 'fus'
        with (outdir / 'FILES').open('w') as f:
            f.write(files)

        # 验证eaf地址
        eaf_gxs = r'eaf_%s_gxs_%s_%s_20070' % (self.group[0], self.group[1], self.group[2])
        if not Path(eaf / eaf_gxs).is_file():
            info(r'Cannot find: %s' % (eaf / eaf_gxs), 3)
            return
        # 创建空文件
        if (indir / 'collapx').is_file():
            _copy(indir / 'collapx', outdir / 'collapx')
        else:
            (outdir / 'collapx').touch()
        if (indir / 'arrayx').is_file():
            _copy(indir / 'arrayx', outdir / 'arrayx')
        else:
            (outdir / 'arrayx').touch()
        # 预执行程序
        if (indir / 'summaryx').is_file():
            _copy(indir / 'summaryx', outdir / 'summaryx')
        if (indir / 'halfunc').is_file():
            _copy(indir / 'halfunc', outdir / 'halfunc')
        _copy(indir / 'fluxes', outdir / 'fluxes')

        if not (indir / 'collapx.i').is_file():
            info('无效目录: %s' % indir, 3)
            return
        copy(indir / 'collapx.i', outdir / 'input')
        if _run('正在处理 collapx.i ...') != 0:
            # info('失败！')
            self.clean(outdir)
            return
        copy(indir / 'arrayx.i', outdir / 'input')
        if _run('正在处理 arrayx.i ...') != 0:
            # info('失败！')
            self.clean(outdir)
            return

        # 遍历.i文件，执行程序
        _list = list(indir.iterdir())
        for i in range(0, len(_list)):
            _input = _list[i]
            if _input.suffix == '.i' and not (_input.name == 'collapx.i' or _input.name == 'arrayx.i'):
                name = _input.stem
                copy(indir / _input, outdir / 'input')
                if _run('正在处理 ' + str(_input) + ' ...') != 0:
                    # info('失败！')
                    self.clean(outdir)
                    return
                copy(outdir / 'output', outdir.joinpath(name + '.o'))
                info('执行成功，输出：' + str(outdir.joinpath(name + '.o')), 3)
        self.clean(outdir)

    def clean(self, path):
        for file in ['input', 'output', 'FILES']:
            if (path / file).is_file():
                (path / file).unlink()
