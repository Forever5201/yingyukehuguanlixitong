from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(username='admin').first()
    if user:
        user.username = '17844540733'
        user.set_password('yuan971035088')
        db.session.commit()
        print('账号密码修改成功')
    else:
        user = User(username='17844540733')
        user.set_password('yuan971035088')
        db.session.add(user)
        db.session.commit()
        print('新账号创建成功')
