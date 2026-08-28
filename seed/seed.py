from app import create_app
from app.extensions import db
from app.models import Lesson, Module, Question, User
DATA=[('Internet Basics','internet-basics','Understand how networks, websites and connections work.'),('Web Browsers','web-browsers','Navigate browser tools safely and efficiently.'),('Search Engines & Google Search','search-engines','Find reliable information with effective search habits.'),('Email','email','Communicate clearly and identify risky messages.'),('Passwords & Privacy','passwords-privacy','Protect accounts and personal information.'),('Cybersecurity & Online Safety','cybersecurity-safety','Recognise scams, malware and unsafe online behaviour.')]
app=create_app()
with app.app_context():
 db.create_all()
 if not User.query.filter_by(email='admin@netwise.local').first():
  admin=User(full_name='NetWise Administrator',email='admin@netwise.local',role='ADMIN');admin.set_password('ChangeMe123!');student=User(full_name='Sample Student',email='student@netwise.local');student.set_password('Student123!');db.session.add_all([admin,student])
 for index,(title,slug,description) in enumerate(DATA,1):
  module=Module.query.filter_by(slug=slug).first()
  if not module:
   module=Module(title=title,slug=slug,description=description,content=f'<p>{description}</p>',estimated_minutes=25,display_order=index,published=True);db.session.add(module);db.session.flush()
   for order,topic in enumerate(['Core concepts','Practical everyday use','Safety checklist'],1): db.session.add(Lesson(module_id=module.id,title=f'{topic}: {title}',content=f'<p>This lesson introduces {topic.lower()} for {title}. Learn one practical action, check the source or setting carefully, and pause before sharing information online.</p>',key_points='Use clear, trusted sources. Check details before acting.',safety_tip='Do not share passwords, one-time codes, or sensitive personal information.',display_order=order))
   for n in range(1,11): db.session.add(Question(module_id=module.id,prompt=f'For {title}, which is the safest first step in situation {n}?',option_a='Act immediately without checking',option_b='Verify the source and review the details',option_c='Share personal information to continue',option_d='Ignore all security guidance',correct_option='B',explanation='Pausing to verify the source and details is a dependable online safety habit.',difficulty='Beginner',active=True))
 db.session.commit();print('Seed complete.')
