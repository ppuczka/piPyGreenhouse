from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import logging


class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    TEMPERATURE_HIGH = "temperature_high"
    TEMPERATURE_LOW = "temperature_low"
    HUMIDITY_HIGH = "humidity_high" 
    HUMIDITY_LOW = "humidity_low"
    SOIL_MOISTURE_HIGH = "soil_moisture_high"
    SOIL_MOISTURE_LOW = "soil_moisture_low"
    LIGHT_INTENSITY_HIGH = "light_intensity_high"
    LIGHT_INTENSITY_LOW = "light_intensity_low"
    SENSOR_ERROR = "sensor_error"
    SYSTEM_ERROR = "system_error"


@dataclass
class Alert:
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    sensor_name: str
    current_value: float
    threshold_value: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "sensor_name": self.sensor_name,
            "current_value": self.current_value,
            "threshold_value": self.threshold_value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class AlertObserver(ABC):
    
    @abstractmethod
    def on_alert(self, alert: Alert) -> None:
        pass


class AlertSubject(ABC):
    
    def __init__(self):
        self._observers: List[AlertObserver] = []
        self._alert_history: List[Alert] = []
        self._max_history_size = 100
    
    def attach(self, observer: AlertObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)
            logging.info(f"Alert observer attached: {observer.__class__.__name__}")
    
    def detach(self, observer: AlertObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)
            logging.info(f"Alert observer detached: {observer.__class__.__name__}")
    
    def notify_observers(self, alert: Alert) -> None:
        self._alert_history.append(alert)
        if len(self._alert_history) > self._max_history_size:
            self._alert_history.pop(0)
        
        logging.info(f"Notifying {len(self._observers)} observers about alert: {alert.alert_type.value}")
        for observer in self._observers:
            try:
                observer.on_alert(alert)
            except Exception as e:
                logging.error(f"Error notifying observer {observer.__class__.__name__}: {e}")
    
    def get_alert_history(self) -> List[Alert]:
        return self._alert_history.copy()


@dataclass
class ThresholdConfig:
    low_threshold: Optional[float] = None
    high_threshold: Optional[float] = None
    low_severity: AlertSeverity = AlertSeverity.MEDIUM
    high_severity: AlertSeverity = AlertSeverity.MEDIUM
    cooldown_seconds: int = 300  # 5 minutes default cooldown
    enabled: bool = True


class AlertManager:
    
    def __init__(self):
        self._last_alert_times: Dict[str, datetime] = {}
    
    def should_send_alert(self, alert_key: str, cooldown_seconds: int) -> bool:
        now = datetime.now()
        last_alert = self._last_alert_times.get(alert_key)
        
        if last_alert is None:
            self._last_alert_times[alert_key] = now
            return True
        
        time_since_last = (now - last_alert).total_seconds()
        if time_since_last >= cooldown_seconds:
            self._last_alert_times[alert_key] = now
            return True
        
        return False
    
    def reset_cooldown(self, alert_key: str) -> None:
        if alert_key in self._last_alert_times:
            del self._last_alert_times[alert_key]


# Global alert manager instance
alert_manager = AlertManager()