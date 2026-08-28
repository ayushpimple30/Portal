from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Module, Progress, QuizAttempt

def admin_required(view):
 @wraps(view)
 def wrapped(*args,**kwargs):
  if not current_user.is_authenticated: return abort(403)
  if not current_user.is_admin: return abort(403)
  return view(*args,**kwargs)
 return wrapped
def completion(user):
 lessons=sum(len(m.lessons) for m in Module.query.filter_by(published=True).all())
 done=Progress.query.filter_by(user_id=user.id).count()
 return (done, lessons, round(done/lessons*100) if lessons else 0)
def eligible(user):
 modules=Module.query.filter_by(published=True).all()
 return bool(modules) and all(all(Progress.query.filter_by(user_id=user.id,lesson_id=l.id).first() for l in m.lessons) and QuizAttempt.query.filter_by(user_id=user.id,module_id=m.id,passed=True).first() for m in modules)
