from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.hierarchical_portfolio import HRPOpt
from pypfopt.cla import CLA
from pypfopt import risk_models, expected_returns
import pandas as pd

from ds import Portfolio
from processor import IndexProcessor

class Optimizer:
    def __init__(self, processor=None):
        self.portfolio = Portfolio()
        self.processor = processor
        self.optimizer = None
    
    def optimize(self):
        pass

class EffOptimizer:
    def __init__(self, processor=None):
        super().__init__()
        self.processor = processor
        self.mu = expected_returns.capm_return(processor.close_matrix)
        self.s = risk_models.CovarianceShrinkage(processor.close_matrix).ledoit_wolf()
        self.optimizer = None

    def optimize_max_sharpe(self):
        self.s = risk_models.sample_cov(self.processor.close_matrix)
        self.optimizer = EfficientFrontier(self.mu, self.s)

        self.optimizer.max_sharpe()
        self.portfolio.composition = self.optimizer.clean_weights()
        self.portfolio.construct(self.processor.metadata_loc, 
                                 self.optimizer.portfolio_performance())

    def optimize_min_volatility(self):
        #self.s = risk_models.sample_cov(self.processor.close_matrix)
        self.optimizer = EfficientFrontier(None, self.s)

        self.optimizer.min_volatility()
        self.portfolio.composition = self.optimizer.clean_weights()
        self.portfolio.construct(self.processor.metadata_loc, 
                                 self.optimizer.portfolio_performance())

class HRPOptimizer:
    def __init__(self, processor=None):
        super().__init__()
        self.processor = processor

        self.processor.process_close()
        self.mu = expected_returns.returns_from_prices(processor.close_matrix)

        self.optimizer = HRPOpt(self.mu)

    def optimize(self):
        self.optimizer.optimize()
        self.portfolio.composition = self.optimizer.clean_weights()
        self.portfolio.construct(self.processor.metadata_loc, 
                                 self.optimizer.portfolio_performance())

class CLAOptimizer:
    def __init__(self, processor=None):
        super().__init__()
        self.processor = processor

        self.processor.process_close()
        self.mu = expected_returns.capm_return(processor.close_matrix)
        #self.s = risk_models.sample_cov(processor.close_matrix)
        self.s = risk_models.CovarianceShrinkage(processor.close_matrix).ledoit_wolf()

        self.optimizer = CLA(self.mu, self.s)

    def optimize_max_sharpe(self):
        self.portfolio.composition = self.optimizer.max_sharpe()
        self.portfolio.construct(self.processor.metadata_loc, 
                                 self.optimizer.portfolio_performance())

    def optimize_min_volatility(self):
        self.portfolio.composition = self.optimizer.min_volatility()
        self.portfolio.construct(self.processor.metadata_loc, 
                                 self.optimizer.portfolio_performance())

class DeepDowOptimizer:
    pass