import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from eventanalyzer.models import Base, User, UserCreate
from eventanalyzer.repository import UserRepository


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def user_repo(db_session):
    return UserRepository(db_session)


def test_create_user(user_repo):
    user_data = UserCreate(telegram_id=123456789)
    user = user_repo.create(user_data)
    
    assert user.id is not None
    assert user.telegram_id == 123456789
    assert user.language == "en"
    assert user.custom_instruction is None
    assert user.created_at is not None


def test_get_by_telegram_id(user_repo):
    user_data = UserCreate(telegram_id=987654321)
    created_user = user_repo.create(user_data)
    
    found_user = user_repo.get_by_telegram_id(987654321)
    assert found_user is not None
    assert found_user.id == created_user.id


def test_get_or_create_existing(user_repo):
    user_data = UserCreate(telegram_id=111222333)
    created_user = user_repo.create(user_data)
    
    user = user_repo.get_or_create(111222333)
    assert user.id == created_user.id


def test_get_or_create_new(user_repo):
    user = user_repo.get_or_create(444555666)
    assert user.id is not None
    assert user.telegram_id == 444555666
    assert user.language == "en"


def test_update_language(user_repo):
    user_data = UserCreate(telegram_id=555666777)
    created_user = user_repo.create(user_data)
    
    updated_user = user_repo.update_language(555666777, "ru")
    assert updated_user.language == "ru" 