# Physical Constants:
import enum

g_earth = 9.807
G = 6.67428E-11
c = 299792458


class Distance(enum.Enum):
    """Units of distance."""

    R_Sol = (6.957E8,)  #: Mean radius of the sun.

    R_Jupiter = (7.1492E7,)  #: Mean radius of Jupiter

    R_Earth = (6.3568E6,)  #: Mean radius of the Earth

    pc = (3.085677581e16,)  #: Parsec

    lyr = (9.4607304725808e15,)  #: Light Year

    AU = (1.495978707e11,)  #: Astronomical Unit

    km = (1000,)  #: Kilometer

    m = (1.0,)  #: Meter

    cm = (0.01,)  #: Centimeter

    mm = (0.001,)  #: Millimeter

    def __init__(self, meters):
        self.meters = meters

    def to_m(self, num: float) -> float:
        """
        Convert from num of this unit to meters.

        :param num: quantity of this unit to convert to meters.
        :return: the number of meters in num of this unit.

        """
        return num * self.meters

    def from_m(self, num: float) -> float:
        """
        Convert from num meters to this unit.

        :param num: quantity of meters to convert to this unit
        :return: the number of this unit in num meters

        """
        return num / self.meters

    def calc(self, num: float, src_unit: 'Distance') -> float:
        """
        Convert from num of this target_unit to this unit.

        :param num: number of src_units to convert to this unit.
        :param src_unit: the source units.
        :return: number of this unit in num src_units
        """
        return self.from_m(src_unit.to_m(num))


class Time(enum.Enum):
    """Units of time."""
    s = (1.0,)  #: Seconds
    min = (60.0,)  #: Minutes
    h = (3600.0,)  #: Hours
    day = (86400.0,)  #: days
    yr = (31557600.0,)  #: years
    Myr = (31557600.0 * 1.0E6,)  #: megayears

    def __init__(self, seconds):
        self.seconds = seconds

    def to_s(self, num: float) -> float:
        """
        Convert from num of this unit to seconds.

        :param num: quantity of this unit to convert to seconds.
        :return: the number of seconds in num of this unit.

        """
        return num * self.seconds

    def from_s(self, num: float) -> float:
        """
        Convert from num seconds to this unit.

        :param num: quantity of seconds to convert to this unit
        :return: the number of this unit in num seconds

        """
        return num / self.seconds

    def calc(self, num: float, src_unit: 'Time') -> float:
        """
        Convert from num of this target_unit to this unit.

        :param num: number of src_units to convert to this unit.
        :param src_unit: the source units.
        :return: number of this unit in num src_units
        """
        return self.from_s(src_unit.to_s(num))


class Mass(enum.Enum):
    """Units of mass."""
    g = (0.001,)  #: Grams
    kg = (1.0,)  #: Kilograms
    Sol = (1.9884E30,)  #: Solar masses
    Jupiter = (1.8985219E27,)  #: Jupiter masses
    Earth = (5.9722E24,)  #: Earth masses

    def __init__(self, kgs):
        self.kgs = kgs

    def to_kg(self, num: float) -> float:
        """
        Convert from num of this unit to kgs.

        :param num: quantity of this unit to convert to kgs.
        :return: the number of kgs in num of this unit.

        """
        return num * self.kgs

    def from_kg(self, num: float) -> float:
        """
        Convert from num kgs to this unit.

        :param num: quantity of kgs to convert to this unit
        :return: the number of this unit in num kgs

        """
        return num / self.kgs

    def calc(self, num: float, src_unit: 'Mass') -> float:
        """
        Convert from num of this target_unit to this unit.

        :param num: number of src_units to convert to this unit.
        :param src_unit: the source units.
        :return: number of this unit in num src_units
        """
        return self.from_kg(src_unit.to_kg(num))
