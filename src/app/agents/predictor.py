from enum import Enum
from pydantic import BaseModel, Field
from app.api.base.markets import ProductInfo


class PredictorStyle(Enum):
    CONSERVATIVE = "Conservativo"
    AGGRESSIVE = "Aggressivo"

class PredictorInput(BaseModel):
    data: list[ProductInfo] = Field(..., description="Market data as a list of ProductInfo")
    style: PredictorStyle = Field(..., description="Prediction style")
    sentiment: str = Field(..., description="Aggregated sentiment from news and social analysis")

class ItemPortfolio(BaseModel):
    asset: str = Field(..., description="Name of the asset")
    percentage: float = Field(..., description="Percentage allocation to the asset")
    motivation: str = Field(..., description="Motivation for the allocation")

class PredictorOutput(BaseModel):
    strategy: str = Field(..., description="Concise operational strategy in Italian")
    portfolio: list[ItemPortfolio] = Field(..., description="List of portfolio items with allocations")
