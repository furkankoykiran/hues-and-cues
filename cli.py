#!/usr/bin/env python3
"""
Command Line Interface for the Trading System

This script provides a simple CLI to run the trading system in either
backtest or live mode with customizable parameters.
"""

import argparse
import json
import datetime
import sys
import os
from trading_system import TradingSystem, TradingMode, MovingAverageStrategy


def load_config(config_path: str = "config.json") -> dict:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file {config_path} not found. Using default settings.")
        return {
            "trading_config": {
                "initial_cash": 100000.0,
                "symbols": ["AAPL", "GOOGL", "MSFT"]
            },
            "strategy_config": {
                "moving_average": {
                    "short_window": 20,
                    "long_window": 50
                }
            }
        }


def run_backtest(args, config):
    """Run the system in backtest mode"""
    print("Starting Backtest Mode...")
    print(f"Symbols: {args.symbols}")
    print(f"Period: {args.start_date} to {args.end_date}")
    print(f"Initial Cash: ${args.initial_cash:,.2f}")
    print("-" * 50)
    
    # Create strategy
    strategy_config = config.get("strategy_config", {}).get("moving_average", {})
    strategy = MovingAverageStrategy(
        short_window=strategy_config.get("short_window", 20),
        long_window=strategy_config.get("long_window", 50)
    )
    
    # Create trading system
    system = TradingSystem(TradingMode.BACKTEST, strategy, args.initial_cash)
    
    # Parse dates
    start_date = datetime.datetime.strptime(args.start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")
    
    # Run backtest
    results = system.run_backtest(args.symbols, start_date, end_date)
    
    # Display results
    print("\n" + "=" * 50)
    print("BACKTEST RESULTS")
    print("=" * 50)
    print(f"Initial Cash: ${results['initial_cash']:,.2f}")
    print(f"Final Value: ${results['current_value']:,.2f}")
    print(f"Total Return: ${results['total_return']:,.2f}")
    print(f"Return %: {results['return_percentage']:.2f}%")
    print(f"Trades Executed: {results['trades_executed']}")
    print(f"Active Positions: {results['positions']}")
    
    # Show trade history
    if hasattr(system.portfolio, 'trade_history'):
        executed_trades = [t for t in system.portfolio.trade_history if t['status'] == 'EXECUTED']
        if executed_trades:
            print(f"\nRecent Trades (last 5):")
            for trade in executed_trades[-5:]:
                print(f"  {trade['timestamp'].strftime('%Y-%m-%d')} - "
                      f"{trade['action']} {trade['quantity']} {trade['symbol']} "
                      f"at ${trade['price']:.2f}")


def run_live(args, config):
    """Run the system in live mode"""
    print("Starting Live Trading Mode...")
    print(f"Symbols: {args.symbols}")
    print(f"Duration: {args.duration} seconds")
    print(f"Initial Cash: ${args.initial_cash:,.2f}")
    print("-" * 50)
    print("WARNING: This is a simulation. No real trades will be executed.")
    print("-" * 50)
    
    # Create strategy
    strategy_config = config.get("strategy_config", {}).get("moving_average", {})
    strategy = MovingAverageStrategy(
        short_window=strategy_config.get("short_window", 20),
        long_window=strategy_config.get("long_window", 50)
    )
    
    # Create trading system
    system = TradingSystem(TradingMode.LIVE, strategy, args.initial_cash)
    
    # Run live trading
    try:
        results = system.run_live(args.symbols, args.duration)
        
        # Display results
        print("\n" + "=" * 50)
        print("LIVE TRADING RESULTS")
        print("=" * 50)
        print(f"Initial Cash: ${results['initial_cash']:,.2f}")
        print(f"Final Value: ${results['current_value']:,.2f}")
        print(f"Total Return: ${results['total_return']:,.2f}")
        print(f"Return %: {results['return_percentage']:.2f}%")
        print(f"Trades Executed: {results['trades_executed']}")
        print(f"Active Positions: {results['positions']}")
        
        # Show current status
        status = system.get_current_status()
        if status['positions']:
            print("\nCurrent Positions:")
            for symbol, pos in status['positions'].items():
                pnl_color = "+" if pos['unrealized_pnl'] >= 0 else ""
                print(f"  {symbol}: {pos['quantity']} shares @ ${pos['entry_price']:.2f} "
                      f"(Current: ${pos['current_price']:.2f}, "
                      f"P&L: {pnl_color}${pos['unrealized_pnl']:.2f})")
        
    except KeyboardInterrupt:
        print("\n\nTrading interrupted by user.")
        status = system.get_current_status()
        summary = status['portfolio_summary']
        print(f"Final Portfolio Value: ${summary['current_value']:,.2f}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Trading System CLI - Run backtests or live trading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run backtest with default settings
  python cli.py backtest
  
  # Run backtest with custom symbols and dates
  python cli.py backtest --symbols AAPL MSFT --start-date 2023-01-01 --end-date 2023-06-30
  
  # Run live trading for 5 minutes
  python cli.py live --duration 300
  
  # Run with custom initial cash
  python cli.py backtest --initial-cash 50000
        """
    )
    
    # Global arguments
    parser.add_argument(
        '--config', 
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    parser.add_argument(
        '--initial-cash',
        type=float,
        default=100000.0,
        help='Initial cash amount (default: 100000)'
    )
    parser.add_argument(
        '--symbols',
        nargs='+',
        default=['AAPL', 'GOOGL', 'MSFT'],
        help='Symbols to trade (default: AAPL GOOGL MSFT)'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='mode', help='Trading mode')
    
    # Backtest subcommand
    backtest_parser = subparsers.add_parser('backtest', help='Run backtesting')
    backtest_parser.add_argument(
        '--start-date',
        default='2023-01-01',
        help='Start date for backtest (YYYY-MM-DD, default: 2023-01-01)'
    )
    backtest_parser.add_argument(
        '--end-date',
        default='2023-12-31',
        help='End date for backtest (YYYY-MM-DD, default: 2023-12-31)'
    )
    
    # Live subcommand
    live_parser = subparsers.add_parser('live', help='Run live trading')
    live_parser.add_argument(
        '--duration',
        type=int,
        default=300,
        help='Duration in seconds (default: 300)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        sys.exit(1)
    
    # Load configuration
    config = load_config(args.config)
    
    # Check dependencies
    try:
        import pandas
        import numpy
    except ImportError as e:
        print(f"Missing required dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        sys.exit(1)
    
    # Run the appropriate mode
    try:
        if args.mode == 'backtest':
            run_backtest(args, config)
        elif args.mode == 'live':
            run_live(args, config)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()