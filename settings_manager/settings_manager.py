import pathlib as path
import json

class SettingsManager:
    def __init__(self, folders: list[tuple[str,bool]], timers: list[int], last_timer: int):
        self.folders = folders
        self.timers = timers
        self.last_timer = last_timer

        config_path = path.Path("~/.config/draw-this").expanduser()
        config_path.mkdir(parents=True, exist_ok=True)
        self.config_file = config_path / "draw-this.json"
        self.read_config()

    def get_folders(self):
        return self.folders

    def set_folders(self, folders: list[tuple[str,bool]]):
        if folders != self.folders:
            self.folders = folders

    def get_last_timer(self):
        return self.last_timer

    def set_last_timer(self, last_timer: int):
        self.last_timer = last_timer

    def get_timers(self):
        return self.timers

    def set_timers(self, timers: list[int]):
        if timers != self.timers:
            self.timers = timers
            self.timers = sorted(self.timers)

    def read_config(self):
        if not self.config_file.exists():
            self.config_file.touch()

        try:
            with open(self.config_file, "r", encoding='utf-8') as config:
                read_data = json.load(config)
        except (json.JSONDecodeError, FileNotFoundError):
            read_data = {"folders": [], "timers": [], "last_timer": 0}

        self.folders = [(item.get("path",""), item.get("enabled", False)) for item in read_data.get("folders", [])]
        self.timers = read_data.get("timers", [])
        self.last_timer = read_data.get("last_timer", 0)

    def write_config(self):
        data = {
            "folders": [{"path": folder_path, "enabled": enabled} for folder_path, enabled in self.folders],
            "timers": [timer for timer in self.timers],
            "last_timer": self.last_timer
        }
        with open(file=self.config_file, mode='w', encoding='utf-8') as config:
            json.dump(obj=data, fp=config, indent=4)

