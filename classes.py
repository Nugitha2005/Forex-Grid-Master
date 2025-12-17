
import MetaTrader5 as mt5
import pandas as pd
import time


class GridBot:
    # UPDATED: Added 'delay' to the list of arguments
    def __init__(self, symbol, volume, tp, no_of_levels, no_of_cycles, delay):
        self.symbol = symbol
        self.volume = volume
        self.tp = tp
        self.no_of_levels = no_of_levels
        self.no_of_cycles = no_of_cycles
        self.delay = delay  # <--- STORE THE DELAY IN THE BACKPACK

    # --- ORDER PLACEMENT FUNCTIONS ---
    def buy_limit(self, price):
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.symbol,
            "volume": self.volume,
            "type": mt5.ORDER_TYPE_BUY_LIMIT,
            "price": price,
            "magic": 100,
            "deviation": 20,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        result = mt5.order_send(request)
        print(result)  # Print full result for debugging

    def sell_limit(self, price):
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.symbol,
            "volume": self.volume,
            "type": mt5.ORDER_TYPE_SELL_LIMIT,
            "price": price,
            "magic": 100,
            "deviation": 20,
            "comment": "python script open",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        result = mt5.order_send(request)
        print(result)  # Print full result for debugging

    # --- CALCULATION FUNCTIONS ---
    def cal_buy_profit(self):
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None: return 0
        df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
        df = df[df.type == 0]
        profit = float(df.profit.sum()) if not df.empty else 0
        return profit

    def cal_sell_profit(self):
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None: return 0
        df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
        df = df[df.type == 1]
        profit = float(df.profit.sum()) if not df.empty else 0
        return profit

    def cal_buy_margin(self):
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None: return 0
        df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
        df = df[df.type == 0]

        sum_margin = 0
        for i in df.index:
            vol = df.volume[i]
            open_price = df.price_open[i]
            margin = mt5.order_calc_margin(mt5.ORDER_TYPE_BUY, self.symbol, vol, open_price)
            sum_margin += margin
        return sum_margin

    def cal_sell_margin(self):
        positions = mt5.positions_get(symbol=self.symbol)
        if positions is None: return 0
        df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
        df = df[df.type == 1]

        sum_margin = 0
        for i in df.index:
            vol = df.volume[i]
            open_price = df.price_open[i]
            margin = mt5.order_calc_margin(mt5.ORDER_TYPE_SELL, self.symbol, vol, open_price)
            sum_margin += margin
        return sum_margin

    def cal_buy_pct_profit(self):
        profit = self.cal_buy_profit()
        margin = self.cal_buy_margin()
        if margin == 0: return 0
        pct = (profit / margin) * 100
        return pct

    def cal_sell_pct_profit(self):
        profit = self.cal_sell_profit()
        margin = self.cal_sell_margin()
        if margin == 0: return 0
        pct = (profit / margin) * 100
        return pct

    # --- CLOSE & DELETE FUNCTIONS ---
    def close_position(self, position):
        tick = mt5.symbol_info_tick(position.symbol)
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": position.ticket,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_BUY if position.type == 1 else mt5.ORDER_TYPE_SELL,
            "price": tick.ask if position.type == 1 else tick.bid,
            "deviation": 20,
            "magic": 100,
            "comment": "python script close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }
        return mt5.order_send(request)

    def close_all_positions(self):
        positions = mt5.positions_get(symbol=self.symbol)
        if positions:
            for position in positions:
                self.close_position(position)

    def delete_pending(self, ticket):
        close_request = {
            "action": mt5.TRADE_ACTION_REMOVE,
            "order": ticket,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(close_request)
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Error deleting: {result._asdict()}")
        else:
            print('Delete complete...')

    def close_all_pending(self):
        orders = mt5.orders_get(symbol=self.symbol)
        if orders is None or len(orders) == 0:
            return

        df = pd.DataFrame(list(orders), columns=orders[0]._asdict().keys())
        for ticket in df.ticket:
            self.delete_pending(ticket)

    # --- GRID LOGIC ---
    def draw_grid(self):
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None: return
        curr = (tick.bid + tick.ask) / 2

        pct_change_sell = 1
        for i in range(self.no_of_levels):
            price = ((pct_change_sell * curr) / 10000) + curr
            self.sell_limit(price)
            pct_change_sell += 1

        pct_change_buy = -1
        for i in range(self.no_of_levels):
            price = ((pct_change_buy * curr) / 10000) + curr
            self.buy_limit(price)
            pct_change_buy -= 1

    # --- MAIN LOOP (Updated with Delay) ---
    def run(self):
        for i in range(self.no_of_cycles):
            print(f"Starting cycle {i + 1}")
            self.draw_grid()

            # 1. WAIT for orders to be placed/recognized
            time.sleep(2)

            # 2. Logic to wait until trades are active (Optional safety)
            # This ensures we don't accidentally close if MT5 is slow to report positions
            retries = 0
            while True:
                positions = mt5.positions_get(symbol=self.symbol)
                if positions is not None and len(positions) > 0:
                    break  # We have trades, proceed to monitoring

                # If we have no positions, check pending orders
                orders = mt5.orders_get(symbol=self.symbol)
                if orders is not None and len(orders) > 0:
                    # Pending orders exist, but no active trades yet.
                    # We stay in this loop monitoring for profit or waiting for fills.
                    pass
                else:
                    # No positions AND no orders? Something is wrong or grid is empty.
                    # Break to avoid infinite loop
                    if retries > 10: break
                    retries += 1

                time.sleep(1)

            # 3. MONITORING LOOP
            while True:
                try:
                    positions = mt5.positions_get(symbol=self.symbol)

                    # If we have active positions, check profit
                    if positions is not None and len(positions) > 0:
                        margin_b = self.cal_buy_margin()
                        margin_s = self.cal_sell_margin()

                        if margin_b > 0:
                            pct = self.cal_buy_pct_profit()
                            if pct >= self.tp:
                                print(f"Buy Target Reached: {pct}%")
                                self.close_all_positions()

                        if margin_s > 0:
                            pct = self.cal_sell_pct_profit()
                            if pct >= self.tp:
                                print(f"Sell Target Reached: {pct}%")
                                self.close_all_positions()

                    # Check if cycle is complete (No positions AND No pending orders)
                    positions = mt5.positions_get(symbol=self.symbol)
                    orders = mt5.orders_get(symbol=self.symbol)

                    # If empty positions, we assume cycle is done or hit TP
                    if (positions is None or len(positions) == 0):
                        self.close_all_pending()
                        print("Cycle complete. Pending orders cleared.")
                        break

                except Exception as e:
                    print(f"An error occurred: {e}")

                time.sleep(1)

            # 4. DELAY BEFORE NEXT CYCLE
            print(f"Cycle finished. Waiting {self.delay} seconds...")
            time.sleep(self.delay)