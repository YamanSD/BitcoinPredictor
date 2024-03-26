from .config import load_config, Config, HfConfig, ProxiesConfig, KaggleConfig

# Default config instance
config: Config = load_config("./Config/config.json")
