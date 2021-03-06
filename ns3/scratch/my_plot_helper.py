#!/usr/bin/env python
#coding: utf-8

#Usage
# 将文本文件绘制成图形
# ../../../ns3/scratch/my_plot_helper.py jitter.txt
# jitter.txt 的格式如下
# 时间 数值
"""
0	0.138706
1	0.008000
2	0.008000
3	0.008000
4	0.008000
5	0.008000
6	0.008000
"""

# INSTALL
# Ubuntu
#  sudo apt-get install python-matplotlib  # 安装 matplotlib
# OSX
# 进入 anaconda 环境
# pyenv shell anaconda2-2.5.0  / pyenv shell anaconda2-2.4.1
#

# 单绘图
# python scratch/my_plot_helper.py seventh-cwnd-count.dat
#
# 独立 多绘图模式 (适合一种模型下的不同类型图表)
# python scratch/my_plot_helper.py TcpVariantsComparison-TcpNewReno-*.txt
#
# merge 多绘图模式 (适合不同模型下的同一类型图表对比)
# python scratch/my_plot_helper.py --merge TcpVariantsComparison-*-cwnd.txt

import sys
import matplotlib.pyplot as plt
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='对 ns3 tracing 作绘图处理')

# api add_argument() https://docs.python.org/2/library/argparse.html#module-argparse
parser.add_argument('-m', '--merge', action='store_true', help='是否叠加绘图结果')
parser.add_argument('-d', '--display', action='store_true', help='是否直接绘图结果')
parser.add_argument('-f', '--field',
                    help="选择 field 进行绘图, 默认是前两栏 1:2",
                    dest="field",
                    default="1:2")
parser.add_argument('-l', '--lable',
                    help="标签名称",
                    dest="label",
                    default=None)
parser.add_argument('filenames', metavar='filename', nargs='+',
                    help='要处理的文件名')

# parser.parse_args(args=['--merge', 'a.txt', 'b.txt'])

args = parser.parse_args()

# if len(sys.argv) < 2:
#     print "Usage: %s <filename1.dat> <filename2.dat>" % sys.argv[0]
#     print "Example: %s ../seventh-cwnd-count.dat" % sys.argv[0]
#     sys.exit()

print "== ARGUMENT == "
if args.merge:
    print "== 使用 merge 绘图模式"
else:
    print "== 使用 独立 绘图模式"
if args.display:
    print "== 显示绘图 "
else:
    print "== 不显示绘图 "

field_list=args.field.split(":")
field1, field2 = int(field_list[0]), int(field_list[1])
print "== 选择 field %d:%d 进行绘图 " % (field1, field2)

plt_handles = []
for this_file in args.filenames: # support multiple file
    print this_file
    if not args.merge:
        plt.clf() # 清除上一次绘图
    arr = np.genfromtxt(this_file)
    print ("读入了数据文件 %s" % this_file)

    # 设定输出文件名
    if not args.label or args.merge:
        png_filename = "%s.%s" % (this_file, 'png')
        args.label = this_file
    else:
        png_filename = "%s.%s" % (args.label, 'png')
    plt.title(args.label)
    this_handle, = plt.plot(arr[:,field1 - 1], arr[:,field2 - 1], label=args.label)
    if not args.merge:
        plt_handles = [this_handle]
    else:
        plt_handles += [this_handle]
    
    #print sys.version_info
    # 兼容 unbuntu14.04 自带的 python 2.7.6 所对应的 matplotlib (1.3.1)
    if sys.version_info < (2,7,7): # 这里的指定版本为 unbuntu14.04 自带的 2.7.6，注意 <= 中的=不起作用， 
        plt.legend(plt_handles)
    else:
        plt.legend(handles=plt_handles)

    plt.grid(True)

    plt.savefig(png_filename) # 保存文件
    print png_filename
    print ("生成了图形文件 %s" % png_filename)
    if args.display: # and len(sys.argv) == 2: # 如果仅有一个图表则显示, 否则只是批量生产png文件
        plt.show()

if args.merge: # merge模式下显示最后的图表
     plt.show()
