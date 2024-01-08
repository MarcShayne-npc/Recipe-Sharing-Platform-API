import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://@Maku/Recipes?driver=ODBC+Driver+17+for+SQL+Server'
db = SQLAlchemy(app)

logging.basicConfig(
    level=logging.INFO,  # Set logging level to INFO
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Define models for Recipes, Ratings, and Comments
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)
    preparation_time = db.Column(db.Integer, nullable=False)
    ratings = db.relationship('Rating', backref='recipe', lazy=True)
    comments = db.relationship('Comment', backref='recipe', lazy='dynamic')

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'), nullable=False)

# Define API endpoints
@app.route('/recipes', methods=['POST'])
def add_recipe():
    logging.info("Add a new recipe")
    data = request.get_json()
    new_recipe = Recipe(
        name=data['name'],
        ingredients=data['ingredients'],
        steps=data['steps'],
        preparation_time=data['preparation_time'],
    )
    db.session.add(new_recipe)
    db.session.commit()

    # Retrieve the generated ID from the new recipe object
    recipe_id = new_recipe.id

    # Include the ID in the response
    return jsonify({'message': 'Recipe added successfully', 'id': recipe_id}), 201

@app.route('/recipes', methods=['GET'])
def get_all_recipes():
    logging.info("Retrive all recipe")
    recipes = Recipe.query.order_by(Recipe.id.desc()).all()
    serialized_recipes = []
    for recipe in recipes:
        serialized_recipes.append({
            'id': recipe.id,
            'name': recipe.name,
            'ingredients': recipe.ingredients,
            'steps': recipe.steps,
            'preparation_time': recipe.preparation_time
        })
    return jsonify({'recipes': serialized_recipes})

@app.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe_by_id(recipe_id):
    logging.info("Retrive recipe by ID")
    recipe = db.session.get(Recipe, recipe_id)
    if recipe:
        serialized_recipe = {
            'id': recipe.id,
            'name': recipe.name,
            'ingredients': recipe.ingredients,
            'steps': recipe.steps,
            'preparation_time': recipe.preparation_time
        }
        return jsonify({'recipe': serialized_recipe}), 200
    else:
        return jsonify({'message': 'Recipe not found'}), 404

@app.route('/recipes/<int:recipe_id>', methods=['PUT'])
def update_recipe(recipe_id):
    logging.info("Update specific recipe by ID")
    data = request.get_json()
    recipe = db.session.get(Recipe, recipe_id)
    if recipe:
        recipe.name = data['name']
        recipe.ingredients = data['ingredients']
        recipe.steps = data['steps']
        recipe.preparation_time = data['preparation_time']
        db.session.commit()
        return jsonify({'message': 'Recipe updated successfully'}), 200
    else:
        return jsonify({'message': 'Recipe not found'}), 404

@app.route('/recipes/<int:recipe_id>', methods=['DELETE'])
def delete_recipe(recipe_id):
    logging.info("Delete specific recipe by ID")
    recipe = db.session.get(Recipe, recipe_id)
    if recipe:
        for comment in recipe.comments:
            comment.recipe_id = None  # Set recipe_id to NULL
            db.session.delete(recipe)
            db.session.commit()
        return jsonify({'message': 'Recipe deleted successfully'}), 204
    else:
        return jsonify({'message': 'Recipe not found'}), 404

@app.route('/recipes/<int:recipe_id>/ratings', methods=['POST'])
def add_rating(recipe_id):
    logging.info("Add rating to recipe")
    data = request.get_json()
    rating = data['rating']
    recipe = db.session.get(Recipe, recipe_id)
    if recipe:
        new_rating = Rating(rating=rating, recipe_id=recipe_id)
        db.session.add(new_rating)
        db.session.commit()
        return jsonify({'message': 'Rating added successfully'}), 201
    else:
        return jsonify({'message': 'Recipe not found'}), 404

@app.route('/recipes/<int:recipe_id>/comments', methods=['POST'])
def add_comment(recipe_id):
    logging.info("Add Comment recipe")
    data = request.get_json()
    comment_text = data['comment']
    recipe = db.session.get(Recipe, recipe_id)
    if recipe:
        new_comment = Comment(text=comment_text, recipe_id=recipe_id)
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({'message': 'Comment added successfully'}), 201
    else:
        return jsonify({'message': 'Recipe not found'}), 404

@app.route('/recipes/<int:recipe_id>/comments', methods=['GET'])
def get_recipe_comments(recipe_id):
    logging.info("Get all comment recipe")
    recipe = db.session.get(Recipe, recipe_id)
    if recipe:
        comments = recipe.comments.all()
        serialized_comments = [comment.to_dict() for comment in comments]
        return jsonify({'comments': serialized_comments}), 200
    else:
        return jsonify({'message': 'Recipe not found'}), 404
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

