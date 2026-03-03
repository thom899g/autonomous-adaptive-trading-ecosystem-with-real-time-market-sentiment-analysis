"""
Configuration management for the trading ecosystem.
Uses environment variables with Firebase as primary configuration store.
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging
from dotenv import load_dotenv

load_dotenv()

@dataclass
class FirebaseConfig:
    """Firebase configuration with validation"""
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    client_x509_cert_url: str
    
    @classmethod
    def from_env(cls) -> 'FirebaseConfig':
        """Initialize from environment variables with validation"""
        required_vars = [
            'FIREBASE_PROJECT_ID',
            'FIREBASE_PRIVATE_KEY_ID',
            'FIREBASE_PRIVATE_KEY',
            'FIREBASE_CLIENT_EMAIL',
            'FIREBASE_CLIENT_ID',
            'FIREBASE_CLIENT_X509_CERT_URL'
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise ValueError(f"Missing Firebase environment variables: {missing}")
        
        # Handle newline formatting in private key
        private_key = os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n')
        
        return cls(
            project_id=os.getenv('FIREBASE_PROJECT_ID', ''),
            private_key_id=os.getenv('FIREBASE_PRIVATE_KEY_ID', ''),
            private_key=private_key,
            client_email=os.getenv('FIREBASE_CLIENT_EMAIL', ''),
            client_id=os.getenv('FIREBASE_CLIENT_ID', ''),
            client_x509_cert_url=os.getenv('FIREBASE_CLIENT_X509_CERT_URL', '')
        )

@dataclass
class TradingConfig:
    """Trading system configuration"""
    # Risk management
    max_position_size: float = 0.1  # 10% of portfolio per position
    max_daily_loss: float = 0.02   # 2% max daily loss
    stop_loss_pct: float = 0.05    # 5% stop loss
    take_profit_pct: float = 0.10  # 10% take profit
    
    # Data collection
    news_update_interval: int = 300  # 5 minutes
    market_data_interval: int = 60   # 1 minute
    sentiment_window_hours: int = 24
    
    # Trading parameters
    min_confidence_score: float = 0.7
    max_open_positions: int = 5
    
    # Exchange configuration (example using CCXT-compatible structure)
    exchange_id: str = "binance"
    testnet: bool = True
    api_timeout: int = 30000

@dataclass  
class SentimentConfig:
    """Sentiment analysis configuration"""
    nltk_data_path: str = "./nltk_data"
    vader_lexicon: str = "vader_lexicon.txt"
    min_sentiment_score: float = -0.8
    max_sentiment_score: float = 0.8
    neutral_threshold: float = 0.1
    
    # Text processing
    max_text_length: int = 1000
    min_text_length: int = 10

class ConfigManager:
    """Centralized configuration management with Firebase sync"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.firebase_config: Optional[FirebaseConfig] = None
        self.trading_config = TradingConfig()
        self.sentiment_config = SentimentConfig()
        
    def initialize(self) -> bool:
        """Initialize configuration from environment and Firebase"""
        try:
            # Load Firebase config
            self.firebase_config = FirebaseConfig.from_env()
            
            # Initialize Firebase connection
            from .firebase_client import FirebaseClient
            self.firebase_client = FirebaseClient(self.firebase_config)
            
            # Load runtime config from Firebase
            self._load_runtime_config()
            
            self.logger.info("Configuration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize configuration: {e}")
            return False
    
    def _load_runtime_config(self):
        """Load runtime configuration from Firebase"""
        try:
            config_data = self.firebase_client.get_document("config", "trading_system")
            if config_data:
                # Update trading config with Firebase values
                for key, value in config_data.items():
                    if hasattr(self.trading_config, key):
                        setattr(self.trading_config, key, value)
                        
        except Exception as e:
            self.logger.warning(f"Could not load runtime config from Firebase: {e}")
            # Continue with default config
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration in Firebase"""
        try:
            if not self.firebase_client:
                raise RuntimeError("Firebase client not initialized")
                
            self.firebase_client.update_document(
                "config", 
                "trading_system",
                updates
            )
            
            # Update local config
            for key, value in updates.items():
                if hasattr(self.trading_config, key):
                    setattr(self.trading_config, key, value)
                    
            self.logger.info(f"Updated configuration: {updates}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            return False

# Global configuration instance
config_manager = ConfigManager()