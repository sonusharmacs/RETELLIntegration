from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Integer, String
import sqlalchemy
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel, ConfigDict

app = FastAPI()

DB_URL = "sqlite:///./test.db"
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = sqlalchemy.orm.declarative_base()


class Item(Base):
    __tablename__ = "items"

    id = sqlalchemy.Column(Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(String, index=True)
    description = sqlalchemy.Column(String, index=True)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ItemCreate(BaseModel):
    name: str
    description: str


class ItemResponse(BaseModel):
    id: int
    name: str
    description: str

    model_config = ConfigDict(from_attributes=True)


@app.post("/items", response_model=ItemResponse)
@app.post("/items/", response_model=ItemResponse, include_in_schema=False)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@app.get("/items/{item_id}", response_model=ItemResponse)
async def read_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item


@app.get("/items", response_model=list[ItemResponse])
@app.get("/items/", response_model=list[ItemResponse], include_in_schema=False)
async def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(Item).offset(skip).limit(limit).all()
    return items

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)