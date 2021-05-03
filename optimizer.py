from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.hierarchical_portfolio import HRPOpt
from pypfopt.cla import CLA
from pypfopt import risk_models, expected_returns
import pandas as pd

from ds import Portfolio
from processor import PortfolioProcessor

class EffOptimizer:
    def __init__(self, processor=IndexProcessor()):
        self.portfolio = Portfolio()
        self.processor = processor
        self.mu = expected_returns.capm_return(processor.close_matrix)
        self.s = risk_models.CovarianceShrinkage(processor.close_matrix).ledoit_wolf()
        self.optimizer = ''

    def optimize_max_sharpe(self):
        self.optimizer = EfficientFrontier(self.mu, self.s)

        self.portfolio.composition = self.optimizer.max_sharpe()
        self.portfolio.construct(self.processor.meta_data_loc)

    def optimize_min_volatility(self):
        self.s = risk_models.sample_cov(self.processor.close_matrix)
        self.optimizer = EfficientFrontier(None, self.s)

        self.portfolio.composition = self.optimizer.min_volatility()
        self.portfolio.construct(self.processor.meta_data_loc)

class HRPOptimizer:
    def __init__(self, processor=IndexProcessor()):
        self.portfolio = Portfolio()
        self.processor = processor

        self.processor.process_close()
        self.mu = expected_returns.returns_from_prices(processor.close_matrix)

        self.optimizer = HRPOpt(self.mu)

    def optimize(self):
        self.optimizer.optimize()
        self.portfolio.composition = self.optimizer.clean_weights()
        self.portfolio.construct(self.processor.meta_data_loc)

class CLAOptimizer:
    def __init__(self, processor=IndexProcessor()):
        self.portfolio = Portfolio()
        self.processor = processor

        self.processor.process_close()
        self.mu = expected_returns.returns_from_prices(processor.close_matrix)
        self.s = risk_models.sample_cov(processor.close_matrix)

        self.optimizer = CLA(mu, s)

    def optimize_max_sharpe(self):
        self.portfolio.composition = self.optimizer.max_sharpe()
        self.portfolio.construct(self.processor.meta_data_loc)

    def optimize_min_volatility(self):
        self.portfolio.composition = self.optimizer.min_volatility()
        self.portfolio.construct(self.processor.meta_data_loc)

class DeepDowOptimizer:
    pass