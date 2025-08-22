from flask import Flask, jsonify
from app import create_app, db
from app.models import Course

app = create_app()

@app.route('/check-trial-prices')
def check_trial_prices():
    with app.app_context():
        try:
            # Get all trial courses
            trial_courses = Course.query.filter_by(is_trial=True).all()
            
            # Check for any price not equal to 39.90
            incorrect_prices = [
                {'id': c.id, 'current_price': c.trial_price, 'status': c.trial_status}
                for c in trial_courses if c.trial_price != 39.90
            ]
            
            if incorrect_prices:
                # Update incorrect prices
                for course in trial_courses:
                    if course.trial_price != 39.90:
                        course.trial_price = 39.90
                db.session.commit()
                
                return jsonify({
                    'status': 'fixed',
                    'message': f'Updated {len(incorrect_prices)} courses to 39.90',
                    'updated_courses': incorrect_prices
                })
            else:
                return jsonify({
                    'status': 'ok',
                    'message': 'All trial courses are correctly priced at 39.90',
                    'total_courses': len(trial_courses)
                })
                
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500

if __name__ == '__main__':
    app.run(debug=True)
