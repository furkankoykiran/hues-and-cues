"""
Advanced Trading System with Backtest and Live Mode Support

This module provides a comprehensive trading system that can operate in both
backtest mode (using historical data) and live mode (using real-time data).
"""

import datetime
import time
import logging
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
import json


class TradingMode(Enum):
    """Enum for trading mode selection"""
    BACKTEST = "backtest"
    LIVE = "live"


@dataclass
class Signal:
    """Trading signal data structure"""
    timestamp: datetime.datetime
    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    quantity: float
    price: float
    confidence: float
    reason: str


@dataclass
class Position:
    """Position data structure"""
    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime.datetime
    current_price: float = 0.0
    unrealized_pnl: float = 0.0


class DataProvider(ABC):
    """Abstract base class for data providers"""
    
    @abstractmethod
    def get_current_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        pass
    
    @abstractmethod
    def get_historical_data(self, symbol: str, start_date: datetime.datetime, 
                          end_date: datetime.datetime) -> pd.DataFrame:
        """Get historical data for backtesting"""
        pass


class HistoricalDataProvider(DataProvider):
    """Data provider for backtesting with historical data"""
    
    def __init__(self):
        self.data_cache = {}
        self.current_date = None
        
    def load_sample_data(self, symbol: str) -> pd.DataFrame:
        """Generate sample historical data for demonstration"""
        dates = pd.date_range(
            start='2023-01-01', 
            end='2023-12-31', 
            freq='D'
        )
        
        # Generate realistic price data
        np.random.seed(42)
        prices = []
        price = 100.0
        
        for _ in dates:
            change = np.random.normal(0, 0.02)  # 2% daily volatility
            price *= (1 + change)
            prices.append(price)
        
        data = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': np.random.randint(1000, 10000, len(dates))
        })
        
        return data
    
    def get_current_price(self, symbol: str) -> float:
        """Get price for current backtest date"""
        if symbol not in self.data_cache:
            self.data_cache[symbol] = self.load_sample_data(symbol)
        
        data = self.data_cache[symbol]
        if self.current_date:
            current_data = data[data['timestamp'] <= self.current_date]
            if not current_data.empty:
                return current_data.iloc[-1]['close']
        
        return data.iloc[-1]['close']
    
    def get_historical_data(self, symbol: str, start_date: datetime.datetime, 
                          end_date: datetime.datetime) -> pd.DataFrame:
        """Get historical data for the specified period"""
        if symbol not in self.data_cache:
            self.data_cache[symbol] = self.load_sample_data(symbol)
        
        data = self.data_cache[symbol]
        mask = (data['timestamp'] >= start_date) & (data['timestamp'] <= end_date)
        return data.loc[mask].copy()
    
    def set_current_date(self, date: datetime.datetime):
        """Set current date for backtesting"""
        self.current_date = date


class LiveDataProvider(DataProvider):
    """Data provider for live trading (mock implementation)"""
    
    def __init__(self):
        self.base_prices = {'AAPL': 150.0, 'GOOGL': 2500.0, 'MSFT': 300.0}
        
    def get_current_price(self, symbol: str) -> float:
        """Get current live price (simulated)"""
        if symbol in self.base_prices:
            # Simulate price movement
            base_price = self.base_prices[symbol]
            variation = np.random.normal(0, 0.005)  # 0.5% variation
            return base_price * (1 + variation)
        return 100.0
    
    def get_historical_data(self, symbol: str, start_date: datetime.datetime, 
                          end_date: datetime.datetime) -> pd.DataFrame:
        """Get recent historical data for analysis"""
        # In real implementation, this would fetch from a live data API
        dates = pd.date_range(start=start_date, end=end_date, freq='H')
        prices = [self.get_current_price(symbol) for _ in dates]
        
        return pd.DataFrame({
            'timestamp': dates,
            'close': prices,
            'volume': np.random.randint(100, 1000, len(dates))
        })


class TradingStrategy(ABC):
    """Abstract base class for trading strategies"""
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame, current_price: float) -> Signal:
        """Generate trading signal based on data and current price"""
        pass


class MovingAverageStrategy(TradingStrategy):
    """Simple moving average crossover strategy"""
    
    def __init__(self, short_window: int = 20, long_window: int = 50):
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signal(self, data: pd.DataFrame, current_price: float) -> Signal:
        """Generate signal based on moving average crossover"""
        if len(data) < self.long_window:
            return Signal(
                timestamp=datetime.datetime.now(),
                symbol="",
                action="HOLD",
                quantity=0,
                price=current_price,
                confidence=0.0,
                reason="Insufficient data"
            )
        
        # Calculate moving averages
        data['ma_short'] = data['close'].rolling(window=self.short_window).mean()
        data['ma_long'] = data['close'].rolling(window=self.long_window).mean()
        
        # Get latest values
        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else latest
        
        # Generate signal
        action = "HOLD"
        confidence = 0.5
        reason = "No clear signal"
        
        if latest['ma_short'] > latest['ma_long'] and previous['ma_short'] <= previous['ma_long']:
            action = "BUY"
            confidence = 0.8
            reason = "MA crossover: Short MA crossed above Long MA"
        elif latest['ma_short'] < latest['ma_long'] and previous['ma_short'] >= previous['ma_long']:
            action = "SELL"
            confidence = 0.8
            reason = "MA crossover: Short MA crossed below Long MA"
        
        return Signal(
            timestamp=datetime.datetime.now(),
            symbol="",
            action=action,
            quantity=100 if action != "HOLD" else 0,
            price=current_price,
            confidence=confidence,
            reason=reason
        )


class Portfolio:
    """Portfolio management class"""
    
    def __init__(self, initial_cash: float = 100000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Dict] = []
        
    def execute_trade(self, signal: Signal) -> bool:
        """Execute a trade based on signal"""
        try:
            total_cost = signal.quantity * signal.price
            
            if signal.action == "BUY":
                if self.cash >= total_cost:
                    self.cash -= total_cost
                    
                    if signal.symbol in self.positions:
                        # Add to existing position
                        pos = self.positions[signal.symbol]
                        total_quantity = pos.quantity + signal.quantity
                        weighted_price = ((pos.quantity * pos.entry_price) + 
                                        (signal.quantity * signal.price)) / total_quantity
                        pos.quantity = total_quantity
                        pos.entry_price = weighted_price
                    else:
                        # Create new position
                        self.positions[signal.symbol] = Position(
                            symbol=signal.symbol,
                            quantity=signal.quantity,
                            entry_price=signal.price,
                            entry_time=signal.timestamp
                        )
                    
                    self._record_trade(signal, "EXECUTED")
                    return True
                else:
                    self._record_trade(signal, "REJECTED_INSUFFICIENT_FUNDS")
                    return False
                    
            elif signal.action == "SELL":
                if signal.symbol in self.positions:
                    pos = self.positions[signal.symbol]
                    if pos.quantity >= signal.quantity:
                        self.cash += signal.quantity * signal.price
                        pos.quantity -= signal.quantity
                        
                        if pos.quantity == 0:
                            del self.positions[signal.symbol]
                        
                        self._record_trade(signal, "EXECUTED")
                        return True
                    else:
                        self._record_trade(signal, "REJECTED_INSUFFICIENT_SHARES")
                        return False
                else:
                    self._record_trade(signal, "REJECTED_NO_POSITION")
                    return False
                    
        except Exception as e:
            logging.error(f"Error executing trade: {e}")
            self._record_trade(signal, f"ERROR_{str(e)}")
            return False
        
        return False
    
    def _record_trade(self, signal: Signal, status: str):
        """Record trade in history"""
        self.trade_history.append({
            'timestamp': signal.timestamp,
            'symbol': signal.symbol,
            'action': signal.action,
            'quantity': signal.quantity,
            'price': signal.price,
            'status': status,
            'reason': signal.reason
        })
    
    def update_positions(self, data_provider: DataProvider):
        """Update current prices and P&L for all positions"""
        for symbol, position in self.positions.items():
            current_price = data_provider.get_current_price(symbol)
            position.current_price = current_price
            position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
    
    def get_portfolio_value(self, data_provider: DataProvider) -> float:
        """Calculate total portfolio value"""
        self.update_positions(data_provider)
        total_value = self.cash
        
        for position in self.positions.values():
            total_value += position.quantity * position.current_price
            
        return total_value
    
    def get_performance_summary(self, data_provider: DataProvider) -> Dict:
        """Get portfolio performance summary"""
        current_value = self.get_portfolio_value(data_provider)
        total_return = current_value - self.initial_cash
        return_pct = (total_return / self.initial_cash) * 100
        
        return {
            'initial_cash': self.initial_cash,
            'current_cash': self.cash,
            'current_value': current_value,
            'total_return': total_return,
            'return_percentage': return_pct,
            'positions': len(self.positions),
            'trades_executed': len([t for t in self.trade_history if t['status'] == 'EXECUTED'])
        }


class TradingSystem:
    """Main trading system class"""
    
    def __init__(self, mode: TradingMode, strategy: TradingStrategy, 
                 initial_cash: float = 100000.0):
        self.mode = mode
        self.strategy = strategy
        self.portfolio = Portfolio(initial_cash)
        
        # Initialize data provider based on mode
        if mode == TradingMode.BACKTEST:
            self.data_provider = HistoricalDataProvider()
        else:
            self.data_provider = LiveDataProvider()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def run_backtest(self, symbols: List[str], start_date: datetime.datetime, 
                    end_date: datetime.datetime):
        """Run backtesting for specified period"""
        if self.mode != TradingMode.BACKTEST:
            raise ValueError("System must be in BACKTEST mode")
        
        self.logger.info(f"Starting backtest from {start_date} to {end_date}")
        
        for symbol in symbols:
            self.logger.info(f"Processing symbol: {symbol}")
            
            # Get historical data
            data = self.data_provider.get_historical_data(symbol, start_date, end_date)
            
            if data.empty:
                self.logger.warning(f"No data available for {symbol}")
                continue
            
            # Simulate trading day by day
            for i in range(len(data)):
                current_date = data.iloc[i]['timestamp']
                current_price = data.iloc[i]['close']
                
                # Set current date for data provider
                self.data_provider.set_current_date(current_date)
                
                # Get historical data up to current date for strategy
                historical_data = data.iloc[:i+1].copy()
                
                if len(historical_data) < 2:
                    continue
                
                # Generate signal
                signal = self.strategy.generate_signal(historical_data, current_price)
                signal.symbol = symbol
                signal.timestamp = current_date
                
                # Execute trade if signal is not HOLD
                if signal.action != "HOLD":
                    executed = self.portfolio.execute_trade(signal)
                    if executed:
                        self.logger.info(f"Executed {signal.action} for {symbol} at {signal.price}")
        
        # Final performance summary
        summary = self.portfolio.get_performance_summary(self.data_provider)
        self.logger.info(f"Backtest completed. Final return: {summary['return_percentage']:.2f}%")
        return summary
    
    def run_live(self, symbols: List[str], duration_seconds: int = 3600):
        """Run live trading for specified duration"""
        if self.mode != TradingMode.LIVE:
            raise ValueError("System must be in LIVE mode")
        
        self.logger.info(f"Starting live trading for {duration_seconds} seconds")
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            for symbol in symbols:
                try:
                    # Get current price
                    current_price = self.data_provider.get_current_price(symbol)
                    
                    # Get recent historical data for strategy analysis
                    end_date = datetime.datetime.now()
                    start_date = end_date - datetime.timedelta(days=30)  # Last 30 days
                    recent_data = self.data_provider.get_historical_data(symbol, start_date, end_date)
                    
                    if recent_data.empty:
                        continue
                    
                    # Generate signal
                    signal = self.strategy.generate_signal(recent_data, current_price)
                    signal.symbol = symbol
                    signal.timestamp = datetime.datetime.now()
                    
                    # Execute trade if signal is not HOLD
                    if signal.action != "HOLD":
                        executed = self.portfolio.execute_trade(signal)
                        if executed:
                            self.logger.info(f"Executed {signal.action} for {symbol} at {signal.price}")
                
                except Exception as e:
                    self.logger.error(f"Error processing {symbol}: {e}")
            
            # Update portfolio
            self.portfolio.update_positions(self.data_provider)
            
            # Wait before next iteration
            time.sleep(10)  # Check every 10 seconds
        
        # Final performance summary
        summary = self.portfolio.get_performance_summary(self.data_provider)
        self.logger.info(f"Live trading completed. Current return: {summary['return_percentage']:.2f}%")
        return summary
    
    def get_current_status(self) -> Dict:
        """Get current system status"""
        return {
            'mode': self.mode.value,
            'portfolio_summary': self.portfolio.get_performance_summary(self.data_provider),
            'positions': {symbol: {
                'quantity': pos.quantity,
                'entry_price': pos.entry_price,
                'current_price': pos.current_price,
                'unrealized_pnl': pos.unrealized_pnl
            } for symbol, pos in self.portfolio.positions.items()},
            'recent_trades': self.portfolio.trade_history[-10:]  # Last 10 trades
        }


def main():
    """Example usage of the trading system"""
    
    # Example 1: Backtest mode
    print("=== BACKTEST MODE ===")
    strategy = MovingAverageStrategy(short_window=20, long_window=50)
    backtest_system = TradingSystem(TradingMode.BACKTEST, strategy, initial_cash=100000)
    
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    start_date = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2023, 12, 31)
    
    backtest_results = backtest_system.run_backtest(symbols, start_date, end_date)
    print("Backtest Results:")
    print(json.dumps(backtest_results, indent=2, default=str))
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Live mode (short duration for demo)
    print("=== LIVE MODE ===")
    live_system = TradingSystem(TradingMode.LIVE, strategy, initial_cash=100000)
    
    # Run for 30 seconds as demo
    live_results = live_system.run_live(symbols, duration_seconds=30)
    print("Live Trading Results:")
    print(json.dumps(live_results, indent=2, default=str))
    
    # Show current status
    print("\nCurrent System Status:")
    print(json.dumps(live_system.get_current_status(), indent=2, default=str))


if __name__ == "__main__":
    main()