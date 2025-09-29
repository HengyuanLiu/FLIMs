import csv
import gzip
import pandas as pd
import os
# GZIP压缩文件路径
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
csv.field_size_limit(500 * 1024 * 1024)
def mutant0(filename):
    with gzip.open(filename, 'rt', newline='',encoding='gb18030', errors='ignore') as gzipfile:
        #reader = csv.reader(gzipfile)
       # reader= itertools.islice(reader, 5)
        reader = csv.reader(x.replace('\0', '') for x in gzipfile)
        # 初始化计数器
        pass_count = 0  #第四列为PASS的数量
        fail_count = 0  #第四列为FAIL的数量
        p_test=[]       #pass 的测试用例
        f_test=[]       #fail 的测试用例
        C_test=[]
        error=[]
        # 逐行遍历CSV文件
        for row in reader:
            if len(row) >= 8:  # 确保至少有四列数据
                col2 = int(row[1])
                col4 = row[3]

                if col2 == 0: #mutant 编号
                    if col4 == 'PASS':
                        pass_count += 1
                        p_test.append(row[0])
                    elif col4 == 'FAIL':
                        fail_count += 1
                        f_test.append(row[0])
                        error.append(row[7])
                    elif col4 == 'CRASH':
                        fail_count+=1
                        C_test.append(row[0])
        return p_test, f_test,C_test, fail_count, pass_count,error

def ochiai(passed, failed, totalpassed, totalfailed):
  if totalfailed == 0 or (passed+failed == 0):
    return 0
  return failed/(totalfailed*(failed+passed))**0.5

def tarantula(passed, failed, totalpassed, totalfailed):
  if totalfailed == 0 or failed == 0:
    return 0
  if totalpassed == 0:
    assert passed == 0
    return 1 if failed > 0 else 0
  return (failed/totalfailed)/(failed/totalfailed + passed/totalpassed)

def opt2(passed, failed, totalpassed, totalfailed):
  return failed - passed/(totalpassed+1)

def dstar2(passed, failed, totalpassed, totalfailed):
  if passed + totalfailed - failed == 0:
    assert passed==0 and failed==totalfailed
    return totalfailed**2 + 1 # slightly higher than otherwise possible
  return failed**2 / (passed + totalfailed - failed)

def jaccard(passed, failed, totalpassed, totalfailed):
  if totalfailed + passed == 0:
    return failed
  return failed / (totalfailed + passed)


buggy = {
        # 'Chart': 26,
        # 'Math': 107,
        # 'Lang': 66,
        # 'Mockito': 39,
        'Closure': 134,
        #'Time': 27
    }

for bug, bugnumber in buggy.items():
  for idex in range(1, bugnumber + 1):
    print(f"{bug}-{idex}  strat----------------------------")
    try :
      gzip_file_path = rf"D:\code\mbfl data\{bug}\{idex}\killmaps\{bug}\{idex}\killmap.csv.gz"
      output_dir = rf"D:\Graduate\code\result\error1\{bug}\{idex}"
      if not os.path.exists(output_dir):
            os.makedirs(output_dir)
      file_name = f'pf_{idex}.xlsx'
      out_path = os.path.join(output_dir, file_name)
      with gzip.open(gzip_file_path, 'rt', newline='',encoding='gb18030', errors='ignore') as gzipfile:
          reader = csv.reader(x.replace('\0', '') for x in gzipfile)
          #reader = csv.reader(gzipfile)
          
          # 初始化字典来跟踪不同值的第二列的PASS和FAIL数量，以及第一列的映射
          pass_counts = {}
          fail_counts = {}
          p_test, f_test,c_test, fail_count, pass_count,error=mutant0(gzip_file_path)
          # 逐行遍历CSV文件
          for row in reader:
              if len(row) >= 8:  # 确保至少有四列数据
                  col1 = row[0]
                  col2 = int(row[1])
                  col4 = row[3]
                  col5 = row[7]
                  if col2 not in pass_counts:
                      pass_counts[col2] = 0
                  if col2 not in fail_counts:
                      fail_counts[col2] = 0

                  if col4 == 'PASS' :
                      pass_counts[col2] += 1
                      if col1 in p_test :
                          pass_counts[col2]-=1
                  if  col4 == 'CRASH' :
                    if col1 in p_test:
                        fail_counts[col2] += 1
                    if col1 in f_test:
                        pass_counts[col2] += 1
                  if col4 == 'FAIL':
                      if col1 in p_test :
                          fail_counts[col2]+=1
                      if col1 in c_test:
                          pass_counts[col2] += 1
                      if  col1 in f_test:
                        if col5 not in error:
                            pass_counts[col2] += 1
                  
                  

          df = pd.DataFrame()        
          temp_dict = {}
          temp_list=[]
          # 输出结果，包括第二列、第一列和对应的PASS和FAIL数量
          # print(fail_counts)
          # print(pass_counts)
          merged_dict = {}
          for key in set(pass_counts.keys()) | set(fail_counts.keys()):
              merged_dict[key] = {'PASS': pass_counts.get(key, 0), 'FAIL': fail_counts.get(key, 0)}

          # 输出合并后的字典
          #print(merged_dict)
    
          for key in merged_dict:
              
              temp_dict['MUT']=key
              # if key>4650:
              #   temp_dict['akf']=merged_dict[key].get('PASS')-1
              # else :
              temp_dict['akf']=merged_dict[key].get('PASS')
              temp_dict['akp']=merged_dict[key].get('FAIL')
              temp_dict['pass']=pass_count
              temp_dict['fail']=fail_count
              temp_dict['ochiai']=ochiai(temp_dict['akp'], temp_dict['akf'],temp_dict['pass'],temp_dict['fail'])
              temp_dict['tarantula']=tarantula(temp_dict['akp'], temp_dict['akf'],temp_dict['pass'],temp_dict['fail'])
              temp_dict['opt2']=opt2(temp_dict['akp'], temp_dict['akf'],temp_dict['pass'],temp_dict['fail'])
              temp_dict['dstar2']=dstar2(temp_dict['akp'], temp_dict['akf'],temp_dict['pass'],temp_dict['fail'])
              temp_dict['jaccard']=jaccard(temp_dict['akp'], temp_dict['akf'],temp_dict['pass'],temp_dict['fail'])
              if temp_dict['akf']>0:
                df = df.append(temp_dict, ignore_index=True) 
          df.to_excel(out_path, index=False)
      print(f'{bug}-{idex} complete')
    except Exception:
      print(f"{bug}-{idex} error !!!")
   
   