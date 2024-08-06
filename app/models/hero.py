from app import db, app
import json

class Hero(db.Model):
    __tablename__ = 'Heroes'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(25), unique=True, nullable=False)
    attribute = db.Column(db.String(3), nullable=False)
    attack_type = db.Column(db.String(6), nullable=False)
    roles = db.Column(db.String(50))

    def __repr__(self) -> str:
        return f'<object Hero(id: {self.id}, name: {self.name})>'

def fetch_heroes_from_json():
    
    with open('dota_heroes.json', 'r', encoding='utf-8') as heroes_base:
        heroes = json.load(heroes_base)
    
    return heroes
    
def update_db_with_heroes():
    heroes = fetch_heroes_from_json()

    for hero in heroes:
        new_hero = Hero(
                    id=hero['id'],
                    name=hero['localized_name'],
                    attribute=hero['primary_attr'],
                    attack_type=hero['attack_type'],
                    roles=', '.join(hero['roles'])
                )
        db.session.add(new_hero)
    
    db.session.commit()
    app.logger.info("Detected new DB. Dota heroues updated")