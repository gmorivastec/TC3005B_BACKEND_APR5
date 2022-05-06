from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session

from sqlalchemy import create_engine
from sqlalchemy import select

Base = declarative_base()

# intención de ORM 
# mappear renglones de una DB a objetos
class Usuario(Base):
    # agregamos los campos donde se mapearan las columnas de la db
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(150))
    PASSWORD = Column(String(100))
    token = Column(String(100))
    last_date = Column(Integer)

# objeto engine para la conexión
#  PARA POSTGRE: 'postgresql://scott:tiger@localhost:5432/mydatabase'
engine = create_engine('ibm_db_sa://db2inst1:hola@localhost:50000/testdb')
session = Session(engine)

# creación de nuevo registro 
nuevoUsuario = Usuario(
    email="ejemplo@ejemplo.com",
    PASSWORD="UN PASSWORDCITO",
    token="SOY UN TOKEN MUY SEGURO",
    last_date=10
)

session.add_all([nuevoUsuario])
session.commit()

#hacer query
#stmt = select(Usuario).where(Usuario.email.in_(["a@a.com"]))
stmt = select(Usuario)
for user in session.scalars(stmt):
    print(user.email)
    print(user.PASSWORD)
    print(user.token)



