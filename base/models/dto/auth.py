from dataclasses import dataclass
from typing import List

from base.models import Ferme

@dataclass
class NewEmploye:
    email: str
    first_name: str
    last_name: str

@dataclass
class CreateFerme:
    nom: str
    adresse: str
    superficie_cultivee: str
    methodes: List[int]
    employes: List[NewEmploye]


@dataclass
class RegisterUser:
    email: str
    password: str
    first_name: str
    last_name: str
    ferme: CreateFerme