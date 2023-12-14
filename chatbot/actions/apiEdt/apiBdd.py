from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import select, func
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:bouchra@localhost:5434/EcoleDB'
db = SQLAlchemy(app)


# Définition des modèles de données
class Groupe(db.Model):
    __tablename__ = 'Groupes'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    emploi_du_temps = db.relationship('EmploiDuTemps', backref='groupe', lazy=True)

class Salle(db.Model):
    __tablename__ = 'Salles'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    capacite = db.Column(db.Integer)
    emploi_du_temps = db.relationship('EmploiDuTemps', backref='salle', lazy=True)

class Professeur(db.Model):
    __tablename__ = 'Professeurs'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    emploi_du_temps = db.relationship('EmploiDuTemps', backref='professeur', lazy=True)

class Cours(db.Model):
    __tablename__ = 'cours'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    emploi_du_temps = db.relationship('EmploiDuTemps', backref='cours', lazy=True)

class EmploiDuTemps(db.Model):
    __tablename__ = 'EmploiDuTemps'
    id = db.Column(db.Integer, primary_key=True)
    groupe_id = db.Column(db.Integer, db.ForeignKey('Groupes.id'))
    salle_id = db.Column(db.Integer, db.ForeignKey('Salles.id'))
    professeur_id = db.Column(db.Integer, db.ForeignKey('Professeurs.id'))
    cours_id = db.Column(db.Integer, db.ForeignKey('cours.id'))
    jour = db.Column(db.String(255), nullable=False)
    horaire_debut = db.Column(db.Time, nullable=False)
    horaire_fin = db.Column(db.Time, nullable=False)

@app.route('/salles/libres', methods=['GET'])
def get_salles_libres():
    jour = request.args.get('jour')
    heure_debut = request.args.get('heure_debut')  # Format HH:MM
    heure_fin = request.args.get('heure_fin')  # Format HH:MM

    if not jour or not heure_debut or not heure_fin:
        return jsonify({"error": "Veuillez fournir un jour et une plage horaire."}), 400

    try:
        heure_debut_obj = datetime.strptime(heure_debut + ':00', '%H:%M:%S').time()
        heure_fin_obj = datetime.strptime(heure_fin + ':00', '%H:%M:%S').time()
    except ValueError:
        return jsonify({"error": "Format d'heure invalide. Utilisez HH:MM ou HH:MM:SS."}), 400

    # Création de la sous-requête pour les salles occupées
    salles_occupees_subq = db.session.query(EmploiDuTemps.salle_id).filter(
        func.lower(EmploiDuTemps.jour) == jour.lower(),
        EmploiDuTemps.horaire_debut < heure_fin_obj,
        EmploiDuTemps.horaire_fin > heure_debut_obj
    ).subquery()

    # Requête pour trouver toutes les salles qui ne sont pas dans la sous-requête des salles occupées
    salles_libres = db.session.query(Salle).outerjoin(
        salles_occupees_subq, Salle.id == salles_occupees_subq.c.salle_id
    ).filter(
        salles_occupees_subq.c.salle_id.is_(None)
    ).all()

    if not salles_libres:
        return jsonify({"message": "Aucune salle libre trouvée pour le jour et l'horaire sélectionnés."}), 200

    return jsonify([salle.nom for salle in salles_libres]), 200


@app.route('/cours/par_jour', methods=['GET'])
def get_cours_par_jour():
    jour_souhaite = request.args.get('jour', type=str).capitalize()  # Capitilize pour correspondre à la casse dans la base de données

    # Requête pour obtenir tous les cours du jour spécifié
    cours_du_jour = db.session.query(
        EmploiDuTemps
    ).join(
        Cours, EmploiDuTemps.cours_id == Cours.id
    ).filter(
        EmploiDuTemps.jour == jour_souhaite
    ).all()

    # Vérifie si des cours sont trouvés
    if not cours_du_jour:
        return jsonify({"message": "Aucun cours trouvé pour le jour indiqué."}), 200

    # Formatage de la réponse
    cours_liste = [{
        'cours_id': emploi.cours_id,
        'nom_cours': emploi.cours.nom,
        'professeur': emploi.professeur.nom,
        'salle': emploi.salle.nom,
        'horaire_debut': emploi.horaire_debut.strftime('%H:%M'),
        'horaire_fin': emploi.horaire_fin.strftime('%H:%M')
    } for emploi in cours_du_jour]

    return jsonify(cours_liste), 200




class Professeur(db.Model):
    __tablename__ = 'professeurs'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)

    def as_dict(self):
        return {"id": self.id, "nom": self.nom}

class Salle(db.Model):
    __tablename__ = 'salles'
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)

    def as_dict(self):
        return {"id": self.id, "nom": self.nom}

# Routes pour obtenir des données
@app.route('/professeurs', methods=['GET'])
def get_professeurs():
    profs = Professeur.query.all()
    return jsonify([prof.as_dict() for prof in profs])

@app.route('/salles', methods=['GET'])
def get_salles():
    salles = Salle.query.all()
    return jsonify([salle.as_dict() for salle in salles])

# Lancer l'application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)