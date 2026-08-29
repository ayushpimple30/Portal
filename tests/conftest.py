import pytest
from app import create_app
from app.extensions import db
from app.models import Lesson, Module, Question, User
class TestConfig:
 TESTING=True;SECRET_KEY='test';SQLALCHEMY_DATABASE_URI='sqlite://';SQLALCHEMY_TRACK_MODIFICATIONS=False;WTF_CSRF_ENABLED=False
@pytest.fixture
def app():
 app=create_app(TestConfig)
 with app.app_context():
  db.create_all();m=Module(title='Basics',slug='basics',description='d',content='c',display_order=1);db.session.add(m);db.session.flush();l=Lesson(module_id=m.id,title='Lesson',content='content',display_order=1);q=Question(module_id=m.id,prompt='Safe?',option_a='No',option_b='Yes',option_c='Maybe',option_d='Never',correct_option='B',explanation='Yes',active=True);admin=User(full_name='Admin',email='admin@test.com',role='ADMIN');admin.set_password('Password123');db.session.add_all([l,q,admin]);db.session.commit()
 yield app
 with app.app_context():db.drop_all()
@pytest.fixture
def client(app):return app.test_client()
def login(client,email,password='Password123'):
 return client.post('/auth/login',data={'email':email,'password':password},follow_redirects=True)
