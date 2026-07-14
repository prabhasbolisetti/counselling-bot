from typing import Literal

from pydantic import BaseModel, Field


class PredictorRequest(BaseModel):
    rank: int = Field(..., gt=0, description="AP EAPCET Rank")

    category: Literal[
        "OC",
        "OC_EWS",
        "BCA",
        "BCB",
        "BCC",
        "BCD",
        "BCE",
        "SC",
        "ST",
    ]

    gender: Literal["BOYS", "GIRLS"]