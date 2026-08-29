import re
from app.extensions import db
from app.models import Certificate, Lesson, Module, Progress, QuizAttempt, User
from conftest import login

def quiz_payload(client, module, answer):
    page = client.get(f'/learn/modules/{module.slug}/quiz')
    token = re.search(r'name="submission_token" value="([^"]+)"', page.get_data(as_text=True)).group(1)
    return {'submission_token': token, **{f'q_{question.id}': answer for question in module.questions}}

def test_registration_login_and_duplicate(client):
    response = client.post('/auth/register', data={'full_name':'Jane Doe','email':'jane@test.com','password':'Password123','confirm_password':'Password123'}, follow_redirects=True)
    assert b'account is ready' in response.data
    assert b'already exists' in client.post('/auth/register', data={'full_name':'Jane Doe','email':'jane@test.com','password':'Password123','confirm_password':'Password123'}).data
    assert b'Invalid email or password' in client.post('/auth/login', data={'email':'jane@test.com','password':'wrongpass'}, follow_redirects=True).data

def test_progress_and_quiz_persistence(client, app):
    with app.app_context():
        user=User(full_name='Jane',email='jane@test.com'); user.set_password('Password123'); db.session.add(user); db.session.commit(); lesson=Lesson.query.first(); module=Module.query.first(); question=module.questions[0]
    login(client,'jane@test.com')
    client.post(f'/learn/lessons/{lesson.id}/complete'); client.post(f'/learn/lessons/{lesson.id}/complete')
    with app.app_context(): assert Progress.query.count() == 1
    response=client.post(f'/learn/modules/{module.slug}/quiz',data=quiz_payload(client,module,question.correct_option),follow_redirects=True)
    assert b'100.0%' in response.data
    with app.app_context(): assert QuizAttempt.query.one().passed and QuizAttempt.query.one().duration_seconds >= 0

def test_result_ownership_and_duplicate_submission(client, app):
    with app.app_context():
        first=User(full_name='First',email='first@test.com');first.set_password('Password123');second=User(full_name='Second',email='second@test.com');second.set_password('Password123');db.session.add_all([first,second]);db.session.commit();module=Module.query.first();question=module.questions[0]
    login(client,'first@test.com'); payload=quiz_payload(client,module,question.correct_option); client.post(f'/learn/modules/{module.slug}/quiz',data=payload)
    with app.app_context(): attempt_id=QuizAttempt.query.one().id
    assert client.post(f'/learn/modules/{module.slug}/quiz',data=payload,follow_redirects=True).status_code == 200
    client.post('/auth/logout'); login(client,'second@test.com'); assert client.get(f'/learn/results/{attempt_id}').status_code == 403

def test_certificate_verification_and_admin_access(client, app):
    with app.app_context():
        user=User(full_name='Certified',email='cert@test.com');user.set_password('Password123');db.session.add(user);db.session.flush();certificate=Certificate(user_id=user.id,certificate_code='NETWISE-TEST');db.session.add(certificate);db.session.commit()
    assert client.get('/verify/NETWISE-TEST').status_code == 200
    assert client.get('/verify/unknown-code').status_code == 404
    login(client,'admin@test.com'); assert client.get('/admin/').status_code == 200
