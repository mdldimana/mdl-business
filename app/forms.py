from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import Utilisateur


class ConnexionForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    mot_de_passe = PasswordField('Mot de passe', validators=[DataRequired(), Length(min=6)])
    se_souvenir = BooleanField('Se souvenir de moi')


class InscriptionForm(FlaskForm):
    prenom = StringField('Prénom', validators=[DataRequired(), Length(min=2, max=50)])
    nom = StringField('Nom', validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    mot_de_passe = PasswordField('Mot de passe', validators=[
        DataRequired(),
        Length(min=6, message='Le mot de passe doit contenir au moins 6 caractères.')
    ])
    mot_de_passe_confirm = PasswordField('Confirmer le mot de passe', validators=[
        DataRequired(),
        EqualTo('mot_de_passe', message='Les mots de passe ne correspondent pas.')
    ])

    def validate_email(self, email):
        """Vérifie que l'email n'est pas déjà utilisé"""
        utilisateur = Utilisateur.query.filter_by(email=email.data).first()
        if utilisateur:
            raise ValidationError('Cet email est déjà utilisé. Veuillez vous connecter.')