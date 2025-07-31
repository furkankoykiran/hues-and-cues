# Python Trading System

Gelişmiş bir Python trading sistemi hem backtest hem de live modlarda çalışabilir. Sistem, historical data kullanarak backtest yapar veya real-time data ile live trading gerçekleştirir.

## Özellikler

- **İki Mod Desteği**: Backtest ve Live trading modları
- **Modüler Mimari**: Kolay genişletilebilir ve özelleştirilebilir
- **Strateji Framework**: Farklı trading stratejileri implementasyonu
- **Portfolio Yönetimi**: Otomatik pozisyon takibi ve P&L hesaplama
- **Risk Yönetimi**: Configüre edilebilir risk parametreleri
- **Loglama**: Detaylı işlem kayıtları ve performans takibi
- **CLI Interface**: Komut satırından kolay kullanım

## Kurulum

### Gereksinimler

```bash
# Python paketlerini yükle
pip install -r requirements.txt
```

### Bağımlılıklar

- Python 3.7+
- pandas >= 1.5.0
- numpy >= 1.20.0

## Kullanım

### 1. Backtest Modu

Historical data kullanarak strategy performansını test eder:

```bash
# Varsayılan ayarlarla backtest çalıştır
python cli.py backtest

# Özel semboller ve tarih aralığı ile
python cli.py backtest --symbols AAPL MSFT GOOGL --start-date 2023-01-01 --end-date 2023-06-30

# Özel başlangıç nakit miktarı ile
python cli.py backtest --initial-cash 50000
```

### 2. Live Modu

Real-time data ile live trading simülasyonu:

```bash
# 5 dakika live trading
python cli.py live --duration 300

# Özel sembollerle live trading
python cli.py live --symbols AAPL TSLA --duration 600
```

### 3. Python Kodu ile Kullanım

```python
from trading_system import TradingSystem, TradingMode, MovingAverageStrategy
import datetime

# Strategy oluştur
strategy = MovingAverageStrategy(short_window=20, long_window=50)

# Backtest sistemi
backtest_system = TradingSystem(TradingMode.BACKTEST, strategy, initial_cash=100000)
symbols = ['AAPL', 'GOOGL', 'MSFT']
start_date = datetime.datetime(2023, 1, 1)
end_date = datetime.datetime(2023, 12, 31)

# Backtest çalıştır
results = backtest_system.run_backtest(symbols, start_date, end_date)
print(f"Return: {results['return_percentage']:.2f}%")

# Live sistem
live_system = TradingSystem(TradingMode.LIVE, strategy, initial_cash=100000)
live_results = live_system.run_live(symbols, duration_seconds=300)
```

## Sistem Mimarisi

### Ana Bileşenler

1. **TradingSystem**: Ana sistem sınıfı
2. **DataProvider**: Veri sağlayıcı (Historical/Live)
3. **TradingStrategy**: Trading stratejisi interface
4. **Portfolio**: Portfolio yönetimi
5. **Signal**: Trading sinyalleri

### Veri Sağlayıcıları

#### HistoricalDataProvider (Backtest Modu)
- Simulated historical data üretir
- Backtest için gün gün veri işleme
- Deterministik sonuçlar için seed kullanır

#### LiveDataProvider (Live Modu)
- Real-time price simulation
- API entegrasyonu için hazır interface
- Gerçek trading için API keys gerekir

### Trading Stratejileri

#### MovingAverageStrategy
- Short ve long period moving averages
- Crossover sinyalleri
- Configüre edilebilir pencere boyutları

```python
# Strateji oluşturma
strategy = MovingAverageStrategy(short_window=20, long_window=50)
```

## Konfigürasyon

`config.json` dosyası ile sistem ayarları:

```json
{
    "trading_config": {
        "default_mode": "backtest",
        "initial_cash": 100000.0,
        "symbols": ["AAPL", "GOOGL", "MSFT"],
        "backtest": {
            "start_date": "2023-01-01",
            "end_date": "2023-12-31"
        },
        "live": {
            "update_interval_seconds": 10,
            "max_runtime_seconds": 3600
        }
    },
    "strategy_config": {
        "moving_average": {
            "short_window": 20,
            "long_window": 50
        }
    }
}
```

## Performans Raporlama

Sistem şu metrikleri takip eder:

- **Total Return**: Toplam getiri miktarı
- **Return Percentage**: Yüzde getiri
- **Number of Trades**: Gerçekleştirilen işlem sayısı
- **Current Positions**: Aktif pozisyonlar
- **Unrealized P&L**: Realize olmamış kar/zarar

### Örnek Output

```
BACKTEST RESULTS
==================================================
Initial Cash: $100,000.00
Final Value: $112,450.00
Total Return: $12,450.00
Return %: 12.45%
Trades Executed: 23
Active Positions: 2

Recent Trades (last 5):
  2023-12-15 - BUY 100 AAPL at $195.50
  2023-12-18 - SELL 100 MSFT at $375.20
  2023-12-20 - BUY 50 GOOGL at $2,650.00
```

## Geliştirme ve Genişletme

### Yeni Strateji Ekleme

```python
from trading_system import TradingStrategy, Signal
import datetime

class RSIStrategy(TradingStrategy):
    def __init__(self, period=14, oversold=30, overbought=70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signal(self, data, current_price):
        # RSI hesaplama logic
        rsi = self.calculate_rsi(data)
        
        if rsi < self.oversold:
            action = "BUY"
        elif rsi > self.overbought:
            action = "SELL"
        else:
            action = "HOLD"
            
        return Signal(
            timestamp=datetime.datetime.now(),
            symbol="",
            action=action,
            quantity=100,
            price=current_price,
            confidence=0.8,
            reason=f"RSI: {rsi:.2f}"
        )
```

### Veri Sağlayıcı Entegrasyonu

```python
from trading_system import DataProvider
import requests

class AlphaVantageProvider(DataProvider):
    def __init__(self, api_key):
        self.api_key = api_key
        
    def get_current_price(self, symbol):
        # Alpha Vantage API call
        url = f"https://www.alphavantage.co/query"
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.api_key
        }
        response = requests.get(url, params=params)
        data = response.json()
        return float(data['Global Quote']['05. price'])
```

## Risk Uyarıları

⚠️ **Önemli**: Bu sistem eğitim ve test amaçlıdır. Gerçek trading için:

1. **Real Data Sources**: Güvenilir veri kaynakları kullanın
2. **Risk Management**: Stop-loss ve position sizing uygulayın
3. **Backtesting**: Stratejileri kapsamlı test edin
4. **Paper Trading**: Önce kağıt üzerinde test edin
5. **Regulatory Compliance**: Yasal düzenlemelere uyun

## Loglama

Sistem otomatik olarak şu logları tutar:

- **Trade Executions**: Gerçekleştirilen işlemler
- **Signal Generation**: Üretilen sinyaller
- **Portfolio Updates**: Portfolio değişiklikleri
- **Error Handling**: Hata durumları

Log dosyası: `trading_system.log`

## Sorun Giderme

### Yaygın Hatalar

1. **ImportError**: `pip install -r requirements.txt` çalıştırın
2. **Date Format Error**: YYYY-MM-DD formatını kullanın
3. **Insufficient Data**: Daha uzun tarih aralığı deneyin

### Debug Modu

```bash
# Detaylı loglama ile çalıştırma
export PYTHONPATH=.
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from cli import main
main()
" backtest --symbols AAPL
```

## Lisans

MIT License - Detaylar için LICENSE dosyasına bakın.

## Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

## İletişim

Sorular ve öneriler için issue açabilirsiniz.