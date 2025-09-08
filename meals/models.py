from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Configuration(models.Model):
    """System configuration settings"""
    name = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Configuration'
        verbose_name_plural = 'Configurations'

    def __str__(self):
        return f"{self.name}: {self.value[:50]}"


class APIConfiguration(models.Model):
    """API configuration and keys management"""
    API_PROVIDERS = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('google', 'Google'),
        ('themealdb', 'TheMealDB'),
    ]
    
    provider = models.CharField(max_length=50, choices=API_PROVIDERS, unique=True)
    api_key = models.CharField(max_length=500)
    api_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    quota_limit = models.IntegerField(null=True, blank=True)
    quota_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['provider']
        verbose_name = 'API Configuration'
        verbose_name_plural = 'API Configurations'

    def __str__(self):
        return f"{self.get_provider_display()} - {'Active' if self.is_active else 'Inactive'}"


class Meal(models.Model):
    """Meal data from TheMealDB"""
    meal_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=100, blank=True)
    instructions = models.TextField()
    thumbnail = models.URLField(blank=True)
    tags = models.CharField(max_length=500, blank=True)
    youtube_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)
    
    # Metadata
    is_indexed = models.BooleanField(default=False)
    last_fetched = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Meal'
        verbose_name_plural = 'Meals'

    def __str__(self):
        return f"{self.name} ({self.category})"


class Ingredient(models.Model):
    """Ingredients for meals"""
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name='ingredients')
    name = models.CharField(max_length=255)
    measure = models.CharField(max_length=100, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['meal', 'order']
        unique_together = ['meal', 'name']
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return f"{self.name} - {self.measure}"


class SearchQuery(models.Model):
    """Track user search queries"""
    query = models.TextField()
    results_count = models.IntegerField(default=0)
    response_time = models.FloatField(help_text="Response time in seconds")
    use_toolfront = models.BooleanField(default=False)
    model_used = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Search Query'
        verbose_name_plural = 'Search Queries'

    def __str__(self):
        return f"{self.query[:50]} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class SearchResult(models.Model):
    """Individual search results for queries"""
    query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name='results')
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    score = models.FloatField()
    position = models.IntegerField()

    class Meta:
        ordering = ['query', 'position']
        verbose_name = 'Search Result'
        verbose_name_plural = 'Search Results'

    def __str__(self):
        return f"{self.meal.name} (pos: {self.position}, score: {self.score:.2f})"


class CacheEntry(models.Model):
    """Cache management"""
    key = models.CharField(max_length=255, unique=True)
    value = models.TextField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    accessed_at = models.DateTimeField(auto_now=True)
    hit_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-accessed_at']
        verbose_name = 'Cache Entry'
        verbose_name_plural = 'Cache Entries'

    def __str__(self):
        return f"{self.key} (hits: {self.hit_count})"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at


class IndexingTask(models.Model):
    """Track indexing tasks"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_meals = models.IntegerField(default=0)
    processed_meals = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Indexing Task'
        verbose_name_plural = 'Indexing Tasks'

    def __str__(self):
        return f"Task {self.id} - {self.get_status_display()} ({self.processed_meals}/{self.total_meals})"

    @property
    def progress_percentage(self):
        if self.total_meals == 0:
            return 0
        return (self.processed_meals / self.total_meals) * 100
