# 📉 Forex Grid Master

A fully automated Forex Trading Bot built with Python and MetaTrader 5 (MT5). This bot implements a **Grid Trading Strategy**, placing buy and sell orders at fixed intervals to profit from market volatility.

## 🚀 Features
* **Automated Grid Strategy:** Automatically places pending orders above and below the current price.
* **MetaTrader 5 Integration:** Uses the official `MetaTrader5` Python library for fast execution.
* **Risk Management:** Configurable lot sizes and stop-loss settings.
* **Real-time Monitoring:** Tracks price changes and updates grid levels dynamically.

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **Platform:** MetaTrader 5 (MT5) Desktop Terminal
* **Libraries:** `MetaTrader5`, `pandas`, `time`

## ⚙️ Configuration
You can adjust the trading logic in the `classes.py` or `main.py` file:
* **Symbol:** (e.g., "EURUSD", "XAUUSD")
* **Grid Distance:** The gap (in points) between orders.
* **Lot Size:** Volume per trade (e.g., 0.01).

## 📦 How to Run
1.  **Prerequisite:** Ensure MetaTrader 5 is installed and logged into your broker account.
2.  Clone the repository:
    ```bash
    git clone [https://github.com/Nugitha2005/Forex-Grid-Master.git](https://github.com/Nugitha2005/Forex-Grid-Master.git)
    ```
3.  Install dependencies:
    ```bash
    pip install MetaTrader5 pandas
    ```
4.  Run the bot:
    ```bash
    python main.py
    ```

## ⚠️ Disclaimer
**Use at your own risk.** Forex trading involves significant risk of loss. This software is for educational purposes only. The author is not responsible for any financial losses incurred while using this bot.
