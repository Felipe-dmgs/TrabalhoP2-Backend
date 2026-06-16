import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db, Base

DATABASE_TEST_URL = os.getenv("DATABASE_TEST_URL","postgresql://usuario:secret@banco-test:5432/banco_teste")

engine_test = create_engine(DATABASE_TEST_URL) #cria a  engine
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def db_engine():#Roda antes de todos os testes,  criando a estrutura de tabelas, setando a secao e apagando tudo ao fim
    Base.metadata.create_all(bind=engine_test)#Cria as tabelas limpas no banco
    yield engine_test #engine_test
    Base.metadata.drop_all(bind=engine_test)#Derruba as tabelas após o término  de todos os testes

@pytest.fixture
def db_session(db_engine):#O  db_engine cria uma  secao para os testes o db_session cria uma secao para cada teste
    connection=db_engine.connect()#Funcao do engine_test
    transaction= connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db_session):#Substitui a dependencia do banco dev pelo banco test
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass
    app.dependency_overrides[get_db] = _get_test_db #Quando a api for chamar o get_db substitui pelo _get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()#Removo a substituicao
