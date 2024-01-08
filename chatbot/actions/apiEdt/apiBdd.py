from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
from sqlalchemy.orm import aliased
from datetime import datetime, time, timedelta



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://sebastien:@localhost:5432/edt'
db = SQLAlchemy(app)

# Models
class Matiere(db.Model):
    __tablename__ = 'matieres'
    id_matiere = db.Column(db.Integer, primary_key=True)
    nom_matiere = db.Column(db.String(255), nullable=False)
    cours = db.relationship('Cours', backref='matiere', lazy='dynamic')

class Professeur(db.Model):
    __tablename__ = 'professeurs'
    id_prof = db.Column(db.Integer, primary_key=True)
    nom_prof = db.Column(db.String(255), nullable=False)
    cours = db.relationship('Cours', backref='professeur', lazy='dynamic')

class Salle(db.Model):
    __tablename__ = 'salles'
    id_salle = db.Column(db.Integer, primary_key=True)
    nom_salle = db.Column(db.String(255), nullable=False)
    cours = db.relationship('Cours', backref='salle', lazy='dynamic')

class Cours(db.Model):
    __tablename__ = 'cours'
    id_cours = db.Column(db.Integer, primary_key=True)
    id_matiere = db.Column(db.Integer, db.ForeignKey('matieres.id_matiere'))
    id_prof = db.Column(db.Integer, db.ForeignKey('professeurs.id_prof'))
    id_salle = db.Column(db.Integer, db.ForeignKey('salles.id_salle'))
    emplois_du_temps = db.relationship('EmploiDuTemps', backref='cours', lazy='dynamic')

class Jour(db.Model):
    __tablename__ = 'jours'
    id_jour = db.Column(db.Integer, primary_key=True)
    nom_jour = db.Column(db.String(255), nullable=False)
    emplois_du_temps = db.relationship('EmploiDuTemps', backref='jour', lazy='dynamic')

class Horaire(db.Model):
    __tablename__ = 'horaires'
    id_horaire = db.Column(db.Integer, primary_key=True)
    heure_debut = db.Column(db.Time, nullable=False)
    heure_fin = db.Column(db.Time, nullable=False)
    emplois_du_temps = db.relationship('EmploiDuTemps', backref='horaire', lazy='dynamic')

class Groupe(db.Model):
    __tablename__ = 'groupes'
    id_groupe = db.Column(db.Integer, primary_key=True)
    nom_groupe = db.Column(db.String(255), nullable=False)
    emplois_du_temps = db.relationship('EmploiDuTemps', backref='groupe', lazy='dynamic')

class EmploiDuTemps(db.Model):
    __tablename__ = 'emploidutemps'
    id_emploi = db.Column(db.Integer, primary_key=True)
    id_groupe = db.Column(db.Integer, db.ForeignKey('groupes.id_groupe'))
    id_jour = db.Column(db.Integer, db.ForeignKey('jours.id_jour'))
    id_horaire = db.Column(db.Integer, db.ForeignKey('horaires.id_horaire'))
    id_cours = db.Column(db.Integer, db.ForeignKey('cours.id_cours'))

# Routes Flask
@app.route('/cours/jour', methods=['GET'])
def emploidutemps_par_jour():
    jour = request.args.get('jour', type=str)
    groupe = request.args.get('groupe', type=int)

    if not jour or groupe is None:
        return jsonify({"error": "Les paramètres 'jour' et 'groupe' sont requis."}), 400

    edt = aliased(EmploiDuTemps)

    emploidutemps = db.session.query(
        Matiere.nom_matiere,  
        Horaire.heure_debut, 
        Horaire.heure_fin,    
        Salle.nom_salle      
    ).select_from(edt).join(
        Cours, Cours.id_cours == edt.id_cours
    ).join(
        Matiere, Matiere.id_matiere == Cours.id_matiere
    ).join(
        Salle, Salle.id_salle == Cours.id_salle  # Joindre la table Salle
    ).join(
        Jour, Jour.id_jour == edt.id_jour
    ).join(
        Horaire, Horaire.id_horaire == edt.id_horaire
    ).filter(
        func.lower(Jour.nom_jour) == jour.lower(),
        edt.id_groupe == groupe
    ).all()

    return jsonify([
        {
            "nom_matiere": nom_matiere,
            "heure_debut": heure_debut.strftime("%H:%M"),
            "heure_fin": heure_fin.strftime("%H:%M"),
            "salle": nom_salle
        } for nom_matiere, heure_debut, heure_fin, nom_salle in emploidutemps
    ])

@app.route('/cours/premier-horaire', methods=['GET'])
def get_premier_horaire_cours_jour():
    jour = request.args.get('jour')
    if not jour:
        return jsonify({"error": "Le paramètre 'jour' est requis."}), 400

    premier_cours = db.session.query(EmploiDuTemps.id_horaire)\
        .join(Jour, Jour.id == EmploiDuTemps.id_jour)\
        .filter(func.lower(Jour.nom_jour) == jour.lower())\
        .order_by(EmploiDuTemps.id_horaire)\
        .first()

    if premier_cours:
        return jsonify({"horaire_debut_premier_cours": premier_cours.id_horaire})
    else:
        return jsonify({"message": "Pas de cours pour ce jour."})



@app.route('/nbr-cours/jour', methods=['GET'])
def nombre_cours_par_jour():
    jour = request.args.get('jour', type=str)
    groupe = request.args.get('groupe', type=int)

    if not jour or groupe is None:
        return jsonify({"error": "Les paramètres 'jour' et 'groupe' sont requis."}), 400

    nombre_cours = db.session.query(func.count(EmploiDuTemps.id_emploi)).join(
        Jour, Jour.id_jour == EmploiDuTemps.id_jour
    ).filter(
        func.lower(Jour.nom_jour) == jour.lower(),
        EmploiDuTemps.id_groupe == groupe
    ).scalar()  

    return jsonify({
        "jour": jour,
        "groupe": groupe,
        "nombre_cours": nombre_cours
    })


@app.route('/salle-cours', methods=['GET'])
def salle_pour_cours_par_nom_et_jour():
    jour_nom = request.args.get('jour', type=str)
    groupe_id = request.args.get('groupe', type=int)
    nom_cours = request.args.get('nom_cours', type=str)

    if not jour_nom or not groupe_id or not nom_cours:
        return jsonify({"error": "Les paramètres 'jour', 'groupe', et 'nom_cours' sont requis."}), 400

    salle_cours = db.session.query(
        Salle.nom_salle
    ).join(
        Cours, Cours.id_salle == Salle.id_salle
    ).join(
        EmploiDuTemps, EmploiDuTemps.id_cours == Cours.id_cours
    ).join(
        Jour, Jour.id_jour == EmploiDuTemps.id_jour
    ).join(
        Matiere, Matiere.id_matiere == Cours.id_matiere
    ).filter(
        func.lower(Jour.nom_jour) == jour_nom.lower(),
        EmploiDuTemps.id_groupe == groupe_id,
        func.lower(Matiere.nom_matiere) == nom_cours.lower()
    ).first()

    if salle_cours:
        return jsonify({
            "jour": jour_nom,
            "groupe": groupe_id,
            "nom_cours": nom_cours,
            "salle": salle_cours.nom_salle
        })
    else:
        return jsonify({"message": "Aucune salle trouvée pour ce nom de cours ou ce jour."})


@app.route('/heure-fin/jour', methods=['GET'])
def heure_fin_cours_par_jour():
    jour = request.args.get('jour', type=str)
    groupe = request.args.get('groupe', type=int)

    if not jour or groupe is None:
        return jsonify({"error": "Les paramètres 'jour' et 'groupe' sont requis."}), 400

    # Trouver l'heure de fin du dernier cours pour le jour et le groupe donnés
    dernier_cours = db.session.query(
        Horaire.heure_fin
    ).join(
        EmploiDuTemps, Horaire.id_horaire == EmploiDuTemps.id_horaire
    ).join(
        Jour, Jour.id_jour == EmploiDuTemps.id_jour
    ).filter(
        func.lower(Jour.nom_jour) == jour.lower(),
        EmploiDuTemps.id_groupe == groupe
    ).order_by(
        Horaire.heure_fin.desc()
    ).first()

    if dernier_cours:
        heure_fin = dernier_cours.heure_fin.strftime("%H:%M")
        return jsonify({"jour": jour, "groupe": groupe, "heure_fin": heure_fin})
    else:
        return jsonify({"message": "Aucun cours trouvé pour ce jour ou groupe."})



@app.route('/salles-libres', methods=['GET'])
def salles_libres_horaires_par_jour():
    jour_nom = request.args.get('jour', type=str)
    
    if not jour_nom:
        return jsonify({"error": "Le paramètre 'jour' est requis."}), 400

    # Define the working hours
    working_hours_start = datetime.combine(datetime.today(), time(8, 30))
    working_hours_end = datetime.combine(datetime.today(), time(19, 0))

    # Generate time slots for the day within working hours
    time_slots = []
    while working_hours_start < working_hours_end:
        end_time = (working_hours_start + timedelta(minutes=30)).time()
        time_slots.append((working_hours_start.time(), end_time))
        working_hours_start += timedelta(minutes=30)

    jour_id = db.session.query(Jour.id_jour).filter(func.lower(Jour.nom_jour) == jour_nom.lower()).scalar()
    if jour_id is None:
        return jsonify({"error": "Le jour spécifié n'existe pas."}), 404

    occupied_slots = db.session.query(
        Cours.id_salle, Horaire.heure_debut, Horaire.heure_fin
    ).join(EmploiDuTemps, EmploiDuTemps.id_cours == Cours.id_cours
    ).join(Horaire, Horaire.id_horaire == EmploiDuTemps.id_horaire
    ).filter(EmploiDuTemps.id_jour == jour_id).all()

    all_rooms = db.session.query(Salle).all()

    free_schedule = {room.nom_salle: [] for room in all_rooms}
    for start, end in time_slots:
        for room in all_rooms:
            # Check if the room is occupied during this timeslot
            if not any(occ for occ in occupied_slots if occ.id_salle == room.id_salle and start >= occ.heure_debut and end <= occ.heure_fin):
                free_schedule[room.nom_salle].append(f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}")

    return jsonify(free_schedule)

# Lancer l'application
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
