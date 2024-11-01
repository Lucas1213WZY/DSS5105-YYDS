# Makes the validator package importable
from .validator import GreenMarkValidator
from .viz_helpers import ValidationVisualizer
from .feedback import FeedbackCollector

# Can add version info
__version__ = '1.0.0'