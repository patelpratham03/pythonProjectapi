from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from .models import FavoriteRecipe

# Helper function to get list of favorite recipe IDs for the logged-in user
def get_favorite_ids(user):
    if user.is_authenticated:
        return list(FavoriteRecipe.objects.filter(user=user).values_list('recipe_id', flat=True))
    return []

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
        "favorite_ids": get_favorite_ids(request.user)
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
        "favorite_ids": get_favorite_ids(request.user),
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
        "favorite_ids": get_favorite_ids(request.user),
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
        "favorite_ids": get_favorite_ids(request.user),
        "active_meal": meal
    }
    return render(request, "index.html", context)

def singledata(request, id):
    try:
        response = requests.get(f"https://dummyjson.com/recipes/{id}").json()
    except Exception:
        response = None

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = FavoriteRecipe.objects.filter(user=request.user, recipe_id=id).exists()
    
    context = {
        "data": response,
        "is_favorite": is_favorite
    }
    return render(request, "receipes.html", context)

# View to toggle favorite recipe (AJAX) - Requires User Login
def toggle_favorite(request, id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "login_required"}, status=200)

    if request.method == "POST":
        try:
            fav = FavoriteRecipe.objects.filter(user=request.user, recipe_id=id)
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
                
                FavoriteRecipe.objects.create(user=request.user, recipe_id=id, name=name, image=image)
                return JsonResponse({"status": "added", "id": id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=400)

# View to render bookmarked recipes list
def favorites_list(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please log in to view your bookmarked recipes.")
        return redirect('/login/')

    favorites = FavoriteRecipe.objects.filter(user=request.user).order_by('-created_at')
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
        "favorite_ids": get_favorite_ids(request.user),
        "is_favorites_page": True
    }
    return render(request, "favorites.html", context)

# User login view
def login_user(request):
    if request.method == "POST":
        u_name = request.POST.get('username')
        u_pass = request.POST.get('password')
        
        user = authenticate(request, username=u_name, password=u_pass)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('/')
        else:
            messages.error(request, "Invalid username or password.")
            
    return render(request, "login.html")

# User registration view
def register_user(request):
    if request.method == "POST":
        name = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=name).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
        else:
            user = User.objects.create_user(username=name, email=email, password=password)
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('/')
            
    return render(request, "register.html")

# Logout view
def logout_user(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('/')