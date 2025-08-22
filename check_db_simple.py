from app import create_app, db
from app.models import Course

def main():
    try:
        app = create_app()
        with app.app_context():
            print("Successfully connected to the database!")
            
            # Count trial courses
            count = Course.query.filter_by(is_trial=True).count()
            print(f"Found {count} trial courses in the database.")
            
            # Show first 10 trial courses
            print("\nFirst 10 trial courses:")
            print("ID  | Price  | Status         | Customer")
            print("-" * 50)
            
            for course in Course.query.filter_by(is_trial=True).limit(10).all():
                customer_name = course.customer.name if course.customer else "None"
                print(f"{course.id:3} | {course.trial_price:6.2f} | {course.trial_status or 'N/A':<14} | {customer_name}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
