import os
from sqlalchemy import create_engine, String, Float, CheckConstraint
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session, Mapped, mapped_column
from dotenv import load_dotenv
from fastapi import  Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL","postgresql://usuario:senha@localhost:5432/nome_do_banco")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db  = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProdutoBase(Base):
    __tablename__ = "Produtos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    preco: Mapped[float] = mapped_column(Float,CheckConstraint("preco > 0", name="check_preco_positivo") ,nullable=False)
    estoque: Mapped[int] = mapped_column(default=0)
    ativo: Mapped[bool] = mapped_column(default=True)

class ProdutoCreate(BaseModel):
    nome: str = Field(...,  min_length=1)
    preco: float = Field(..., gt=0)
    estoque: int = Field(default=0, ge=0)
    ativo: bool = Field(default=True)

class ProdutoResponse(ProdutoCreate):
    id: int

    model_config = {"from_attributes": True}

app = FastAPI(title="E-commerce")

@app.get("/produtos", response_model=list[ProdutoResponse], status_code=status.HTTP_200_OK)
def get_produtos(db: Session =  Depends(get_db)) -> list[ProdutoBase]:
    return db.query(ProdutoBase).all()

@app.get("/produtos/{produto_id}",response_model=ProdutoResponse,status_code=status.HTTP_200_OK)
def search_produto(produto_id:  int,  db: Session =  Depends(get_db)) -> ProdutoBase:
    produto = db.query(ProdutoBase).filter(ProdutoBase.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    return produto
@app.post("/produtos", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def create_produto(produtoC: ProdutoCreate, db: Session =  Depends(get_db))-> ProdutoBase:
    produto =  ProdutoBase(**produtoC.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto

@app.delete("/produtos/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_produtos(produto_id: int, db: Session =  Depends(get_db)) -> None:
    produto =  db.query(ProdutoBase).filter(ProdutoBase.id ==  produto_id).first()
    if not produto: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    db.delete(produto)
    db.commit()
    return None

@app.put("/produtos/{produto_id}", response_model=ProdutoResponse, status_code=status.HTTP_200_OK)
def atualizar_produto(produto_id: int, produtoC: ProdutoCreate, db: Session = Depends(get_db)) -> ProdutoBase:
    produto = db.query(ProdutoBase).filter(ProdutoBase.id == produto_id).first()
    if not produto: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produto não encontrado")
    dados_atualizados = produtoC.model_dump()
    for key, value in dados_atualizados.items():
        setattr(produto, key, value)
    db.commit()
    db.refresh(produto)
    return produto