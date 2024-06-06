#コメントアウトしたい箇所のソースを選択状態にして、[Ctrl]+[k] →[c]を押します
#コメント解除したい箇所のソースを選択状態にして、[Ctrl]+[k] →[u]を押します

#==========================Python 3.9で動作確認済み=============================================
#==========================R6個の場合、車両1台あたり平均2秒でcsvに書き出せる=============================================

from datetime import timedelta


def make_data(csv_name):

    import csv
    import os
    import collections
    from decimal import Decimal
    import datetime
    from Main import get_parameter
    from tqdm import tqdm
    import numpy as np
    import random


    parameter = get_parameter() #main関数からパラメータを取得

    R_RANGE         = parameter[0]  #Rの範囲の大きさ。基準点からの距離の最小単位
    R_total_num     = parameter[1]  #Rの範囲の種類の個数
    Type_num        = parameter[2]  #csvを書き出したい(注目したい)車両Typeの番号を指定。存在しないType番号は入れないこと
    #Type_num        = parameter[2]  #すべての車両Typeについて書き出したい場合
    ave_flag        = parameter[3]  #自車速度を平均に含めるかどうか。1なら含める。0なら含めない。
    time_step       = parameter[4]  #出力するデータの時間の間隔
    sampling_step   = parameter[5]  #サンプリング間隔



    #R内の平均速度計算関数calculate_ave_speedR
    #引数は（ある車両IDの車のデータについて、何行目を見ているかのk,生データを時間ごとにまとめた配列timeData,生データの1行目の最初の秒数を取得するためだけの生データ配列data,データ生成中の車両IDのcarID,生成いしたいRの範囲の通し番号R_num）
    #@functools.lru_cache
    def calculate_ave_speedR (R_RANGE,ave_flag,k,data,timeData,carData,carID,R_num,Type_num):
        #R1の基準点はその時の[速度(秒速)×10s]先の位置。そこから前後に100m(任意)がR1の範囲
        ave_speed   = 0
        R_range     = R_RANGE                       #Rの範囲を指定。ページ最上部で設定可能
        R_point     = Decimal(str(float(carData[carID][k][2]))) + Decimal(str(float(carData[carID][k][3]))) * 15     #Rの基準点を計算
        R_start     = R_point-(R_range*R_num)               #Rの範囲の始まり
        R_goal  = R_point + (R_range*R_num)               #Rの範囲の終わり
        if R_start < 0:         #R_startが0より小さければ0に変更。ex.)R_s = -0.7,R_g = 199.7をR_s = 0.0,R_g = 200.0にする。
            R_start = 0
            R_goal  = 2*R_RANGE*R_num
        #生データの中から前方位置がRの範囲内にある車両を探し、その速度を加算した後平均を導出
        speed_sum = 0 #速度の合計用の変数
        counter   = 0   #何個足したか数える

        if Type_num=="ALL": #車両タイプ　関係なく全部書き出す場合
            for i in range(len(timeData[int(float(carData[carID][k][0])) - int(float(data[1][0]))])):  #その瞬間のデータには何両が走っていたか
                if int(timeData[int(float(carData[carID][k][0])) - int(float(data[1][0]))][i][17]) == int(carData[carID][k][17]) and R_start <= Decimal(str(timeData[int(float(carData[carID][k][0])) - int(float(data[1][0]))][i][2])) and Decimal(str(timeData[int(float(carData[carID][k][0])) - int(float(data[1][0]))][i][2])) <= R_goal:  #車両がRの範囲内にあるか判別
                    if ave_flag == 0 and int(timeData[int(float(carData[carID][k][0])) - int(float(data[1][0]))][i][1]) == carID:    #もし平均フラグが0なら自車速度の加算をスルー
                        continue
                    speed_sum = speed_sum + Decimal(str(timeData[int(float(carData[carID][k][0])) - int(float(data[1][0]))][i][6]))       #速度を加算
                    counter   = counter + 1                         #counter加算。何個足したか数える。
            if counter == 0:
                #ave_speed = carData[carID][k][6] #Rの範囲内に車両がいなかったら自車速度を代入
                ave_speed = None #Rの範囲内に車両が居なかったらNoneを代入（データ欠損扱い）
            else:
                ave_speed = speed_sum / counter 
        
        else:   #車両タイプを抽出して計算する場合
            for i in range(len(timeData[int(float(carData[carID][k][0])) - int(float(data[1][0]))])):  #その瞬間のデータには何両が走っていたか
                if int(0) == Type_num and R_start <= Decimal(str(timeData[int(float(carData[carID][k][0])) - int(float(data[1][0]))][i][2])) and Decimal(str(timeData[int(float(carData[carID][k][0])) - int(float(data[1][0]))][i][2])) <= R_goal:  #車両がRの範囲内にあるか判別
                    if ave_flag == 0 and timeData[int(float(carData[carID][k][0])) - int(float(data[1][0]))][i][1] == carID:    #もし平均フラグが0なら自車速度の加算をスルー
                        continue
                    speed_sum = speed_sum + Decimal(str(timeData[int(float(carData[carID][k][0])) - int(float(data[1][0]))][i][3]))       #速度を加算
                    counter   = counter + 1                         #counter加算。何個足したか数える。
            if counter == 0:
                #ave_speed = carData[carID][k][6] #Rの範囲内に車両がいなかったら自車速度を代入
                ave_speed = None #Rの範囲内に車両が居なかったらNoneを代入（データ欠損扱い）
            else:
                ave_speed = speed_sum / counter         #Rの範囲内の車両の平均速度を計算

        return ave_speed




    

    #現在時刻を記録
    dt_now = datetime.datetime.now()
    now_date = str(dt_now.year).zfill(4) + "'" + str(dt_now.month).zfill(2) + "'" + str(dt_now.day).zfill(2) + "_" + str(dt_now.hour).zfill(2) + "'" + str(dt_now.minute).zfill(2) + "'" + str(dt_now.second).zfill(2) + "'" + str(dt_now.microsecond).zfill(6)
    print("処理開始日時：　" , now_date)
    print(csv_name)
    print("====================データ加工処理開始====================")
    print("データ加工中...しばらくお待ちください")
    print()
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #========ここからcsvのデータ作成================================================

    #カレントディレクトリは省略可能だが明示したい場合は「.」で表し、一階層上位のディレクトリは「..」で表す。「..」を繰り返し記述することでディレクトリ階層の親子関係をたどって上へ移動することができる。
    #「../../foo/bar.txt」という記述は、現在のディレクトリの二階層上のディレクトリの中にある「foo」ディレクトリの中にある「bar.txt」というファイルを指し示している。
    csv_file=os.listdir('.\元データ')#元データフォルダ内のcsvファイルをすべて読み込み、配列に名前を格納
    #print("===============" , (x + 1) , "個目のファイル処理開始===============")
    #print(csv_file[0])
    #print()
    file_pass = ".\元データ\\" + csv_name #生データフォルダ内の一つ目のcsvファイルを読み込む

    #読み込んだcsvのデータを保持する配列（生データ）
    data = []

    with open(file_pass, 'r', encoding="utf-16", errors="", newline="") as f:
        #リスト形式
        csv_data1 = csv.reader(f, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)

        #辞書形式
        #f = csv.DictReader(csv_data1, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)

        data_append = data.append
        for i in csv_data1:  # 各行がリストになっている
            data_append(i)
            #print(i)

    #========ここまでcsvのデータ作成================================================

    #========ここから台数と車両IDの最大値を得る============================================
    carID_max = -1   #最大車両ID用変数の初期化 #NOTE この変数使ってないみたい
    car_list = [[0] *1  for i in range(0)]
    car_list_append = car_list.append
    #for i in range(1,len(data)):    #全行の中からIDの最大値を探索
    #    if int(data[i][1]) > carID_max:
    #        carID_max = int(data[i][1])
    #        car_list_append(data[i][1])
    car_list= [row[1] for row in data]
    c = set(collections.Counter(car_list))
    c.discard('vehicle_ID')
    car_num= len(c) #車の台数
    #print("全車両台数: ",car_num)
    #========ここまで台数と車両IDの最大値を得る============================================

    #===================ここから車両IDを0から順に辞書型に登録する=======================
    car_dict = {}
    for i in c:
        car_dict[i] = i
    #===================ここまで車両IDを0から順に辞書型に登録する=======================

    #車データを個別に格納する配列を作成

    #numpy配列verは扱い方がわからないから保留
    #carData = np.zeros((carID_max,1,21))
    #IDは0も存在し、0から数えているので配列数は+1必要
    #carData  = [[[0] * 21 for i in range(0)] for j in range(car_num)]#車の台数分用意
    #NOTE IDはStrなので辞書型にしなければならない
    carData={}
    timeData = [[[0] * 21 for i in range(0)] for j in range(int(float(data[-1][0]))-int(float(data[1][0]))+1)]#記録されてる時間分用意
    #=========ここから車両ID別データに分類========================================================
    for k in range(1,len(data)):#ヘッダーは除外してインクリメント
        #車両IDを見て、対応する配列に一行ずつ丸々追加
        carData.setdefault(data[k][1], []).append(data[k])
    #=========ここまで車両ID別データに分類========================================================

    #=========ここから時間別データに分類========================================================
    for i in range(1,len(data)):#ヘッダーは除外してインクリメント
        #時間を見て、対応する配列に一行ずつ丸々追加
        timeData[int(float(data[i][0]))-int(float(data[1][0]))].append(data[i])
    #=========ここまで時間別データに分類========================================================

    #=========ここから予測に使うcsv用にデータを編集・形成。自動手動関係なくとりあえず全部加工。自動か手動のラベルは残しておく===================================
    #車両IDごとに必要データをすべて先に生成する。全部そろってからIDを指定してcsvファイルに書き出していく。
    #変数を宣言
    #配列は台数分用意
    #time        =[[[0] * 1 for i in range(0)] for j in range(car_num)]
    #ID          =[[[0] * 1 for i in range(0)] for j in range(car_num)]
    #position    =[[[0] * 1 for i in range(0)] for j in range(car_num)]
    #car_speed   =[[[0] * 1 for i in range(0)] for j in range(car_num)]
    #car_Type    =[[[0] * 1 for i in range(0)] for j in range(car_num)]
    #avr_speed   =[[[[0] * 1 for i in range(0)] for j in range(R_total_num)] for j in range(car_num)]
    time        ={key: [] for key in c}
    ID          ={key: [] for key in c}
    position    ={key: [] for key in c}
    car_speed   ={key: [] for key in c}
    car_Type    ={key: [0] for key in c}
    avr_speed   ={key: [[[0] * 1 for i in range(0)] for j in range(R_total_num)] for key in c}
    #===========ここから出力したい車両の分だけ計算させるためにIDだけ先に記録======================================================================-
    #for A in c:#車両IDインクリメント
    #    carID = A
    #    for k in range(len(carData[carID])):    #その車両IDのデータの行数分インクリメント
    #        car_Type[carID].append([0])  #車両Typeの列作成。0=手動,1=閾値を下回ってから自動運転,2=予測結果が閾値を下回ってから自動運転
    #===========ここまで出力したい車両の分だけ計算させるためにIDだけ先に記録======================================================================-
    
    #===========ここから車両Type別に台数をカウント=========================================
    #変数の初期化
    car_Type0 = 0
    car_Type1 = 0
    car_Type2 = 0
    car_Type3 = 0
    car_TypeX = 0
    car_Type_max = 0
    for A in c:#車両IDインクリメント
        carID = A
        if car_Type_max < int(car_Type[carID][0]):  #carTypeの最大値を求める。最後にフォルダ作るときに使う。
            car_Type_max = int(car_Type[carID][0])    
        if int(car_Type[carID][0]) == 0:
            car_Type0 = car_Type0+1
        elif int(car_Type[carID][0]) == 1:
            car_Type1 = car_Type1+1
        elif int(car_Type[carID][0]) == 2:
            car_Type2 = car_Type2+1
        elif int(car_Type[carID][0]) == 3:
            car_Type3 = car_Type3+1
        else:
            car_TypeX = car_TypeX+1
    #念のため合計
    car_Type_sum = car_Type0 + car_Type1 + car_Type2 + car_Type3 + car_TypeX

    if Type_num == 0:
        car_TypeN = car_Type0
    elif Type_num == 1:
        car_TypeN = car_Type1
    elif Type_num == 2:
        car_TypeN = car_Type2
    elif Type_num == 3:
        car_TypeN = car_Type3
    else:
        car_TypeN = car_Type_sum
    #===========ここまで車両Type別に台数をカウント=========================================
    #print()
    #print("車両Type0: ",car_Type0,"  車両Type1: ",car_Type1,"  車両Type2: ",car_Type2,"  車両Type3: ",car_Type3,"  車両Type不明: ",car_TypeX,"    合計: ",car_Type_sum)
    #print()
    #print()


    #出力数をカウントする変数
    output_num = 0
    for carID in tqdm(c):#車両IDインクリメント
        if Type_num == "ALL":
            pass
        elif int(car_Type[carID][0]) != Type_num: #欲しい車両Typeと一致していなかったら計算をスキップ
            continue

        output_num = output_num + 1
        #print(output_num,"/",car_TypeN," ","車両ID:",carID," 生成中...")
    
        time_array = time[carID]
        ID_array = ID[carID]
        position_array = position[carID]
        car_speed_array = car_speed[carID]
    
        time_array_append = time_array.append
        ID_array_append = ID_array.append
        position_array_append = position_array.append
        car_speed_array_append = car_speed_array.append

        for k in range(len(carData[carID])):    #その車両IDのデータの行数分インクリメント
            time_array_append(carData[carID][k][0])       #時間の列作成
            ID_array_append(carData[carID][k][1])         #IDの列作成。代入の値はcarIDそのものでもいいかも（処理速度的に）。
            position_array_append(carData[carID][k][2])   #車両位置（前方位置）の列作成
            car_speed_array_append(carData[carID][k][3])  #速度の列作成 #NOTE多分ここ変更ポイント
            #car_Type[carID].append(carData[carID][k][17])  #車両Typeの列作成。0=手動,1=閾値を下回ってから自動運転,2=予測結果が閾値を下回ってから自動運転

            for n in range(R_total_num):
                ave_speedR = calculate_ave_speedR(R_RANGE,ave_flag,k,data,timeData,carData,carID,n+1,Type_num)#計算させたい車両IDとRの通し番号を引数で与える
                avr_speed[carID][n].append(ave_speedR)


            #print(float(carData[carID][k][0])) #時間の確認
            #print(float(carData[carID][k][2])) #前方位置の確認
            #print(float(carData[carID][k][6])) #速度の確認
            #print(ave_speedR)                  #計算した平均速度の確認
            #print()
    #=========ここまで予測に使うcsv用にデータを編集・形成=====================================================================================================

    #車両IDを指定してそのログを一行ごとに表示
    #[print(i) for i in carData[carID_max]]

    #print(time)
    #print(ID)
    #print(avr_speed[0][0])#avr_speed[車両ID][Rの通し番号]
    #print(avr_speed[0][1])
    #print(avr_speed[0][5])
    #車両Typeは配列番号17

    #print()
    #print("csvファイルに出力中...")
    dt_now_finish = datetime.datetime.now()
    now_time = str(dt_now_finish.second).zfill(2) + str(dt_now_finish.microsecond).zfill(6)
    Pnum = str(round(int(now_time)*(car_Type0+car_Type2)*random.randint(1, 10000),8))#絶対に重ならない数字を生みだす

    #出力フォルダを作成
    folder_name1 = csv_name[:-4]
    folder_nameR = folder_name1.replace('高速交通量', '')
    folder_nameR = folder_nameR.replace('速度閾値', '')
    folder_nameR = folder_nameR.replace('目標交通量', '')
    folder_nameR = folder_nameR.replace('制御時間', '')
    folder_nameR = folder_nameR.replace('車載率', '')
    folder_nameR = folder_nameR.replace('車線変更確率', '')
    folder_nameR = folder_nameR.replace('.csv', '')
    folder_nameR = folder_nameR + "(" + now_time + ")"
    result_path = './result/' + folder_nameR
    os.makedirs(result_path,exist_ok=True) #resultフォルダを作る。既にフォルダが存在していてもエラーにならない

    #csv書き出し用に一つの2次元配列にまとめる
    #ヘッダーの作成
    header = ["time","ID","position","car_speed"]
    for i in range(R_total_num):    #Rの範囲の個数分インクリメント
        I = (i+1)*50                     #0からカウントされているので、通し番号を表すにはプラス1する。基準点の秒数を乗算。
        header.append("avr_speed_R"+str(I))   #ヘッダー用の名前を作成

    #出力ファイルの数を数える
    csv_Number = 0

    if Type_num == 0 or Type_num == 1 or Type_num == 2:
        if Type_num == 0:
            path = './result/' + folder_nameR + '/Type0'
        elif Type_num == 1:
            path = './result/' + folder_nameR + '/Type1'
        elif Type_num == 2:
            path = './result/' + folder_nameR + '/Type2'
        else:
            path = './result/' + folder_nameR + '/TypeX'
        os.makedirs(path,exist_ok=True)

        for A in c:
            carID = A
            if int(car_Type[carID][0]) == Type_num:
                for_csv = [[0] * (4+R_total_num) for i in range((len(carData[carID]) + time_step - 1) // time_step)]
                for i in range((len(carData[carID]) + time_step - 1) // time_step):
                    for_csv[i][0] = time[carID][i * time_step]
                    for_csv[i][1] = ID[carID][i * time_step]
                    for_csv[i][2] = position[carID][i * time_step]
                    for_csv[i][3] = car_speed[carID][i * time_step]
                    for n in range(R_total_num):
                        for_csv[i][4+n] = avr_speed[carID][n][i * time_step]

                #ここでsampling_step間隔に応じて一つのtime_step間隔の配列を分割してcsvに書き出すする。
                separate_num = sampling_step // time_step
                for_csv_numpy = np.array(for_csv)#numpy型に変換
                for S in range(separate_num):
                    key = [k for k, v in car_dict.items() if v == carID][0]    #辞書型car_listから対応する車両IDの取得
                    new_file_name = "log_data(" + str(csv_Number) + str(S+1) + ").csv"
                    f = open(path + "/" + "(" + now_time + ")" + str(key).zfill(4) + new_file_name , 'w', newline='')
                    writer = csv.writer(f)
                    writer.writerow(header)
                    writer.writerows((for_csv_numpy[S::separate_num]).tolist())
                    f.close()
                del for_csv
                del for_csv_numpy
                csv_Number = csv_Number + 1

    else:
        for i in range(car_Type_max + 1):  #フォルダをすべてのcarTypeについて作成する。
            path = './result/' + folder_nameR + '/Type' + str(i)
            os.makedirs(path,exist_ok=True)

        for A in range(car_num):
            carID = A      
            for_csv = [[0] * (4+R_total_num) for i in range((len(carData[carID]) + time_step - 1) // time_step)]
            for i in range((len(carData[carID]) + time_step - 1) // time_step):
                for_csv[i][0] = time[carID][i * time_step]
                for_csv[i][1] = ID[carID][i * time_step]
                for_csv[i][2] = position[carID][i * time_step]
                for_csv[i][3] = car_speed[carID][i * time_step]
                for n in range(R_total_num):
                    for_csv[i][4+n] = avr_speed[carID][n][i * time_step]
       
            #ここでsampling_step間隔に応じて一つのtime_step間隔の配列を分割してcsvに書き出すする。
            separate_num = sampling_step // time_step
            for_csv_numpy = np.array(for_csv)#numpy型に変換
            for S in range(separate_num):
                path = './result/' + folder_nameR + '/Type' + str(car_Type[carID][0])    #車両Typeと同じフォルダのパスを指定
                key = [k for k, v in car_dict.items() if v == carID][0]    #辞書型car_listから対応する車両IDの取得
        
                new_file_name = "log_data(" +str(S+1)+ ").csv"
                f = open(path + "/" + "(" + Pnum + ")"  + str(key).zfill(4) + new_file_name , 'w', newline='')
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows((for_csv_numpy[S::separate_num]).tolist())
                f.close()
            del for_csv
            del for_csv_numpy
    
    dt_now_DONE = datetime.datetime.now()
    now_date_finish2 = str(dt_now_DONE.year).zfill(4) + "'" + str(dt_now_DONE.month).zfill(2) + "'" + str(dt_now_DONE.day).zfill(2) + "_" + str(dt_now_DONE.hour).zfill(2) + "'" + str(dt_now_DONE.minute).zfill(2) + "'" + str(dt_now_DONE.second).zfill(2) + "'" + str(dt_now_DONE.microsecond).zfill(6)
    print("処理終了日時：　" , now_date_finish2)
    print(csv_name)
    print("全車両台数: ",car_num)
    print("車両Type0: ",car_Type0,"  車両Type1: ",car_Type1,"  車両Type2: ",car_Type2,"  車両Type3: ",car_Type3,"  車両Type不明: ",car_TypeX,"    合計: ",car_Type_sum)
    print("===============データ加工処理終了===============")
    print()


