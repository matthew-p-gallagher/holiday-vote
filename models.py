from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Traveler(db.Model):
    """Model for travelers who can vote"""
    __tablename__ = 'travelers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    has_voted = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f'<Traveler {self.name}>'


class Holiday(db.Model):
    """Model for holiday options"""
    __tablename__ = 'holidays'

    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(100), nullable=False, unique=True)
    by = db.Column(db.String(100), nullable=False, unique=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)


    def __repr__(self):
        return f'<Holiday {self.destination}>'

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'destination': self.destination,
            'by': self.by,
            'latitude': self.latitude,
            'longitude': self.longitude
        }


class Vote(db.Model):
    """Model for storing votes"""
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    voter_name = db.Column(db.String(100), nullable=False, unique=True)
    first_choice = db.Column(db.String(100), nullable=False)
    second_choice = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Vote by {self.voter_name}>'


def init_db():
    """Initialize database and populate with default holiday options and travelers"""
    db.create_all()

    # Check if travelers already exist
    if Traveler.query.count() == 0:
        # Create 14 default travelers
        default_travelers = [Traveler(name=f'{n}') for n in [
            'Amy', 'Matt McP', 'Finni', 'Jack Marsh', 'Gabbie', 'Chiz', 'Will', 'Katie', 'Jack Houst', 'Kirsty', 'Sophie', 'Matt Gall', 'Laura', 'Finlay'
            ]]

        for traveler in default_travelers:
            db.session.add(traveler)

        db.session.commit()
        print("Database initialized with 14 travelers!")

    # Check if holidays already exist
    if Holiday.query.count() == 0:
        # Default 5 holiday ideas with coordinates
        default_holidays = [
            Holiday(destination='Leucate', by='Will', latitude=42.9114, longitude=3.0296),
            Holiday(destination='Lake Garda', by='Kirsty', latitude=45.4906, longitude=10.6067),
            Holiday(destination='Porto', by='Amy', latitude=41.1579, longitude=-8.6291),
            Holiday(destination='Marrakesh', by='Gabbie', latitude=31.6295, longitude=-7.9811),
        ]

        for holiday in default_holidays:
            db.session.add(holiday)

        db.session.commit()
        print("Database initialized with holiday options!")


def get_results():
    """Calculate and return voting results with scores"""
    holidays = Holiday.query.all()
    results = {}

    for holiday in holidays:
        results[holiday.destination] = {
            'destination': holiday.destination,
            'by': holiday.by,
            'first_choice_votes': 0,
            'second_choice_votes': 0,
            'total_score': 0
        }

    # Count votes
    votes = Vote.query.all()
    for vote in votes:
        if vote.first_choice in results:
            results[vote.first_choice]['first_choice_votes'] += 1
            results[vote.first_choice]['total_score'] += 2  # 2 points for first choice

        if vote.second_choice in results:
            results[vote.second_choice]['second_choice_votes'] += 1
            results[vote.second_choice]['total_score'] += 1  # 1 point for second choice

    # Sort by total score (descending)
    sorted_results = sorted(results.values(), key=lambda x: x['total_score'], reverse=True)

    return sorted_results, len(votes)


def mark_traveler_voted(traveler_name):
    """Mark a traveler as having voted"""
    traveler = Traveler.query.filter_by(name=traveler_name).first()
    if traveler:
        traveler.has_voted = True
        db.session.commit()
        return True
    return False
