from app import create_app, db

def update_trial_prices():
    app = create_app()
    with app.app_context():
        try:
            # Direct SQL update
            result = db.session.execute(
                "UPDATE course SET trial_price = 39.90 WHERE is_trial = 1"
            )
            db.session.commit()
            print(f"Updated {result.rowcount} trial course prices to 39.90")
            
            # Verify the update
            from app.models import Course
            updated = Course.query.filter_by(is_trial=True, trial_price=39.90).count()
            total = Course.query.filter_by(is_trial=True).count()
            print(f"Verified: {updated} out of {total} trial courses updated to 39.90")
            
        except Exception as e:
            print(f"Error updating prices: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    update_trial_prices()
