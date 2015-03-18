from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from blazeutils.decorators import memoize

engine = create_engine('sqlite://')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session1 = Session()
session2 = Session()


class MessageKeeper(list):

    def clear(self):
        for i in range(len(self)):
            self.pop()

mk = MessageKeeper()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    addresses = relationship("Address", backref="user")

    @classmethod
    def testing_create(cls):
        user = User(name='hi')
        session1.add(user)

        address = Address(email='foo', user=user)
        session1.add(address)
        address = Address(email='foo', user=user)
        session1.add(address)

        session1.commit()

        return user

    @memoize
    def address_count(self):
        mk.append('ac')
        return len(self.addresses)


event.listen(User, 'expire', User.address_count.reset_memoize)


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    email = Column(String(50))
    user_id = Column(Integer, ForeignKey('users.id'))


def setup_module():
    Base.metadata.create_all(engine)


class TestSAMemoize(object):

    def test_cache_works(self):
        user = User.testing_create()
        assert user.address_count() == 2
        assert mk.pop() == 'ac'

        assert user.address_count() == 2
        assert len(mk) == 0

    def test_cache_resets(self):
        user = User.testing_create()
        assert user.address_count() == 2
        assert mk.pop() == 'ac'

        session1.add(Address(email='foo', user=user))
        print 'committing'
        session1.commit()

        print 'accessing'
        assert user.address_count() == 3
        assert mk.pop() == 'ac'
