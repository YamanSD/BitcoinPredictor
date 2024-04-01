from .config import load_config, Config, HfConfig, ProxiesConfig, \
    KaggleConfig, BinanceConfig, AlphaVantageConfig, FearGreedConfig, \
    ObserverConfig, ServerConfig

# Default config instance
config: Config = load_config("./config.json")
