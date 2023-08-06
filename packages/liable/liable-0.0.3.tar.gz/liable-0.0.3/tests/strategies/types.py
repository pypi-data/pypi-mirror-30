from hypothesis import strategies
from types import (FunctionType,
                   ModuleType)
modules = strategies.builds(ModuleType)
functions = strategies.builds(FunctionType)
from types import (FunctionType,
                   ModuleType)
from hypothesis import strategies
modules = strategies.builds(ModuleType)
functions = strategies.builds(FunctionType)
