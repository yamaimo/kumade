# Configuration

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")

Converter = Callable[[str], T]


@dataclass(frozen=True)
class ConfigItem(Generic[T]):
    """
    Configuration item.

    Attributes
    ----------
    name : str
        Name of item.
    converter : Converter[T]
        Convert function from str to type of item value.
    default_value : T
        Default value.
    help : str
        Description of item.
    """

    name: str
    converter: Converter[T]
    default_value: T
    help: str


class ConfigRegistry:
    """
    Configuration registry.
    """

    __instance: Optional["ConfigRegistry"] = None

    @classmethod
    def get_instance(cls) -> "ConfigRegistry":
        """
        Return the singleton instance of configuration registry.

        Returns
        -------
        registry : ConfigRegistry
            The instance of configuration registry.
        """
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self) -> None:
        self.__items: dict[str, ConfigItem] = {}

    def add_item(self, item: ConfigItem) -> None:
        """
        Add a configuration item.

        Parameters
        ----------
        item : ConfigItem
            Configuration item to be added.

        Raises
        ------
        RuntimeError
            If a configuration item with the same name has already been added.
        """
        name = item.name
        if name in self.__items:
            raise RuntimeError(f"Configuration item {name} already exists.")
        self.__items[name] = item

    def get_all_items(self) -> list[ConfigItem]:
        """
        Return all configuration items.

        Returns
        -------
        items : list[ConfigItem]
            List of all configuration items.
        """
        return list(self.__items.values())

    def get_confirmed_values(self, values: dict[str, str]) -> dict[str, Any]:
        """
        Get confirmed configuration values with specified values.

        Parameters
        ----------
        values : dict[str, str]
            User specified values for configuration items.

        Returns
        -------
        confirmed_values : dict[str, str]
            Confirmed configuration values.

        Raises
        ------
        RuntimeError
            If the specified item is not in configuration items.
        """
        for name in values:
            if name not in self.__items:
                raise RuntimeError(f"There is no configuration item named {name}.")

        confirmed_values: dict[str, Any] = {}

        for name, item in self.__items.items():
            if name in values:
                confirmed_values[name] = item.converter(values[name])
            else:
                confirmed_values[name] = item.default_value

        return confirmed_values


class Config:
    """
    Confirmed configuration.
    """

    __instance: Optional["Config"] = None

    @classmethod
    def get_instance(cls) -> "Config":
        """
        Return the singleton instance of configuration.

        Returns
        -------
        config : Config
            The instance of configuration.

        Raises
        ------
        RuntimeError
            If the configuration is not confirmed.
        """
        if cls.__instance is None:
            raise RuntimeError("Configuration is not confirmed.")
        return cls.__instance

    @classmethod
    def set(cls, values: dict[str, Any]) -> None:
        """
        Set confirmed configuration values.

        Parameters
        ----------
        values : dict[str, Any]
            Confirmed configuration values.

        Raises
        ------
        RuntimeError
            If the configuration is already set.
        """
        if cls.__instance is not None:
            raise RuntimeError("Configuration is already set.")
        cls.__instance = cls(values)

    def __init__(self, values: dict[str, Any]) -> None:
        """
        Parameters
        ----------
        values : dict[str, Any]
            Confirmed configuration values.
        """
        self.__values = values

    def get(self, name: str) -> Any:
        """
        Get a configuration value.

        Parameters
        ----------
        name : str
            Name of item to get.

        Returns
        -------
        value : Any
            Value of item.

        Raises
        ------
        RuntimeError
            If the name is not in configuration items.
        """
        if name not in self.__values:
            raise RuntimeError(f"There is no configuration item named {name}.")
        return self.__values[name]

    def __getattr__(self, name: str) -> Any:
        """Alias for get()"""
        return self.get(name)

    def __getitem__(self, name: str) -> Any:
        """Alias for get()"""
        return self.get(name)

    @property
    def values(self) -> dict[str, Any]:
        """Copy of confirmed configuration values."""
        return dict(self.__values)
