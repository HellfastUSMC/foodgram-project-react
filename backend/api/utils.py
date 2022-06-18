from food.models import Ingredient


def check_fields(request, fields):
    response_message = {}
    for field in fields:
        if field not in request.data or not request.data[field]:
            response_message[field] = f'Проверьте поле {field}'
    if response_message:
        return response_message
    return None


def create_ingredients(obj, ingredients):
    objects = []
    for ingredient in ingredients:
        objects.append(Ingredient(
            product_id=int(ingredient['id']),
            amount=int(ingredient['amount']),
            recipe_id=obj.id
        ))
    Ingredient.objects.bulk_create(objects)
