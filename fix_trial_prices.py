from app import create_app, db
from app.models import Course
import sys

def update_trial_prices():
    try:
        app = create_app()
        with app.app_context():
            print("Connected to database successfully")
            
            # Get all trial courses
            trial_courses = Course.query.filter_by(is_trial=True).all()
            print(f"Found {len(trial_courses)} trial courses")
            
            if not trial_courses:
                print("No trial courses found. Please check your database connection.")
                return
                
            for course in trial_courses:
                print(f"Course ID: {course.id}, Current Price: {course.trial_price}, Status: {course.trial_status}")
                course.trial_price = 39.90
            
            db.session.commit()
            print("\nSuccessfully updated all trial course prices to 39.90")
            
            # Verify the updates
            updated = Course.query.filter_by(is_trial=True, trial_price=39.90).count()
            print(f"Verified: {updated} courses now have price 39.90")
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        if 'db' in locals():
            db.session.rollback()

if __name__ == "__main__":
    update_trial_prices()
