# LIST ANIMAL

Collecter la liste de tous les animals postés.

**URL** : `/api/animal_list/`

**Method** : `GET`

**Auth required** : NO


## Success Response

**Code** : `200 OK`

**Content example**

```json

   [
      {
        "age": 5, 
        "date_creation": "2018-03-05", 
        "description": "beautiful polar bear", 
        "id": 1, 
        "name": "bearette", 
        "race": "bearus", 
        "type": "bear"
      }
   ]

```

## Réponse Erreur

**Condition** : S'il n'y a aucun contenu

**Code** : `204 NO CONTENT`

**Content** :

```json
{
   "error":"no animals"
}
```
