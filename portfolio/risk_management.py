class RiskManagement:
    """A class to manage risk allocations and strategy distribution based on user's profile."""
    
    # Class-level constants for better maintainability
    TOLERANCE_MAPPING = {
        'low': 0.2,
        'medium': 0.5,
        'high': 0.8
    }
    
    TIME_MAPPING = {
        'long': 0.2,
        'medium': 0.5,
        'short': 0.8
    }
    
    MAX_RISK_SCORE = TOLERANCE_MAPPING['high'] * TIME_MAPPING['short']

    def __init__(self, user_tolerance: str, user_time: str):
        """Initialize with user's risk tolerance and time horizon.
        
        Args:
            user_tolerance: Risk tolerance ('low', 'medium', or 'high')
            user_time: Time horizon ('long', 'medium', or 'short')
        """
        self.user_tolerance = user_tolerance.lower()
        self.user_time = user_time.lower()
        
        # Validate inputs
        self._validate_inputs()
        self._risk_score = self._get_risk_score()  # Calculate risk score at initialization

    def _validate_inputs(self):
        """Validate that inputs are within expected values."""
        if self.user_tolerance not in self.TOLERANCE_MAPPING:
            raise ValueError(f"Invalid risk tolerance. Expected one of: {list(self.TOLERANCE_MAPPING.keys())}")
            
        if self.user_time not in self.TIME_MAPPING:
            raise ValueError(f"Invalid time horizon. Expected one of: {list(self.TIME_MAPPING.keys())}")

    def _get_risk_score(self) -> float:
        """Calculate and return the risk allocation ratio.
        
        Returns:
            float: Risk allocation ratio between 0 and 1
        """
        tol_num = self.TOLERANCE_MAPPING[self.user_tolerance]
        tim_num = self.TIME_MAPPING[self.user_time]
        
        risk_score = (tol_num * tim_num) / self.MAX_RISK_SCORE
        
        # Ensure the result is between 0 and 1
        return max(0.0, min(1.0, risk_score))

    def get_strategy_allocation(self) -> dict:
        """Calculate allocation percentages for each strategy using curved relationships.
        
        Returns:
            dict: {'mean_reversion': x%, 'momentum': y%, 'factor_investing': z%}
        """
        # Strategy weights based on risk score
        mean_rev = self._risk_score * 0.7  # Short-term strategy scales with risk
        momentum = 0.5 - (0.5 - self._risk_score)**2  # Medium-term peaks in middle
        factor_inv = (1 - self._risk_score) * 0.7  # Long-term scales inversely
        
        # Normalize to 100%
        total = mean_rev + momentum + factor_inv
        return {
            'mean_reversion': mean_rev / total,
            'momentum': momentum / total,
            'factor_investing': factor_inv / total
        }

    def get_risk_profile(self) -> dict:
        """Return comprehensive risk profile including score and allocations.
        
        Returns:
            dict: {
                'risk_score': float,
                'allocations_advanced': dict,
                'allocations_simple': dict
            }
        """
        return {
            'risk_score': self._risk_score,
            'allocations_advanced': self.get_strategy_allocation(),
        }