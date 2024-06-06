import os
from Continuous_processing_of_csv import count_csv , print_file , make_file_name_list
from Make_Data import make_data
from joblib import Parallel, delayed

def get_parameter():
#=============================================パラメータ設定================================================

    R_RANGE         = 50 #Rの範囲の大きさ。基準点からの距離
    R_total_num     = 6   #Rの範囲の個数
    Type_num        = 0   #csvを書き出したい(注目したい)車両Typeの番号を指定。存在しないType番号は入れないこと
    #Type_num       = "ALL" #すべての車両Typeについて書き出したい場合
    ave_flag        = 0   #自車速度を平均に含めるかどうか。1なら含める。0なら含めない。
    time_step       = 5   #出力するデータの時間の間隔
    sampling_step   = 15  #サンプリング間隔。time_stepの定数倍にすること。最小1倍。

#=============================================パラメータ設定================================================
    #パラメータを他の関数へ回す
    return R_RANGE , R_total_num , Type_num , ave_flag , time_step , sampling_step



if __name__ == "__main__":

    parameter = get_parameter()
    print("=================出力モード=================")
    print("出力する車両Type: ",parameter[2])
    if parameter[3] == 1:
        print("自車込み速度平均:  True")
    else:
        print("自車込み速度平均:  False")
    print("============================================")


    #出力フォルダを作成
    path = './result'
    os.makedirs(path,exist_ok=True) #resultフォルダを作る。既にフォルダが存在していてもエラーにならない

    total_num_of_csv = count_csv()              #全処理ファイル数を取得
    print("ファイル数" , total_num_of_csv)      #全ファイル数を表示 
    print_file(total_num_of_csv)                #全ファイル名を表示

    
    file_name_list = make_file_name_list()      #ファイル名のリストを生成


    Parallel(n_jobs = 2)([delayed(make_data)(n) for n in file_name_list]) #ファイル名を一つずつ渡して実行する

    print("======FINISH======")