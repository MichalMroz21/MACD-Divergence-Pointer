from matplotlib import pyplot as plt
import numpy as np
import matplotlib.ticker
from dateutil import parser
import csv
import os
import pandas as pd
import math
import PySimpleGUI as sg

plt.rcParams.update({'font.size': 9}) #to make it more readable
plt.rcParams['figure.dpi'] = 150
plt.rcParams['savefig.dpi'] = 300

MAX_CSV_DATA_SIZE = 999
MAX_DISPLAY_ROWS = 10000
STARTING_MONEY = 10000

def calculate_ema(prices, n):

    ema = []

    for i in range(0, MAX_CSV_DATA_SIZE):

        numerator = prices[i]
        denominator = 1
        alpha = 2 / (n + 1)

        startingPoint = i - n #going back n days
        if startingPoint < 0: startingPoint = 0 #if went too far then go as far as possible

        for j in range(startingPoint, i): 

            numerator = numerator + (pow((1 - alpha), i - j) * prices[j]) #previous nth day prize * (1 - alpha) to power of nth previous day
            denominator = denominator + pow((1 - alpha), i - j) #(1 - alpha) to power of nth previous day

        ema.append(numerator/denominator) #add to result list

    return ema


def calculate_macd(ema12, ema26):

    macd = []
    i = 0

    for ema in ema26:

        macd.append(ema12[i] - ema) #MACD = EMA12 - EMA26
        i = i + 1

    return macd


def open_file(name):

    usecols = ["Date", "Closed prize"] #pobieram dwie kolumny tylko te

    pd.options.display.max_rows = MAX_DISPLAY_ROWS #for potential debugging

    wigData = pd.read_csv(name, usecols=usecols)

    prizes = wigData['Closed prize'].tolist() #convert prizes to a list

    if all(isinstance(elem, str) for elem in prizes): prizes = [elem.replace(',', '') for elem in prizes] #delete ',' so that convertion to float works, if all elements are strings
    prizes = list(map(float, prizes)) #convert strings to floats

    ema12 = calculate_ema(prizes, 12)
    ema26 = calculate_ema(prizes, 26)

    wigData['Date'] = wigData['Date'].values[::-1] #reverse dates
    wigData['Date'] = pd.to_datetime(wigData['Date']) #space dates on plot

    macd = calculate_macd(ema12, ema26)
    signal = calculate_ema(macd, 9)

    money = STARTING_MONEY
    startMoney = money
    shares = 0

    for i in range(1, MAX_CSV_DATA_SIZE):

        if macd[i] >= signal[i] and macd[i - 1] < signal[i - 1]:

            shares = math.floor(money/prizes[i])
            money = money - shares * prizes[i]

        if macd[i] <= signal[i] and macd[i - 1] > signal[i - 1]:

            money = money + shares * prizes[i]
            shares = 0

    finalMoney = money + shares * prizes[i]
    profit = finalMoney - startMoney

    nameWithoutCSV = name[:name.rfind(".csv")]

    print("For: " + nameWithoutCSV)
    print("Final amount of money: " + str(finalMoney))
    print("Profit: " + str(profit))

    fig, (ax1, ax2) = plt.subplots(2, 1, constrained_layout=True) #split into two subplots

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Pointer values')
    ax1.plot(wigData['Date'][:MAX_CSV_DATA_SIZE], macd, label='MACD', linewidth = 1)
    ax1.plot(wigData['Date'][:MAX_CSV_DATA_SIZE], signal, label='Signal', linewidth = 1)
    ax1.set_title("MACD Plot for " + nameWithoutCSV)
    ax1.legend()

    ax2.set_xlabel('Date')
    ax2.set_ylabel('Closing prizes')
    ax2.plot(wigData['Date'], prizes, label='Prizes', linewidth = 1)
    ax2.set_title("Closing Prizes Plot")
    ax2.legend()

    plt.savefig(nameWithoutCSV + '.png')
    plt.show()

   

sg.ChangeLookAndFeel('Dark')

font = ('Lato', 12, 'bold italic')
colors = ('Black', 'White')

sg.set_options(font=font)

layout = [
    
        [sg.Text('Select data to track')],
        [sg.Button('AAPL', button_color=colors)],
        [sg.Button('WIG20', button_color=colors)],
        [sg.Button('CAC 40', button_color=colors)],
        [sg.Button('DAX', button_color=colors)],
        [sg.Button('S&P 500', button_color=colors)],
        [sg.Button('Exit', button_color=colors)],
]

window = sg.Window('MACD_Project', layout, size=(900, 600), element_justification='c')


while True:

    event, values = window.Read()

    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    if event == "AAPL":
        open_file('AAPL Historical Data.csv')

    if event == "WIG20":
        open_file('WIG20 Historical Data.csv')

    if event == "CAC 40":
        open_file('CAC 40 Historical Data.csv')

    if event == "DAX":
        open_file('DAX Historical Data.csv')

    if event == "S&P 500":
        open_file('S&P 500 Historical Data.csv')
