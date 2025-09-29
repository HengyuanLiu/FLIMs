import csv
import os

def mutants(file):
    """
    Reads the mutants.log file and returns a dictionary mapping functions to mutant IDs.
    """
    with open(file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        data = {}
        for row in csvreader:
            str1 = str(row).split(':')[0]
            str2 = str(row).split(':')[4]
            try:
                str1 = str1.split("'")[1]
            except:
                str1 = str1.split('"')[1]
            str2 = str2.split(':')[0]
            str2 = str2.replace('@', '.')
            data[str1] = str2
        return data

def read(file_path):
   
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.rstrip('\n') for line in file]
    return lines

def save(keys, output_path):
   
    directory = os.path.dirname(output_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(output_path, 'w', encoding='utf-8') as output_file:
        for key in keys:
            output_file.write(key + '\n')
def queryname(file):
    #查询id对应函数
    with open(file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        data={}
        data1=[]
        for row in csvreader:
            data1.append(row[0])
        for i in data1[1:]:  
            try:
               data[i.split(';')[2]]=i.split(';')[3].split('(')[0].split('"')[1]
            except:
                data[i.split(';')[2]]=i.split(';')[3].split('(')[0]
        return data   
def find_mutanterror(df_killmap, idx, test):
    try:
        mask = (df_killmap.iloc[:, 1] == idx) & (df_killmap.iloc[:, 0] == test)
        return df_killmap.loc[mask, df_killmap.columns[7]].values.tolist()
    except Exception as e:
        print(f"error {e}")
        return []

if __name__ == "__main__":
    buggy = {
        'Chart': 26,
        #  'Math': 107,
        #  'Closure': 134,
        #  'Lang': 66,
        #  'Mockito': 39,
        #  'Time': 27
    }
    for bug, bugnumber in buggy.items():
        for idex in range(1, bugnumber + 1):
            print(f"{bug}-{idex}b start!!!")
            try:
                file = rf'D:\Graduate\code\fault\BuggyMethod\{bug}\{bug}-{idex}.buggy.methods'
                file3 = rf"D:\code\mbfl data\{bug}\{idex}\killmaps\{bug}\{idex}\mutants.log"
                file2 = rf'D:\code\chain\{bug}\{idex}b\method-base.csv'
                query=queryname(file2)
                #print(query)
                mut = mutants(file3)
                fault = read(file)
                #print(fault)
                methods = []
                for key, value in query.items():
                    if value in fault:
                        methods.append(key)
                output_file_path = rf"D:\Graduate\code\result\bug-mutant\{bug}\{bug}-{idex}.methods.txt"
                
                save(methods, output_file_path)
                # for line in 
                # keys = []
                # for key, value in mut.items():
                #     if value in fault:
                #         keys.append(key)
                
                
                # output_file_path = rf"D:\Graduate\code\result\bug-mutant\{bug}\{bug}-{idex}.keys.txt"
                
                # save(keys, output_file_path)
                        
            except Exception as e:
                pass
