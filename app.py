from flask import Flask, jsonify, abort, make_response, request
import numpy as np
import pandas as pd
import json

#basic認証をするためのライブラリー
# from flask_httpauth import HTTPBasicAuth

# 独自定義関数
from model import efficient_data, gBM, monte_sim
from datasets import create_params

#グラフを描写するチャート
# import matplotlib.pyplot as plt
# import seaborn as sns

# # 画像ファイルをbase64にエンコードする
# import base64

app = Flask(__name__)

# ----------------------------------------------
#認証するためのコード
# ----------------------------------------------
# auth = HTTPBasicAuth()

# users = {
#     "john": "hello",
#     "susan": "bye"
# }

# @auth.get_password
# def get_pw(username):
#     if username in users:
#         return users.get(username)
#     return None

# ----------------------------------------------
#各種統計量の算出
# ----------------------------------------------
@app.route('/statistic',methods=["POST"])
def statistic():

  #リストを受け取るフォーム形式
  # request.formは文字列を受け取るため、リストとしては認識されず、最初の１文字だけ
  #testとして送信されてくるのはリスト形式のadjust
  data=request.form.getlist('test')

  #文字列からfloatに変換する
  lists=[float(i) for i in data]

  data_max=np.max(lists)
  data_min=np.min(lists)
  data_mean=np.mean(lists)
  data_median=np.median(lists)
  data_std=np.std(lists)

  result={
    "max":np.max(lists),
    "min":np.min(lists),
    "mean":np.mean(lists),
    "median":np.median(lists),
    "std":np.std(lists)
  }

  return make_response(jsonify(result))


#matplotlibやseabornはherokuにアップする際に
#エラーが出るのでコメントアウトした
# ----------------------------------------------
#各種統計量の算出
# ----------------------------------------------
# @app.route('/ts_analysis',methods=["POST"])
# def ts_analysis():

#   #jsonファイルで転送されてきたものが辞書型になっている
#   data = request.get_json()

#   # コード一覧リスト取得。コードをキーとしてバリューが入っている
#   names=list(data["data"].keys())
#   prices=list(data["data"].values())
#   #priceに入っている文字は文字列なので変換する必要がある
#   prices2=[]

#   for price in prices:
#       lists=[float(i) for i in price]
#       prices2.append(lists)

#   df=pd.DataFrame()

#   for name, price in zip(names, prices):
#       df[name]=price

#   #変化率を算出させてくれる関数、100をかけて%表示にする
#   result1=df.pct_change(periods=1)*100
#   #1日目のデータがNONであるとエラーになるので削除、その後roundで小数点２桁で丸め
#   result2=round(result1.iloc[1:,:],2)

#   #チャートを描写するときは新しくfigureを定義する（そうしないと前のデータが残る）
#   plt.figure()
#   #文字化けするのでここでフォントを指定する
#   # sns.set(font='AppleGothic')
#   #カラムに銘柄名、データは収益率を入れたpandasデータフレーム
#   sns.pairplot(result2)
#   plt.savefig('static/images/sample.png')

#   #Base64でエンコードする画像
#   target_file="static/images/sample.png"

#   #読み出し専用なら'r',書き込み専用なら 'w'
#   #mode に 'b' を追加するとファイルをバイナリモードで開く
#   with open(target_file, 'rb') as f:
#       data = f.read()
#   #Base64で画像をエンコード
#   # 参考サイト  https://financial-it-engineer.hatenablog.com/entry/20180728/1532757959
#   encode=base64.b64encode(data).decode("utf-8")
#   #辞書型形式にパッケージする
#   datasets={"data":encode}

#   return make_response(jsonify(datasets))

# ----------------------------------------------
#シミュレーション
# ----------------------------------------------
@app.route('/simulation',methods=["POST"])
def simulation():

  #jsonファイルで転送されてきたものが辞書型になっている
  #jsonファイルで転送されてきたものは数字であっても
  #基本文字列なので整数、浮動点少数に変換する
  #{codes:[],sigma:[],adjust:[],day:[]}
  data = request.get_json()
  #for文を回す回数
  num=len(data["sigma"])
  # 結果を格納する空の辞書型
  result={}

  #モンテカルロ法によるシミュレーション
  for i in range(0,num):
      code=data["codes"][i]#キーとなるコード
      day=int(data["day"][i]) #予測したい日数->文字列なので整数変換する
      start=int(data["adjust"][i])
      process=monte_sim(start,day)
      # 各銘柄をキーとしてシミュレーション結果のリストを入れる
      result[code]=process.tolist()

  # # 幾何ブラウンによるシミュレーション
  # for i in range(0,num):
  #     code=data["codes"][i]#キーとなるコード
  #     day=int(data["day"][i]) #予測したい日数->文字列なので整数変換する
  #     sigma=round(float(data["sigma"][i]),2) #収益率の標準偏差,文字列なのでfloat,round(,2)
  #     delta_t=0.01 #時間間隔
  #     #発生させたい日数分の株価分の０ベクトル
  #     process=np.zeros(day)
  #     process[0]=data["adjust"][i]#初期値

  #     #平均と分散が標準正規分布から生成されると過程した分布
  #     for n in range(1,len(process)):
  #         #ボラティリティのばらつきは大きくないと仮定する
  #         var=np.random.normal(0,0.3)
  #         # 期待収益率は基本的に0と考える。ボラティリティのみを参考にする
  #         mean=np.random.normal(0,sigma)
  #         process[n]=gBM(process[n-1],var,mean,delta_t,np.random.normal(0, 1))
  #     # 各銘柄をキーとしてシミュレーション結果のリストを入れる
  #     result[code]=process.tolist()

  return make_response(jsonify(result))

# ----------------------------------------------
#最適化計算
# ----------------------------------------------
@app.route('/optimisation',methods=["POST"])
def optimisation():

  #jsonファイルで転送されてきたものが辞書型になっている
  data = request.get_json()

  # コード一覧リスト取得。コードをキーとしてバリューが入っている
  codes=list(data.keys())

  # 日付を含まない時系列データ
  #result内は[mean,std,cov]のリスト
  result1=create_params(data)

  # efficient_data(Mu,Stdev,CorrMatrix)
  # result2=[V_Target,V_Risk,V_Weight]
  result2=efficient_data(result1[0],result1[1],result1[2])

  result3={
    "code":codes,
    "mean":result1[0].tolist(),
    "std":result1[1].tolist(),
    "target":result2[0],
    "risk":result2[1],
    "weight":result2[2],
    #シミュレーション計算で使用する
    "weight2":result2[3]
  }

  return make_response(jsonify(result3))

# エラーハンドリング
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0')

# @app.route('/getname/<string:name>', methods=['POST'])
# def greet(name):
#     result = { "greeting": 'hello {}'.format(name) }
#     return make_response(jsonify(result))

# @app.route('/getname/<string:name>', methods=['GET'])
# @app.route('/getname', methods=['GET','POST'])
# # @app.route('/getname', methods=['GET'])
# def greet():

#     # name= request.form['namae']
#     name="satoru"

#     # result = { "greeting": 'hello{}'.format(name) }
#     result = { "greeting": 'hello{}'.format(name)}
#     return make_response(jsonify(result))
