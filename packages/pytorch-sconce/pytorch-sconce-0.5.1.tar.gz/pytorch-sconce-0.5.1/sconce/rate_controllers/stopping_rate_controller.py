from sconce.rate_controllers.base import RateController
from torch.autograd import Variable

import numpy as np


class StoppingRateController(RateController):
    def __init__(self, stop_factor=None, loss_key='training_loss'):
        self.stop_factor = stop_factor
        self.loss_key = loss_key
        self.min_loss = None

    def start_session(self, num_steps):
        self.learning_rates = np.linspace(self.min_learning_rate,
                                self.max_learning_rate,
                                num_steps)

    def new_learning_rate(self, step, data):
        if self.learning_rates is None:
            raise RuntimeError("You must call 'start_session' before calling "
                    "'new_learning_rate'")
        if step >= len(self.learning_rates):
            raise RuntimeError(f"Argument step={step}, should not equal "
                    f"or exceed num_steps={len(self.learning_rates)}")

        if self.should_continue(data):
            new_learning_rate = self.learning_rates[step]
            return new_learning_rate
        else:
            return None

    def should_continue(self, data):
        if self.loss_key not in data:
            return True

        loss = data[self.loss_key]
        if isinstance(loss, Variable):
            loss = loss.data[0]

        if self.min_loss is None or loss < self.min_loss:
            self.min_loss = loss

        if (self.stop_factor is not None and
                loss > self.min_loss * self.stop_factor):
            return False

        return True
