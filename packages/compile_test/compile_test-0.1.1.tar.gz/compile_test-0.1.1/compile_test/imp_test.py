#coding:utf-8
import imp
from mylib import mylib

fp,pathname,des = imp.find_module("mylib")
print fp
print pathname
print des
imp.load_module("mylib",fp,pathname,des)
import dis
dis.dis(mylib)
# import opcode
# for op in range(len(opcode.opname)):
#   print('0x%.2X(%.3d): %s' % (op, op, opcode.opname[op]))

#
# 利用编译程序从源语言编写的源程序产生目标程序的过程。 2、用编译程序产生目标程序的动作。 编译就是把高级语言变成计算机可以识别的2进制语言
#
# 编译原理是计算机专业的一门重要专业课，旨在介
#
# 将字符序列转换为单词（Token）序列的过程
# 语法分析的任务是在词法分析的基础上将单词序列组合成各类语法短语
# 绍编译程序构造的一般原理和基本方法。内容包括语言和文法、词法分析、语法分析、语法制导翻译、中间代码生成、存储管理、代码优化和目标代码生成