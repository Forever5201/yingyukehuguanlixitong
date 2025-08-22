from app import create_app, db
from app.models import Course

def update_trial_prices():
    app = create_app()
    with app.app_context():
        try:
            # Get all trial courses
            trial_courses = Course.query.filter_by(is_trial=True).all()
            
            print(f"Found {len(trial_courses)} trial courses")
            
            # Update each trial course price to 39.90
            for course in trial_courses:
                print(f"Updating course ID {course.id}: price from {course.trial_price} to 39.90")
                course.trial_price = 39.90
            
            # Commit the changes
            db.session.commit()
            print("Successfully updated all trial course prices to 39.90")
            
        except Exception as e:
            print(f"Error updating trial prices: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    update_trial_prices()
