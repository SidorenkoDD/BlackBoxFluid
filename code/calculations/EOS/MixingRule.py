from abc import ABC, abstractmethod 


class MixingRule(ABC):
    ...

class ClassicMixingRule(MixingRule):
    ...

class HuronVidalMixingRule(MixingRule):
    ...



class MixingRuleFactory:
    ...
