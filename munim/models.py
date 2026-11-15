from pydantic import BaseModel, ConfigDict, Field

class Strict(BaseModel):
    model_config = ConfigDict(strict=True, extra='forbid', frozen=True)

class Item(Strict):
    id: str
    name: str
    category: str
    cost: int = Field(gt=0)
    list_price: int = Field(gt=0)
    stock: int = Field(ge=0)

class Line(Strict):
    item: str
    qty: int = Field(gt=0)
    unit_price: int = Field(gt=0)

class Offer(Strict):
    lines: tuple[Line, ...]
    total: int = Field(ge=0)

class Move(Strict):
    kind: str
    offer: Offer | None = None
    final: bool = False
    hint: str = ''

class Commitment(Strict):
    needs: dict[str, int] = Field(default_factory=dict)
    counter: int | None = None
    accept: bool = False

class State(Strict):
    round: int
    commitment: Commitment
    previous: Offer | None = None
    previous_needs: dict[str, int] = Field(default_factory=dict)

