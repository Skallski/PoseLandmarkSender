import json
import os
import sys


class ConfigLoader:
    
    @staticmethod
    def _get_cfg_path() -> str :
        base_path = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
        return os.path.join(base_path, "config.json")
    
    @staticmethod
    def load_config() -> dict:
        cfg_path = ConfigLoader._get_cfg_path()
        if not os.path.exists(cfg_path):
            raise FileNotFoundError(f"Config file not found: {cfg_path}")
    
        with open(cfg_path, "r", encoding="utf-8") as f:
            return json.load(f)