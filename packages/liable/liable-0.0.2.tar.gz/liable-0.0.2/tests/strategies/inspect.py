from hypothesis import strategies
import inspect
parameters = strategies.builds(inspect.Parameter,
                               name=strategies.none(),
                               kind=strategies.none(),
                               default=strategies.none(),
                               annotation=strategies.none())
from hypothesis import strategies
import inspect
parameters = strategies.builds(inspect.Parameter,
                               name=strategies.none(),
                               kind=strategies.none(),
                               default=strategies.none(),
                               annotation=strategies.none())
