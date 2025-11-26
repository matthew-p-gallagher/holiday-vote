from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, Vote, Holiday, Traveler, init_db, get_results, mark_traveler_voted

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///votes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

with app.app_context():
    init_db()

@app.route('/')
def index():
    """Display voting form"""
    holidays = Holiday.query.all()
    # Only show travelers who haven't voted yet
    travelers = Traveler.query.filter_by(has_voted=False).order_by(Traveler.name).all()
    return render_template('index.html', holidays=holidays, travelers=travelers)

@app.route('/vote', methods=['POST'])
def vote():
    """Handle vote submission"""
    voter_name = request.form.get('voter_name', '').strip()
    first_choice = request.form.get('first_choice')
    second_choice = request.form.get('second_choice')

    # Validate inputs
    if not voter_name or not first_choice or not second_choice:
        holidays = Holiday.query.all()
        travelers = Traveler.query.filter_by(has_voted=False).order_by(Traveler.name).all()
        return render_template('index.html', holidays=holidays, travelers=travelers,
                             error='Please fill in all fields!')

    # Check if traveler exists
    traveler = Traveler.query.filter_by(name=voter_name).first()
    if not traveler:
        holidays = Holiday.query.all()
        travelers = Traveler.query.filter_by(has_voted=False).order_by(Traveler.name).all()
        return render_template('index.html', holidays=holidays, travelers=travelers,
                             error='Invalid traveler selected!')

    # Check if traveler has already voted
    if traveler.has_voted:
        holidays = Holiday.query.all()
        travelers = Traveler.query.filter_by(has_voted=False).order_by(Traveler.name).all()
        return render_template('index.html', holidays=holidays, travelers=travelers,
                             error=f'{voter_name} has already voted!')

    # Create and save the vote
    new_vote = Vote(
        voter_name=voter_name,
        first_choice=first_choice,
        second_choice=second_choice
    )

    db.session.add(new_vote)
    db.session.commit()

    # Mark traveler as voted
    mark_traveler_voted(voter_name)

    # Get total vote count
    total_votes = Vote.query.count()

    return render_template('success.html', voter_name=voter_name, total_votes=total_votes)

@app.route('/results')
def results():
    """Display voting results"""
    results_data, total_votes = get_results()
    return render_template('results.html', results=results_data,
                         total_votes=total_votes, max_votes=14)

@app.route('/api/holidays')
def api_holidays():
    """API endpoint to get all holidays with coordinates for map"""
    holidays = Holiday.query.all()
    return jsonify([holiday.to_dict() for holiday in holidays])

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
