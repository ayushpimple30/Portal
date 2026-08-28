from app.extensions import db
from app.models import Lesson, Module, Progress, QuizAttempt, User
from conftest import login
def test_register_and_duplicate(client):
 r=client.post('/auth/register',data={'full_name':'Jane Doe','email':'jane@test.com','password':'Password123','confirm_password':'Password123'},follow_redirects=True);assert b'account is ready' in r.data
 r=client.post('/auth/register',data={'full_name':'Jane Doe','email':'jane@test.com','password':'Password123','confirm_password':'Password123'});assert b'already exists' in r.data
def test_unauthorized_and_student_flow(client,app):
 assert client.get('/learn/dashboard').status_code==302
 with app.app_context():u=User(full_name='Jane',email='jane@test.com');u.set_password('Password123');db.session.add(u);db.session.commit();lesson=Lesson.query.first();module=Module.query.first()
 login(client,'jane@test.com');assert client.get('/learn/dashboard').status_code==200
 client.post(f'/learn/lessons/{lesson.id}/complete');
 with app.app_context():assert Progress.query.count()==1
 r=client.post('/learn/modules/basics/quiz',data={f'q_{module.questions[0].id}':'B'},follow_redirects=True);assert b'100.0%' in r.data
 with app.app_context():assert QuizAttempt.query.first().passed
def test_admin_access_and_module_crud(client):
 assert client.get('/admin/').status_code==302
 login(client,'admin@test.com');assert client.get('/admin/').status_code==200
 r=client.post('/admin/modules/new',data={'title':'New','slug':'new','description':'d','content':'c','estimated_minutes':10,'display_order':2,'published':'y'},follow_redirects=True);assert b'Module saved' in r.data
def test_contact_and_feedback(client,app):
 assert b'valid email' in client.post('/contact',data={'name':'N','email':'x','subject':'S','message':'M'}).data
 with app.app_context():u=User(full_name='Jane',email='jane@test.com');u.set_password('Password123');db.session.add(u);db.session.commit()
 login(client,'jane@test.com');r=client.post('/learn/feedback',data={'rating':5,'message':'Helpful'},follow_redirects=True);assert b'Feedback received' in r.data
