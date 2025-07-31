#!/usr/bin/env python3
"""
Trading System Usage Examples

Bu dosya trading sisteminin nasıl kullanılacağına dair örnekler içerir.
"""

from trading_system import TradingSystem, TradingMode, MovingAverageStrategy, Signal
import datetime
import json


def example_backtest():
    """Backtest mode örneği"""
    print("=== BACKTEST ÖRNEĞİ ===")
    
    # Strateji oluştur
    strategy = MovingAverageStrategy(short_window=10, long_window=30)
    
    # Trading sistemi oluştur
    system = TradingSystem(TradingMode.BACKTEST, strategy, initial_cash=50000)
    
    # Test parametreleri
    symbols = ['AAPL', 'MSFT']
    start_date = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2023, 6, 30)
    
    print(f"Semboller: {symbols}")
    print(f"Tarih Aralığı: {start_date.date()} - {end_date.date()}")
    print(f"Başlangıç Nakit: ${system.portfolio.initial_cash:,.2f}")
    print("-" * 50)
    
    # Backtest çalıştır
    results = system.run_backtest(symbols, start_date, end_date)
    
    # Sonuçları göster
    print("\nSonuçlar:")
    print(f"Toplam Getiri: ${results['total_return']:,.2f}")
    print(f"Getiri %: {results['return_percentage']:.2f}%")
    print(f"İşlem Sayısı: {results['trades_executed']}")
    print(f"Aktif Pozisyon: {results['positions']}")
    
    return results


def example_live():
    """Live mode örneği"""
    print("\n=== LIVE TRADİNG ÖRNEĞİ ===")
    
    # Farklı strateji parametreleri ile
    strategy = MovingAverageStrategy(short_window=5, long_window=15)
    
    # Live trading sistemi
    system = TradingSystem(TradingMode.LIVE, strategy, initial_cash=25000)
    
    symbols = ['AAPL', 'GOOGL']
    duration = 20  # 20 saniye test
    
    print(f"Semboller: {symbols}")
    print(f"Süre: {duration} saniye")
    print(f"Başlangıç Nakit: ${system.portfolio.initial_cash:,.2f}")
    print("-" * 50)
    print("NOT: Bu bir simülasyondur, gerçek işlem yapılmaz.")
    print("-" * 50)
    
    # Live trading çalıştır
    results = system.run_live(symbols, duration)
    
    # Sonuçları göster
    print("\nSonuçlar:")
    print(f"Final Değer: ${results['current_value']:,.2f}")
    print(f"Getiri: ${results['total_return']:,.2f}")
    print(f"Getiri %: {results['return_percentage']:.2f}%")
    print(f"İşlem Sayısı: {results['trades_executed']}")
    
    # Mevcut durumu göster
    status = system.get_current_status()
    if status['positions']:
        print("\nAktif Pozisyonlar:")
        for symbol, pos in status['positions'].items():
            print(f"  {symbol}: {pos['quantity']} adet @ ${pos['entry_price']:.2f}")
            print(f"    Güncel Fiyat: ${pos['current_price']:.2f}")
            print(f"    P&L: ${pos['unrealized_pnl']:,.2f}")
    
    return results


def example_custom_strategy():
    """Özel strateji örneği"""
    print("\n=== ÖZEL STRATEJİ ÖRNEĞİ ===")
    
    class SimpleStrategy(MovingAverageStrategy):
        """Basit özel strateji - sadece BUY sinyali verir"""
        
        def generate_signal(self, data, current_price):
            signal = super().generate_signal(data, current_price)
            
            # Sadece BUY sinyallerine izin ver
            if signal.action == "SELL":
                signal.action = "HOLD"
                signal.reason = "SELL sinyali engellendi"
            
            return signal
    
    # Özel strateji ile sistem
    custom_strategy = SimpleStrategy(short_window=5, long_window=20)
    system = TradingSystem(TradingMode.BACKTEST, custom_strategy, initial_cash=30000)
    
    # Kısa test
    symbols = ['AAPL']
    start_date = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2023, 3, 31)
    
    print("Özel strateji: Sadece BUY sinyalleri")
    print(f"Test Dönemi: {start_date.date()} - {end_date.date()}")
    
    results = system.run_backtest(symbols, start_date, end_date)
    
    print(f"\nSonuçlar:")
    print(f"Getiri %: {results['return_percentage']:.2f}%")
    print(f"İşlem Sayısı: {results['trades_executed']}")
    
    return results


def example_portfolio_analysis():
    """Portfolio analizi örneği"""
    print("\n=== PORTFOLIO ANALİZİ ÖRNEĞİ ===")
    
    strategy = MovingAverageStrategy(short_window=15, long_window=40)
    system = TradingSystem(TradingMode.BACKTEST, strategy, initial_cash=100000)
    
    # Daha fazla sembol ile test
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    start_date = datetime.datetime(2023, 1, 1)
    end_date = datetime.datetime(2023, 12, 31)
    
    print(f"Portfolio Analizi: {len(symbols)} sembol")
    print(f"Tarih Aralığı: Tam 2023 yılı")
    
    results = system.run_backtest(symbols, start_date, end_date)
    
    # Detaylı analiz
    print(f"\nPortfolio Performansı:")
    print(f"Başlangıç: ${results['initial_cash']:,.2f}")
    print(f"Son Değer: ${results['current_value']:,.2f}")
    print(f"Toplam Getiri: ${results['total_return']:,.2f}")
    print(f"Getiri Oranı: {results['return_percentage']:.2f}%")
    print(f"Gerçekleşen İşlem: {results['trades_executed']}")
    print(f"Aktif Pozisyon: {results['positions']}")
    
    # Trade history analizi
    if hasattr(system.portfolio, 'trade_history'):
        trades = system.portfolio.trade_history
        executed_trades = [t for t in trades if t['status'] == 'EXECUTED']
        
        if executed_trades:
            buy_trades = [t for t in executed_trades if t['action'] == 'BUY']
            sell_trades = [t for t in executed_trades if t['action'] == 'SELL']
            
            print(f"\nİşlem Detayları:")
            print(f"Toplam BUY işlemi: {len(buy_trades)}")
            print(f"Toplam SELL işlemi: {len(sell_trades)}")
            
            if executed_trades:
                print(f"\nSon 3 İşlem:")
                for trade in executed_trades[-3:]:
                    print(f"  {trade['timestamp'].strftime('%Y-%m-%d')} - "
                          f"{trade['action']} {trade['quantity']} {trade['symbol']} "
                          f"@ ${trade['price']:.2f}")
    
    return results


def main():
    """Ana fonksiyon - tüm örnekleri çalıştır"""
    try:
        # Backtest örneği
        backtest_results = example_backtest()
        
        # Live trading örneği
        live_results = example_live()
        
        # Özel strateji örneği
        custom_results = example_custom_strategy()
        
        # Portfolio analizi
        portfolio_results = example_portfolio_analysis()
        
        # Özet karşılaştırma
        print("\n" + "="*60)
        print("ÖZET KARŞILAŞTIRMA")
        print("="*60)
        
        examples = [
            ("Standart Backtest", backtest_results),
            ("Live Trading", live_results),
            ("Özel Strateji", custom_results),
            ("Portfolio Analizi", portfolio_results)
        ]
        
        for name, result in examples:
            print(f"{name:20}: {result['return_percentage']:8.2f}% "
                  f"({result['trades_executed']:2d} işlem)")
        
        print("\nTüm örnekler başarıyla tamamlandı!")
        
    except Exception as e:
        print(f"Hata: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()