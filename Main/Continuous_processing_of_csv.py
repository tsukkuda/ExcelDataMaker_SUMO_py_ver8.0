import os
import csv
import shutil

def print_file(total_num_of_csv):
    #ディレクトリのパスを指定
    dir1  = '.\元データ'
 
    csv_file=os.listdir(dir1)#元データフォルダ内のcsvファイルをすべて読み込み、配列に名前を格納
    
    print("------------------全処理ファイル------------------")
    for i in range(total_num_of_csv):
        print(csv_file[i])
    print("--------------------------------------------------")
    print()
    print()
    print()


def count_csv():

    #ディレクトリのパスを指定
    dir  = '.\元データ'
 
    #ファイル数を出力
    count_file = 0
 
    #ディレクトリの中身分ループ
    for file_name in os.listdir(dir):
 
      #ファイルもしくはディレクトリのパスを取得
      file_path = os.path.join(dir,file_name)
 
      #ファイルであるか判定
      if os.path.isfile(file_path):
        count_file +=1

    return count_file

def make_file_name_list():
    '''
    全てのファイルパスを一つのリストにまとめる
    '''
    #ディレクトリのパスを指定
    dir1  = '.\元データ'
 
    csv_file=os.listdir(dir1)#元データフォルダ内のcsvファイルをすべて読み込み、配列に名前を格納

    return csv_file     #csvのファイル名リストを返す