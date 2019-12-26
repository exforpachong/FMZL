# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 16:25:46 2019

@author: Xiaodong Wang
@修改日志:
2019-12-23——增加功能：
1. 对于被引证数据，增加“被引证”标签
2. 对于引证数据，增加“所有”标签
3. 对于“被引证”标签，拆分并增加“被引证时间”标签
4. 对于“审查员引证”标签，拆分并增加“引证时间”标签
5. 对于“非专利引证”标签，根据.;分开，并且增加一列，该列根据长短标记数字1，长度是可自定义的
使用方法：
命令行窗口输入：python dealXml.py -f [数据文件夹的路径] -t [需要标记的长度，默认为20]
如：python dealXml.py -f ./data -t 30
"""

import xml.etree.ElementTree as ET
import os
import pandas as pd
from xdLog import log
import pickle
from config_default import configs
import argparse

#dirPath = os.path.join('.','data')
savePath = os.path.join('.','resultData')
if not os.path.exists(savePath):
    os.mkdir(savePath)

def savelosefilename(name):
     filename = os.path.join(configs['LogDir'],'losefilenames.pkl')
     a = []
     if os.path.exists(filename):
         a = pickle.load(open(filename, 'rb'))
     a += [name]
     pickle.dump(a,open(filename, 'wb'))
def dealXml(dirPath,startStr,num_flag):
    for name in os.listdir(dirPath):
        if name.startswith(startStr) and name.endswith('.XML'):
            try:
                comName = os.path.join(dirPath,name)
                log.logger.info('开始处理文件：\n['+name+']')
                try:
                    tree = ET.parse(comName)
                    root = tree.getroot()
                except Exception as e:
                    log.logger.error('文件['+name+']解析失败，原因是：')
                    log.logger.error(e)
                    raise Exception('文件解析失败错误！[注：文件格式非标准，无法处理！]')
                #第一步扫描所有标签
                BasicHeads = ['申请号','申请日','公布号','公布日']
                BasciTags = set(BasicHeads)
                AllTags = BasciTags.copy()
                for child in root:
                    for tag in child:
                        AllTags.add(tag.tag)
                log.logger.debug('该文件所有标签为：\n'+str(AllTags))
                otherTags = AllTags-BasciTags
                allHeads = [BasicHeads]    #存放所有标题
                if startStr == '被引证数据':
                    allHeads[0] += ['被引证']  #修改需求1：对于被引证数据，增加“被引证”标签
                elif startStr == '引证数据':
                    allHeads[0] += list(otherTags)  #修改需求2：对于引证数据，增加“所有”标签
                for tag in otherTags:
                    allHeads += [['申请号',tag]]  #其他的都是[申请号+其他]的组合形式
                #第二步：得到所有数据
                allData = [[] for i in range(len(allHeads))]  #存放所有数据'申请号','申请日','公布号','公布日'
                for child in root:
                    #搜集基本数据
                    temDataForBasic = []
                    for tag in allHeads[0]:
                        if child.find(tag)!=None:
                            temDataForBasic += [child.find(tag).text]
                        else:
                            temDataForBasic += ['']
                    allData[0] += [temDataForBasic]
                    #搜集其他数据
                    for ind,head in enumerate(allHeads[1:]):
                        if child.find(head[1]) != None:
                            #print(child.find(head[1]).text)
                            if head[1] == '非专利引证':  #修改需求5：对于“非专利引证”标签，根据.;分开，并且根据长短标记
                                if len(head) == 2:
                                    allHeads[ind + 1] += ['长度标记']
                                for content in child.find(head[1]).text.split('.;'):
                                    if len(content) > num_flag:
                                        allData[ind+1] += [[child.find('申请号').text,content,1]]
                                    else:
                                        allData[ind+1] += [[child.find('申请号').text,content,None]]
                            elif head[1] == '被引证':  #修改需求3：对于“被引证”标签，拆分并增加“被引证时间”标签
                                if len(head) == 2:
                                    allHeads[ind + 1] += ['被引证时间']
                                for content in child.find(head[1]).text.split(';'):
                                    allData[ind+1] += [[child.find('申请号').text,content.split(' ')[0],content.split(' ')[1]]]
                            elif head[1] == '审查员引证':  #修改需求4：对于“审查员引证”标签，拆分并增加“引证时间”标签
                                if len(head) == 2:
                                    allHeads[ind + 1] += ['引证时间']
                                for content in child.find(head[1]).text.split(';'):
                                    allData[ind+1] += [[child.find('申请号').text,content.split(' ')[0],content.split(' ')[1]]]
                            else:
                                for content in child.find(head[1]).text.split(';'):
                                    allData[ind+1] += [[child.find('申请号').text,content]]
                #第三步：保存所有数据
                savedir = os.path.join(savePath,name)
                if not os.path.exists(savedir):
                    os.mkdir(savedir)
                original_data_path = os.path.join(savedir,name.split('.')[0]+'_原始数据.xlsx')
                log.logger.debug('开始保存'+original_data_path)
                df = pd.DataFrame(allData[0],columns=allHeads[0])
                try:
                    ## 先保存原始数据
                    df.to_excel(original_data_path,index=False)
                    ## 保存其他所有数据
                    for i,head in enumerate(allHeads[1:]):
                        path = os.path.join(savedir, name.split('.')[0] + '_' + head[1] + '.xlsx')
                        log.logger.debug('开始保存文件'+path)
                        df = pd.DataFrame(allData[i+1],columns=head)
                        df.to_excel(path,index=False)
                        log.logger.info('已保存：\n['+path+']')
                    log.logger.info('['+name+']文件处理完成！')
                except Exception as e:
                    # raise e   #测试
                    log.logger.error('文件['+name+']保存失败，原因是：')
                    log.logger.error(e)
                    raise Exception('文件保存失败错误！')
                #打印符合说明一个文件处理完成
                log.logger.info('*************************************************************')
            except Exception as e:
                # raise e  #测试
                log.logger.error('文件['+name+']处理失败，原因是：')
                log.logger.error(e) 
                savelosefilename(name)

if __name__=='__main__':
#    filename = os.path.join(configs['LogDir'],'losefilenames.pkl')
#    if os.path.exists(filename):
#        os.remove(filename)
    parser = argparse.ArgumentParser(description='Softwar to transform all the .XML files to .xlsx files, all\
    the result files will be saved in the \'resultData\' folder which is exist in the same as the python file')
    parser.add_argument('-f',help='the folder to dealing in which all the .XML file exist',type=str)
    parser.add_argument('-t',help='the threshold to distinguish the length of Non-patent citation',default=20,type=int)
    args = parser.parse_args()
    args = parser.parse_args(['-f','data'])   #调试用
    dirPath = args.f
    threshold = args.t
    if not os.path.exists(dirPath):
        print('The input file is not available, Please try again!')
        import sys
        sys.exit()
    log.logger.info('开始处理[被引证数据]')
    dealXml(dirPath,'被引证数据',threshold)
    log.logger.info('--------------------------------------------------------------------------------------')
    log.logger.info('开始处理[引证数据]')
    dealXml(dirPath,'引证数据',threshold)

