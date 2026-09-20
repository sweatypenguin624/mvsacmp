from ultralytics.trackers import BOTSORT, BYTETracker
import inspect
print(inspect.signature(BYTETracker.__init__))
print(inspect.signature(BYTETracker.update))
