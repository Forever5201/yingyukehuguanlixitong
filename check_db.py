from app import create_app, db
from app.models import Course

def check_trial_courses():
    app = create_app()
    with app.app_context():
        try:
            # Get all trial courses
            trial_courses = Course.query.filter_by(is_trial=True).all()
            
            if not trial_courses:
                print("No trial courses found in the database.")
                return
                
            print(f"Found {len(trial_courses)} trial courses:")
            print("-" * 60)
            print(f"{'ID':<5} | {'Price':<10} | {'Status':<15} | Customer")
            print("-" * 60)
            
            for course in trial_courses:
                customer_name = course.customer.name if course.customer else "No customer"
                print(f"{course.id:<5} | {course.trial_price:<10} | {course.trial_status or 'N/A':<15} | {customer_name}")
            
            # Calculate total revenue
            total_revenue = sum(c.trial_price for c in trial_courses if c.trial_status != 'refunded' and c.trial_status != 'not_registered')
            print("\nCalculated total revenue (excluding refunded/not_registered):", total_revenue)
            
        except Exception as e:
            print(f"Error accessing database: {str(e)}")

if __name__ == "__main__":
    check_trial_courses()
