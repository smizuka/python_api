# -*- coding: utf-8 -*-
import numpy as np
import numpy.linalg as lin
import cvxpy as cvx

#効率的フロンティア曲線を生成する関数
def efficient_data(Mu,Stdev,CorrMatrix):
    Sigma = np.diag(Stdev).dot(CorrMatrix).dot(np.diag(Stdev))
    iota = np.ones(Mu.shape)
    inv_Sigma = lin.inv(Sigma)
    A = Mu.dot(inv_Sigma).dot(iota)
    B = Mu.dot(inv_Sigma).dot(Mu)
    C = iota.dot(inv_Sigma).dot(iota)
    D = B * C - A ** 2

    # %% 空売り制約の下での分散最小化問題の設定
    #このweightとは最適化問題の中で制御するべき変数
    Weight = cvx.Variable(Mu.shape[0])

    #最適化問題の中で目標収益率として機能するパラメーター
    #オプション引数としてsign="positive"としているのはリターンは基本的に正の数であるから。
    Target_Return = cvx.Parameter()

    #cvx.quad_formは２次形式を計算するための関数
    #w'Σwを目的関数とする
    Risk_Variance = cvx.quad_form(Weight, Sigma)

    #MinimizeオプションでRisk_Varianceを目的関数に設定する
    Opt_Portfolio = cvx.Problem(cvx.Minimize(Risk_Variance),
                                [Weight.T*Mu == Target_Return,
    #                              cvx.sum_entries(Weight) == 1.0,
                                 cvx.sum(Weight) == 1.0,
                                 Weight >= 0.0])

    # %% 空売り制約の下での最小分散フロンティアの計算
    V_Target = np.linspace(Mu.min(), Mu.max(), num=5)
    V_Risk = np.zeros(V_Target.shape)
    V_Weight = np.zeros((V_Target.shape[0], Mu.shape[0]))
    for idx, Target_Return.value in enumerate(V_Target):
        Opt_Portfolio.solve()
        V_Weight[idx, :] = Weight.value.T
        V_Risk[idx] = np.sqrt(Risk_Variance.value)

    #stockpriceではV_Weight.T.tolist()（転置）を使う
    #stockprice2ではV_Weight.tolist()を使う

    result=[
        V_Target.tolist(),
        V_Risk.tolist(),
        V_Weight.T.tolist(),
        V_Weight.tolist()
    ]
    return result

#幾何ブラウン運動
def gBM(S,sigma,mu,t,z):
    gBM=S*np.exp((mu-sigma**2/2)*t+sigma*np.sqrt(t)*z)
    return gBM

#標準モンテカルロ法
def monte_sim(start,day):
    array=np.zeros(day)#発生させたい日数分の株価分のリスト
    array[0]=start#初期株価
    # モンテカルロ法
    for n in range(1,day):
        #分散の平均を１、分散の標準偏差を１とする
        var=abs(np.random.normal(1,1))
        #平均の平均は０、平均の標準偏差を１とする
        mu=np.random.normal(0,1)
        array[n]= array[n-1]+(array[n-1]*np.random.normal(mu, var)/100)
    return array
