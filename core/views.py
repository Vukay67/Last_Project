from django.shortcuts import redirect, render
from django.contrib.auth import login, logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import AuthenticationForm, RegistrationForm, CustemUserForm
from .models import *
from django.db import models as db_models
from django.shortcuts import get_object_or_404
from django.db.models import OuterRef, Subquery
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.db.models import Q
from random import choices
import os
from django.http import StreamingHttpResponse
from django.conf import settings

def serve_video(request, path):
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    file_size = os.path.getsize(full_path)
    range_header = request.META.get('HTTP_RANGE', '').strip()

    if range_header and range_header.startswith('bytes='):
        first, last = range_header.replace('bytes=', '').split('-')
        first = int(first)
        last = int(last) if last else file_size - 1
        length = last - first + 1

        def iterator():
            with open(full_path, 'rb') as f:
                f.seek(first)
                remaining = length
                while remaining:
                    chunk = f.read(min(8192, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        response = StreamingHttpResponse(iterator(), status=206, content_type='video/mp4')
        response['Content-Range'] = f'bytes {first}-{last}/{file_size}'
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(length)
        return response

    response = StreamingHttpResponse(open(full_path, 'rb'), content_type='video/mp4')
    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = str(file_size)
    return response

def main_page(request):
    anime = Anime.objects.prefetch_related('genres').all()
    top_ani = Anime.objects.filter(our_rating__gte=4.5)
    event = Episode.event
    years = Episode.years
    event_ani = Episode.objects.filter(ss_year=event, year=years).order_by("-id")

    if request.user.is_authenticated:
        history = WatchHistory.objects.filter(user=request.user).order_by('-id').select_related('anime', 'episode')[:10]
    else:
        history = []

    planned_anime = None

    if request.user.is_authenticated:
        planned_anime_qs = Anime.objects.filter(
            bookmark__user=request.user,
            bookmark__status='planned'
        )

        if planned_anime_qs.exists():
            planned_anime = choices(planned_anime_qs)

    ran_ani = choices(top_ani) if top_ani else None

    context = {
        "anime": anime,
        "ran_ani": ran_ani,
        "nex_ani": planned_anime,
        "event": event,
        "event_ani": event_ani,
        "year": years,
        "history": history,
    }
    return render(request, "index.html", context)

def login_page(request):
    if request.method == "POST":
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            login(request, form.user)
            return redirect("main_page")
    else:
        form = AuthenticationForm()
    context = {
        "form": form
    }
    return render(request, "login.html", context)

def register_page(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = CustemUser.objects.create_user(
                email=email,
                username=username,
                password=password
            )
            login(request, user)
            return redirect("main_page")
    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'register.html', context)\
    
def logout_view(request):
    logout(request)
    return redirect('main_page')

def anime_detail_page(request, slug):
    anime = get_object_or_404(
        Anime.objects.prefetch_related('genres', 'seasons__episodes'),
        slug=slug
    )
    current_bookmark = None
    current_reating = None

    if request.user.is_authenticated:
        bookmark = Bookmark.objects.filter(user=request.user, anime=anime).first()
        if bookmark:
            current_bookmark = bookmark.status

    if request.user.is_authenticated:
        point = Reating.objects.filter(user=request.user, anime=anime).first()
        if point:
            current_reating = point.point

    character = Character.objects.filter(anime=anime).order_by('-gg')
    context = {
        "anime": anime,
        "character": character,
        'current_bookmark': current_bookmark,
        "current_reating": current_reating
    }
    return render(request, "anime_detail.html", context)

def all_anime_page(request):
    search_query = request.GET.get('search', '')
    genre_id = request.GET.get('genres', '')
    sort_option = request.GET.get('sort', '')

    print(search_query)

    animes = Anime.objects.prefetch_related('genres', 'seasons__episodes')

    if search_query:
        animes = animes.filter(Q(name__icontains=search_query) | Q(name_en__icontains=search_query))
    if genre_id:
        animes = animes.filter(genres__id=genre_id)
    if sort_option == 'name_asc':
        animes = animes.order_by('name')
    elif sort_option == 'name_desc':
        animes = animes.order_by('-name')
    elif sort_option == 'series_asc':
        animes = animes.annotate(
            total_episodes=db_models.Count('seasons__episodes')
        ).order_by('-total_episodes')

    genres = Genre.objects.all()
    context = {
        'anime': animes,
        'genres': genres,
        'selected_genre': genre_id,
        'search_query': search_query,
        'sort_option': sort_option,
    }
    return render(request, 'all_anime.html', context)

def characters_page(request):
    search_query = request.GET.get('search', '')
    selected_eye = request.GET.get('eye_color', '')
    selected_hair = request.GET.get('hair_color', '')
    selected_gender = request.GET.get('gender', '')
    selected_specie = request.GET.get('specie', '')

    characters = Character.objects.select_related('anime').all()

    if search_query:
        characters = characters.filter(name__icontains=search_query)
    if selected_eye:
        characters = characters.filter(eye_color=selected_eye)
    if selected_hair:
        characters = characters.filter(hair_color=selected_hair)
    if selected_gender:
        characters = characters.filter(gender=selected_gender)
    if selected_specie:
        characters = characters.filter(species=selected_specie)

    context = {
        'character': characters,
        'eye_colors':  Character.EYE_COLOR_CHOICES,
        'hair_colors': Character.HAIR_COLOR_CHOICES,
        'genders':     Character.GENDER_CHOICES,
        'species':     Character.SPECIES_CHOICES,
        'search_query':    search_query,
        'selected_eye':    selected_eye,
        'selected_hair':   selected_hair,
        'selected_genders': selected_gender,
        'selected_specie': selected_specie,
    }
    return render(request, 'characters.html', context)

def episode_detail_page(request, episode_id):
    episode = get_object_or_404(Episode.objects.select_related('season__anime'), id=episode_id)
    characters = Character.objects.filter(anime=episode.season.anime, gg="Главный герой")

    prev_episode = Episode.objects.filter(
        season=episode.season,
        episode_number=episode.episode_number - 1
    ).first()

    next_episode = Episode.objects.filter(
        season=episode.season,
        episode_number=episode.episode_number + 1
    ).first()

    history = None
    if request.user.is_authenticated:
        history = WatchHistory.objects.filter(
            user=request.user,
            episode=episode
        ).first()

    context = {
        "characters": characters,
        "episode": episode,
        'history': history,
        "prev_episode": prev_episode,
        "next_episode": next_episode,
    }
    return render(request, 'episode_detail.html', context)

def all_gg_page(request):
    character = Character.objects.filter(gg="Главный герой")
    search_query = request.GET.get('search', '')
    selected_eye = request.GET.get('eye_color', '')
    selected_hair = request.GET.get('hair_color', '')
    selected_gender = request.GET.get('gender', '')
    selected_specie = request.GET.get('specie', '')

    if search_query:
        character = character.filter(name__icontains=search_query)
    if selected_eye:
        character = character.filter(eye_color=selected_eye)
    if selected_hair:
        character = character.filter(hair_color=selected_hair)
    if selected_gender:
        character = character.filter(gender=selected_gender)
    if selected_specie:
        character = character.filter(species=selected_specie)

    context = {
        "character": character,
        'eye_colors':  Character.EYE_COLOR_CHOICES,
        'hair_colors': Character.HAIR_COLOR_CHOICES,
        'genders':     Character.GENDER_CHOICES,
        'species':     Character.SPECIES_CHOICES,
        'search_query':    search_query,
        'selected_eye':    selected_eye,
        'selected_hair':   selected_hair,
        'selected_genders': selected_gender,
        'selected_specie': selected_specie,
    }
    return render(request, "all_gg.html", context)

@login_required
def add_bookmark(request, slug, status):
    anime = get_object_or_404(Anime, slug=slug)
    if status == 'delete':
        Bookmark.objects.filter(user=request.user, anime=anime).delete()
    else:
        Bookmark.objects.update_or_create(
            user=request.user,
            anime=anime,
            defaults={"status": status}
        )
    return redirect("anime_detail_page", slug=slug)

@login_required
def add_reating(request, slug, point):
    anime = get_object_or_404(Anime, slug=slug)
    if point == 'delete':
        Reating.objects.filter(user=request.user, anime=anime).delete()
    else:
        Reating.objects.update_or_create(
            user=request.user,
            anime=anime,
            defaults={"point": point}
        )
    return redirect("anime_detail_page", slug=slug)

@login_required
def profil_page(request, pk):
    user = get_object_or_404(CustemUser, id=pk)

    rating_sub = Reating.objects.filter(
        user=user, anime=OuterRef('anime')
    ).values('point')[:1]

    watched = user.bookmark_set.filter(status='watched').annotate(
        user_rating=Subquery(rating_sub)
    )
    planned = user.bookmark_set.filter(status='planned')

    context = {
        'user': user,
        'watched': watched,
        'planned': planned,
    }
    return render(request, "profil.html", context)

@login_required
def episode_page(request, anime_slug, season_num, episode_num):
    anime = get_object_or_404(Anime, slug=anime_slug)
    season = get_object_or_404(SeasonAnime, anime=anime, seasons_number=season_num)
    episode = get_object_or_404(Episode, season=season, episode_number=episode_num)

    if request.user.is_authenticated:
        WatchHistory.objects.get_or_create(
            user=request.user,
            anime=anime,
            season_anime=season,
            episode=episode,
        )

    context = {
        'anime': anime,
        'season': season,
        'episode': episode,
    }
    return render(request, "episode.html", context)

@require_POST
def save_progress(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error'}, status=401)

    data = json.loads(request.body)
    anime_id = data.get('anime_id')
    season_id = data.get('season_id')
    episode_id = data.get('episode_id')
    watched_seconds = data.get('watched_seconds', 0)
    duration_seconds = data.get('duration_seconds', 0)

    history, created = WatchHistory.objects.get_or_create(
        user=request.user,
        anime_id=anime_id,
        season_anime_id=season_id,
        episode_id=episode_id,
    )
    history.watched_seconds = watched_seconds
    history.duration_seconds = duration_seconds
    history.save()

    if history.progress_percent >= 93:
        history.delete()
        return JsonResponse({'status': 'deleted', 'progress': 100})

    return JsonResponse({'status': 'ok', 'progress': history.progress_percent})

def redact_page(request):
    if request.method == "POST":
        form = CustemUserForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profil_page", pk=request.user.pk)
    else:
        form = CustemUserForm(instance=request.user)

    context = {
        "form": form 
    }

    return render(request, "redact.html", context)

def about_page(request):
    return render(request, "about.html", {})

def contacts_page(request):
    return render(request, "contacts.html", {})

@login_required
@require_POST
def comment_action(request, slug):
    anime = Anime.objects.get(slug=slug)
    user = request.user
    comment_text = request.POST.get("comment")

    if len(comment_text) != 0:
        comment = Comments.objects.create(author=user, anime=anime, content=comment_text)
        comment.save()

    return redirect(reverse("anime_detail_page", kwargs={"slug": slug}) + "#commentsList")

def hentai(request):
    return render(request, "hentai.html", {})

def all_hentai(request):
    return render(request, "all_hentai.html", {})