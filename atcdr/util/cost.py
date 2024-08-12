from enum import Enum
from typing import Optional

import tiktoken
import yfinance as yf  # type: ignore


class Model(Enum):
	GPT4O = 'gpt-4o'
	GPT4O_MINI = 'gpt-4o-mini'


class CostType(Enum):
	INPUT = 'input'
	OUTPUT = 'output'


class Currency:
	def __init__(
		self, usd: Optional[float] = None, jpy: Optional[float] = None
	) -> None:
		self._exchange_rate = self.get_exchange_rate()
		self._usd = usd if usd is not None else 0.0
		self._jpy = jpy if jpy is not None else self.convert_usd_to_jpy(self._usd)

	@staticmethod
	def get_exchange_rate() -> float:
		ticker = yf.Ticker('USDJPY=X')
		todays_data = ticker.history(period='1d')
		return todays_data['Close'].iloc[0]

	def convert_usd_to_jpy(self, usd: float) -> float:
		return usd * self._exchange_rate

	def convert_jpy_to_usd(self, jpy: float) -> float:
		return jpy / self._exchange_rate

	@property
	def usd(self) -> float:
		return self._usd

	@usd.setter
	def usd(self, value: float) -> None:
		self._usd = value
		self._jpy = self.convert_usd_to_jpy(value)

	@property
	def jpy(self) -> float:
		return self._jpy

	@jpy.setter
	def jpy(self, value: float) -> None:
		self._jpy = value
		self._usd = self.convert_jpy_to_usd(value)

	def __add__(self, other: 'Currency') -> 'Currency':
		return Currency(usd=self.usd + other.usd)

	def __sub__(self, other: 'Currency') -> 'Currency':
		return Currency(usd=self.usd - other.usd)

	def __mul__(self, factor: float) -> 'Currency':
		return Currency(usd=self.usd * factor)

	def __truediv__(self, factor: float) -> 'Currency':
		return Currency(usd=self.usd / factor)

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Currency):
			return NotImplemented
		epsilon = 1e-9  # 許容範囲
		return abs(self.usd - other.usd) < epsilon

	def __lt__(self, other: 'Currency') -> bool:
		return self.usd < other.usd

	def __repr__(self) -> str:
		return f'Currency(usd={self.usd:.2f}, jpy={self.jpy:.2f})'

	def __str__(self) -> str:
		return f'USD: {self.usd:.2f}, JPY: {self.jpy:.2f}'


class Rate:
	_COST_RATES = {
		Model.GPT4O: {CostType.INPUT: 5 / 1000**2, CostType.OUTPUT: 15 / 1000**2},
		Model.GPT4O_MINI: {
			CostType.INPUT: 0.15 / 1000**2,
			CostType.OUTPUT: 0.60 / 1000**2,
		},
	}

	@staticmethod
	def calc_cost(model: Model, cost_type: CostType, token_count: int) -> Currency:
		cost_in_usd = Rate._COST_RATES[model][cost_type] * token_count
		return Currency(usd=cost_in_usd)


class ApiCostCalculator:
	def __init__(self, text: str, cost_type: CostType, model: Model) -> None:
		self.text = text
		self.cost_type = cost_type
		self.model = model

		# トークンモデルを取得
		self.token_model = tiktoken.encoding_for_model(model.value)

	@property
	def token_count(self) -> int:
		return len(self.token_model.encode(self.text))

	@property
	def cost(self) -> Currency:
		return Rate.calc_cost(self.model, self.cost_type, self.token_count)

	def __str__(self) -> str:
		return f'Token count: {self.token_count}\nCost ({self.cost_type.value}): ${self.cost.usd:.2f} / ¥{self.cost.jpy:.2f}'

	def __repr__(self) -> str:
		return f'ApiCostCalculator(text={self.text}, cost_type={self.cost_type}, model={self.model})'
