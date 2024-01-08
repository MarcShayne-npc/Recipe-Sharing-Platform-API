import unittest
import requests

BASE_URL = 'http://127.0.0.1:5000'

def create_test_recipe():
    """Creates a test recipe and returns the response object."""
    data = {
        'name': 'Test Recipe',
        'ingredients': 'Test Ingredient 1, Test Ingredient 2',
        'steps': 'Test Step 1, Test Step 2',
        'preparation_time': 30
    }
    response = requests.post(f'{BASE_URL}/recipes', json=data)
    response.raise_for_status()  # Raise an exception for non-201 responses
    return response

class TestAppEndpoints(unittest.TestCase):
    def test_add_recipe(self):
        response = create_test_recipe()
        try:
            recipe_id = response.json().get('id')
            self.assertIsNotNone(recipe_id, "Failed to extract recipe ID from response")
        except ValueError as e:
            self.fail(f"Failed to parse JSON response. Error: {e}")

    def test_get_all_recipes(self):
        response = requests.get(f'{BASE_URL}/recipes')
        self.assertEqual(response.status_code, 200)
        # Add more assertions based on the expected response

    def test_get_recipe_by_id(self):
        response = create_test_recipe()
        recipe_id = response.json().get('id')

        get_recipe_response = requests.get(f'{BASE_URL}/recipes/{recipe_id}')
        self.assertEqual(get_recipe_response.status_code, 200)

    def test_update_recipe(self):
        response = create_test_recipe()
        recipe_id = response.json().get('id')

        updated_data = {
            'name': 'Updated Recipe Name',
            'ingredients': 'Updated Ingredient 1, Updated Ingredient 2',
            'steps': 'Updated Step 1, Updated Step 2',
            'preparation_time': 45  # Updated preparation time
        }

        response = requests.put(f'{BASE_URL}/recipes/{recipe_id}', json=updated_data)
        self.assertEqual(response.status_code, 200)

    def test_delete_recipe(self):
        response = create_test_recipe()
        recipe_id = response.json().get('id')

        response = requests.delete(f'{BASE_URL}/recipes/{recipe_id}')
        self.assertEqual(response.status_code, 204)

    def test_add_rating(self):
        response = create_test_recipe()
        recipe_id = response.json().get('id')
        rating = 4
        response = requests.post(f'{BASE_URL}/recipes/{recipe_id}/ratings', json={'rating': rating})
        self.assertEqual(response.status_code, 201)

    def test_add_comment(self):
        response = create_test_recipe()
        recipe_id = response.json().get('id')
        comment_text = "This recipe is delicious!"
        response = requests.post(f'{BASE_URL}/recipes/{recipe_id}/comments', json={'comment': comment_text})
        self.assertEqual(response.status_code, 201)

    def test_get_recipe_comments(self):
        response = create_test_recipe()
        recipe_id = response.json().get('id')
        response = requests.get(f'{BASE_URL}/recipes/{recipe_id}/comments')
        self.assertEqual(response.status_code, 200)

# Add more test classes for other endpoints

if __name__ == '__main__':
    unittest.main()
