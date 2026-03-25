from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models.functions import Cast
from django.db.models import FloatField, Avg
from django.utils import timezone

# ================== EditeProfil ==================
class CustemUser(AbstractUser):
    avatar = models.ImageField(upload_to="avatars", null=True, blank=True, verbose_name="Аватар")
    description = models.TextField(max_length=250, null=True, blank=True, verbose_name="Описание")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

# ================== Genre ==================
class Genre(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name

# ================== Anime ==================
class Anime(models.Model):
    event = ""
    month = timezone.now().month
    if month in (12, 1, 2):
        event = "winter"
    elif month in (3, 4, 5):
        event = "Весна"
    elif month in (6, 7, 8):
        event = "summer"
    elif month in (9, 10, 11):
        event = "autumn"

    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(unique=True, blank=True, verbose_name="Slug")
    image = models.ImageField(upload_to="anime_poster", verbose_name="Постер")
    description = models.TextField(verbose_name="Описание")
    release_year = models.DateField(verbose_name="Дата выхода")
    shikimori_rating = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="Рейтинг Shikimori")
    our_rating = models.FloatField(default=0, verbose_name="Наш рейтинг")
    ss_year = models.CharField(default=event, verbose_name="Сезон")
    year = models.CharField(default=timezone.now().year, verbose_name="Год")

    genres = models.ManyToManyField("Genre", related_name="animes", verbose_name="Жанры")

    class Meta:
        verbose_name = "Аниме"
        verbose_name_plural = "Аниме"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Anime.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        genres = ", ".join(g.name for g in self.genres.all())
        return f"Аниме: {self.name} || Жанр: {genres} || Дата выхода: {self.release_year} || {self.slug}"

# ================== Bookmark ==================
class Bookmark(models.Model):
    STATUS_CHOICES = [
        ['planned', 'Буду смотреть'],
        ['watched', 'Просмотрено'],
    ]

    user = models.ForeignKey(CustemUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, verbose_name="Аниме")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name="Статус")

    class Meta:
        unique_together = ("user", "anime")
        verbose_name = "Закладка"
        verbose_name_plural = "Закладки"

    def __str__(self):
        return f"{self.user} - {self.anime.name} ({self.status})"

# ================== Reating ==================
class Reating(models.Model):
    REATING_CHOICES = [
        ['1', '⭐1'],
        ['2', '⭐2'],
        ['3', '⭐3'],
        ['4', '⭐4'],
        ['5', '⭐5'],
    ]

    user = models.ForeignKey(CustemUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, verbose_name="Аниме")
    point = models.CharField(max_length=5, choices=REATING_CHOICES, verbose_name="Оценка")

    class Meta:
        unique_together = ("user", "anime")
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"

    def __str__(self):
        return f"{self.user} - {self.anime.name} ({self.point})"

# ================== SeasonAnime ==================
class SeasonAnime(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name="seasons", verbose_name="Аниме")
    seasons_number = models.PositiveIntegerField(verbose_name="Номер сезона")

    class Meta:
        verbose_name = "Сезон"
        verbose_name_plural = "Сезоны"

    def __str__(self):
        return f"Аниме: {self.anime.name} || Сезон: {self.seasons_number}"

# ================== Episode ==================
class Episode(models.Model):
    season = models.ForeignKey(SeasonAnime, on_delete=models.CASCADE, related_name="episodes", verbose_name="Сезон")
    title = models.CharField(max_length=200, verbose_name="Название")
    episode_number = models.PositiveIntegerField(verbose_name="Номер эпизода")
    video = models.FileField(upload_to="episodes/", verbose_name="Видео")
    poster = models.ImageField(upload_to="episode_posters/", verbose_name="Постер")

    class Meta:
        verbose_name = "Эпизод"
        verbose_name_plural = "Эпизоды"

    def __str__(self):
        return f"Аниме: {self.season.anime.name} || Сезон: {self.season.seasons_number} || Название: {self.title} || Эпизод: {self.episode_number}"

# ================== Character ==================
class Character(models.Model):
    GENDER_CHOICES = [
        ['Мужской',    '♂️ Мужской'],
        ['Женский',    '♀️ Женский'],
        ['Неизвестно', '❓ Неизвестно'],
    ]

    GG_CHOICES = [
        ['Главный герой', '⭐ Главный герой'],
    ]

    EYE_COLOR_CHOICES = [
        ['Красный', '🔴 Красный'],
        ['Оранжевый', '🟠 Оранжевый'],
        ['Жёлтый', '🟡 Жёлтый'],
        ['Зелёный', '🟢 Зелёный'],
        ['Синий', '🔵 Синий'],
        ['Фиолетовый', '🟣 Фиолетовый'],
        ['Коричневый', '🟤 Коричневый'],
        ['Чёрный', '⚫️ Чёрный'],
        ['Белый', '⚪️ Белый'],
    ]

    HAIR_COLOR_CHOICES = EYE_COLOR_CHOICES.copy()

    SPECIES_CHOICES = [
        ['Человек', 'Человек'],
        ['Демон',   'Демон'],
        ['Ангел',   'Ангел'],
        ['Гном',    'Гном'],
        ['Эльф',    'Эльф'],
        ['Неизвестно', 'Неизвестно']
    ]

    anime      = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name="characters", verbose_name="Аниме")
    eye_color  = models.CharField(max_length=20, choices=EYE_COLOR_CHOICES, verbose_name="Цвет глаз")
    hair_color = models.CharField(max_length=20, choices=HAIR_COLOR_CHOICES, verbose_name="Цвет волос")
    gender     = models.CharField(max_length=20, choices=GENDER_CHOICES, verbose_name="Пол")
    species    = models.CharField(max_length=20, choices=SPECIES_CHOICES, verbose_name="Раса")
    age        = models.PositiveIntegerField(blank=True, null=True, verbose_name="Возраст")
    name       = models.CharField(max_length=100, verbose_name="Имя")
    gg         = models.CharField(max_length=20, choices=GG_CHOICES, blank=True, null=True, default=None, verbose_name="Роль")
    image      = models.ImageField(upload_to="characters/", verbose_name="Изображение")

    class Meta:
        verbose_name = "Персонаж"
        verbose_name_plural = "Персонажи"

    def __str__(self):
        return f"Имя: {self.name} || Пол: {self.gender} || Раса: {self.species} || Возраст: {self.age} || {self.gg}"

@receiver(post_save, sender=Reating)
@receiver(post_delete, sender=Reating)
def update_anime_rating(sender, instance, **kwargs):
    anime = instance.anime
    avg = Reating.objects.filter(anime=anime).aggregate(
        avg=Avg(Cast('point', FloatField()))
    )['avg'] or 0
    Anime.objects.filter(pk=anime.pk).update(our_rating=round(avg, 1))

class BackgroundPicture(models.Model):
    image = models.ImageField(upload_to="background/", verbose_name="Изображение")

    class Meta:
        verbose_name = "Фоновое изображение"
        verbose_name_plural = "Фоновые изображения"

# ================== WatchHistory ==================
class WatchHistory(models.Model):
    user = models.ForeignKey(CustemUser, on_delete=models.CASCADE, verbose_name="Пользователь")
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, verbose_name="Аниме")
    season_anime = models.ForeignKey(SeasonAnime, on_delete=models.CASCADE, verbose_name="Сезон")
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, verbose_name="Эпизод")
    watched_seconds = models.PositiveIntegerField(default=0, verbose_name="Просмотрено (сек)")
    duration_seconds = models.PositiveIntegerField(default=0, verbose_name="Длительность (сек)")

    class Meta:
        verbose_name = "История просмотра"
        verbose_name_plural = "История просмотров"

    @property
    def progress_percent(self):
        if self.duration_seconds == 0:
            return 0
        return int((self.watched_seconds / self.duration_seconds) * 100)

    def __str__(self):
        return f"Пользователь: {self.user} || Аниме: {self.anime.name} || Сезон: {self.season_anime.seasons_number} || Серия: {self.episode.episode_number} || {self.progress_percent}%"

# ================== Comments ==================
class Comments(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    author = models.ForeignKey(CustemUser, on_delete=models.CASCADE, verbose_name="Автор")
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name="comments", verbose_name="Аниме")
    content = models.CharField(max_length=600, verbose_name="Содержание")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, verbose_name="Родительский комментарий")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    @property
    def children(self):
        return Comments.objects.filter(parent=self).all()

    @property
    def children_count(self):
        return Comments.objects.filter(parent=self).all().count()

    def __str__(self):
        return f"{self.author} оставил комментарий на аниме {self.anime.name}"