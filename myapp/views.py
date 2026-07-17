from django.shortcuts import render
from django.http import JsonResponse
import requests
from .models import FavoriteRecipe

# Helper function to get list of favorite recipe IDs
def get_favorite_ids():
    return list(FavoriteRecipe.objects.values_list('recipe_id', flat=True))

# Create your views here.
def index(request):
    try:
        url = requests.get("https://dummyjson.com/recipes")
        mydata = url.json()
        recipes = mydata.get("recipes", [])
    except Exception:
        recipes = []

    try:
        tagurl = requests.get("https://dummyjson.com/recipes/tags").json()
    except Exception:
        tagurl = []

    context = {
        "data": recipes,
        "tag": tagurl,
        "favorite_ids": get_favorite_ids()
    }
    return render(request, "index.html", context)

def search(request):
    query = request.POST.get("query", "")
    try:
        response = requests.get(f"https://dummyjson.com/recipes/search?q={query}").json()
        recipes = response.get("recipes", [])
    except Exception:
        recipes = []

    try:
        tagurl = requests.get("https://dummyjson.com/recipes/tags").json()
    except Exception:
        tagurl = []

    context = {
        "data": recipes,
        "tag": tagurl,
        "favorite_ids": get_favorite_ids(),
        "search_query": query
    }
    return render(request, "index.html", context)

def databytags(request, tag):
    try:
        response = requests.get(f"https://dummyjson.com/recipes/tag/{tag}").json()
        recipes = response.get("recipes", [])
    except Exception:
        recipes = []

    try:
        tagurl = requests.get("https://dummyjson.com/recipes/tags").json()
    except Exception:
        tagurl = []

    context = {
        "data": recipes,
        "tag": tagurl,
        "favorite_ids": get_favorite_ids(),
        "active_tag": tag
    }
    return render(request, "index.html", context)

def mealtype(request, meal):
    try:
        response = requests.get(f"https://dummyjson.com/recipes/meal-type/{meal}").json()
        recipes = response.get("recipes", [])
    except Exception:
        recipes = []

    try:
        tagurl = requests.get("https://dummyjson.com/recipes/tags").json()
    except Exception:
        tagurl = []

    context = {
        "data": recipes,
        "tag": tagurl,
        "favorite_ids": get_favorite_ids(),
        "active_meal": meal
    }
    return render(request, "index.html", context)

def singledata(request, id):
    try:
        response = requests.get(f"https://dummyjson.com/recipes/{id}").json()
    except Exception:
        response = None

    is_favorite = FavoriteRecipe.objects.filter(recipe_id=id).exists()
    
    context = {
        "data": response,
        "is_favorite": is_favorite
    }
    return render(request, "receipes.html", context)

# View to toggle favorite recipe (AJAX)
def toggle_favorite(request, id):
    if request.method == "POST":
        try:
            fav = FavoriteRecipe.objects.filter(recipe_id=id)
            if fav.exists():
                fav.delete()
                return JsonResponse({"status": "removed", "id": id})
            else:
                name = request.POST.get('name')
                image = request.POST.get('image')
                
                # Fallback to API if not in POST payload
                if not name or not image:
                    res = requests.get(f"https://dummyjson.com/recipes/{id}").json()
                    name = res.get('name')
                    image = res.get('image')
                
                FavoriteRecipe.objects.create(recipe_id=id, name=name, image=image)
                return JsonResponse({"status": "added", "id": id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=400)

# View to render bookmarked recipes list
def favorites_list(request):
    favorites = FavoriteRecipe.objects.all().order_by('-created_at')
    try:
        tagurl = requests.get("https://dummyjson.com/recipes/tags").json()
    except Exception:
        tagurl = []

    # Map FavoriteRecipe objects to match DummyJSON properties for template compatibility
    recipes_data = []
    for f in favorites:
        recipes_data.append({
            "id": f.recipe_id,
            "name": f.name,
            "image": f.image,
            "cookTimeMinutes": "Saved",
            "mealType": []
        })

    context = {
        "data": recipes_data,
        "tag": tagurl,
        "favorite_ids": get_favorite_ids(),
        "is_favorites_page": True
    }
    return render(request, "favorites.html", context)