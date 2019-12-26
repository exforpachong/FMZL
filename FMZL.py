# -*- coding: utf-8 -*-
"""
Created on Mon Oct 28 17:54:28 2019

@author: dell
"""

import xml.sax
import pandas as pd
 
class MovieHandler( xml.sax.ContentHandler ):
   def __init__(self,content):
      self.content = content
      self.CurrentData = ""
      self.appNum = ""
      self.pubNum = ""
      self.pubDay = ""
 
   # 元素开始事件处理
   def startElement(self, tag, attributes):
      self.CurrentData = tag
      if tag == "Patent":
         num = attributes["Num"]
         self.content.append({})
         if int(num)%5000 == 0:
             print('处理到第%s个专利了！'%num)
 
   # 元素结束事件处理
   def endElement(self, tag):
      if self.CurrentData == "申请号":
         self.content[-1]['appNum'] = self.appNum
      elif self.CurrentData == "专利引证":
         self.content[-1]['pubNum'] = self.pubNum
      elif self.CurrentData == "公开公告日":
        self.content[-1]['pubDay'] = self.pubDay.replace('.','')
      self.CurrentData = ""
 
   # 内容事件处理
   def characters(self, content):
      if self.CurrentData == "申请号":
         self.appNum = content
      elif self.CurrentData == "专利引证":
         self.pubNum = content
      elif self.CurrentData == "公开公告日":
         self.pubDay = content
      
  
if __name__ == "__main__":
   
   # 创建一个 XMLReader
   parser = xml.sax.make_parser()
   # turn off namepsaces
   parser.setFeature(xml.sax.handler.feature_namespaces, 0)
 
   # 重写 ContextHandler
   contents = []
   Handler = MovieHandler(contents)
   parser.setContentHandler( Handler )
   #解析文件
   parser.parse("FMZL_23.XML")

   #保存文件结果
   appNums,pubNums,pubDays = [],[],[]
   for line in contents:
       if 'pubNum' in line:
           appNums +=[line['appNum']]
           pubNums +=[line['pubNum']]
           pubDays +=[line['pubDay']]
       else:
           appNums +=[line['appNum']]
           pubNums +=['']
           pubDays +=[line['pubDay']]
   d = pd.DataFrame(data={'申请号':appNums,'专利引证公开号':pubNums,'公开日':pubDays})
   d.to_csv('results.csv',encoding="utf_8_sig")
