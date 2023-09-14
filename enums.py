from enum import Enum, auto


class AutoEnum(Enum):
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name

    @classmethod
    def from_string(cls, name):
        for member in cls:
            if isinstance(member.value, str):
                if member.value.lower() == name.lower():
                    return member
            else:
                if member.name.lower() == name.lower():
                    return member
        raise ValueError(f'No {cls.__name__} member with name {name}')


class UpgradeResult(AutoEnum):
    SUCCESS = auto()
    UPGRADED = auto()
    FAILED = auto()


class NetworkNames(AutoEnum):
    Starknet = auto()
    StarknetTestnet = auto()
