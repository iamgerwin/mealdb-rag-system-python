from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Configuration, APIConfiguration, Meal, Ingredient,
    SearchQuery, SearchResult, CacheEntry, IndexingTask
)


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'value_preview', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'value', 'description']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'value', 'description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def value_preview(self, obj):
        return obj.value[:100] + '...' if len(obj.value) > 100 else obj.value
    value_preview.short_description = 'Value'


@admin.register(APIConfiguration)
class APIConfigurationAdmin(admin.ModelAdmin):
    list_display = ['provider', 'api_key_masked', 'is_active', 'quota_status', 'updated_at']
    list_filter = ['provider', 'is_active']
    search_fields = ['provider', 'api_url']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at', 'quota_used']
    
    fieldsets = (
        ('API Details', {
            'fields': ('provider', 'api_key', 'api_url', 'is_active')
        }),
        ('Quota Management', {
            'fields': ('quota_limit', 'quota_used'),
            'description': 'Set quota limits to track API usage'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def api_key_masked(self, obj):
        if obj.api_key:
            return obj.api_key[:10] + '...' + obj.api_key[-4:] if len(obj.api_key) > 14 else '****'
        return '-'
    api_key_masked.short_description = 'API Key'
    
    def quota_status(self, obj):
        if obj.quota_limit:
            percentage = (obj.quota_used / obj.quota_limit) * 100
            color = 'green' if percentage < 75 else 'orange' if percentage < 90 else 'red'
            return format_html(
                '<span style="color: {};">{}/{} ({}%)</span>',
                color, obj.quota_used, obj.quota_limit, int(percentage)
            )
        return '-'
    quota_status.short_description = 'Quota Status'


class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1
    fields = ['name', 'measure', 'order']
    ordering = ['order']


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['meal_id', 'name', 'category', 'area', 'is_indexed', 'thumbnail_preview']
    list_filter = ['category', 'area', 'is_indexed', 'last_fetched']
    search_fields = ['name', 'instructions', 'tags']
    readonly_fields = ['meal_id', 'created_at', 'updated_at', 'last_fetched', 'thumbnail_preview_large']
    inlines = [IngredientInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('meal_id', 'name', 'category', 'area', 'tags')
        }),
        ('Media', {
            'fields': ('thumbnail', 'thumbnail_preview_large', 'youtube_url', 'source_url')
        }),
        ('Instructions', {
            'fields': ('instructions',)
        }),
        ('Metadata', {
            'fields': ('is_indexed', 'last_fetched', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="50" height="50" />', obj.thumbnail)
        return '-'
    thumbnail_preview.short_description = 'Thumbnail'
    
    def thumbnail_preview_large(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" width="200" />', obj.thumbnail)
        return '-'
    thumbnail_preview_large.short_description = 'Thumbnail Preview'
    
    actions = ['mark_as_indexed', 'mark_as_not_indexed']
    
    def mark_as_indexed(self, request, queryset):
        updated = queryset.update(is_indexed=True)
        self.message_user(request, f'{updated} meals marked as indexed.')
    mark_as_indexed.short_description = 'Mark selected meals as indexed'
    
    def mark_as_not_indexed(self, request, queryset):
        updated = queryset.update(is_indexed=False)
        self.message_user(request, f'{updated} meals marked as not indexed.')
    mark_as_not_indexed.short_description = 'Mark selected meals as not indexed'


class SearchResultInline(admin.TabularInline):
    model = SearchResult
    extra = 0
    fields = ['position', 'meal', 'score']
    readonly_fields = ['position', 'meal', 'score']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query_preview', 'results_count', 'response_time', 'use_toolfront', 'model_used', 'created_at']
    list_filter = ['use_toolfront', 'model_used', 'created_at']
    search_fields = ['query']
    readonly_fields = ['query', 'results_count', 'response_time', 'use_toolfront', 
                      'model_used', 'ip_address', 'user_agent', 'created_at']
    inlines = [SearchResultInline]
    date_hierarchy = 'created_at'
    
    def query_preview(self, obj):
        return obj.query[:50] + '...' if len(obj.query) > 50 else obj.query
    query_preview.short_description = 'Query'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(CacheEntry)
class CacheEntryAdmin(admin.ModelAdmin):
    list_display = ['key', 'is_expired_display', 'hit_count', 'expires_at', 'accessed_at']
    list_filter = ['created_at', 'expires_at']
    search_fields = ['key', 'value']
    readonly_fields = ['key', 'created_at', 'accessed_at', 'hit_count']
    
    fieldsets = (
        ('Cache Details', {
            'fields': ('key', 'value', 'expires_at')
        }),
        ('Statistics', {
            'fields': ('hit_count', 'created_at', 'accessed_at')
        })
    )
    
    def is_expired_display(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">✗ Expired</span>')
        return format_html('<span style="color: green;">✓ Valid</span>')
    is_expired_display.short_description = 'Status'
    
    actions = ['clear_expired_cache']
    
    def clear_expired_cache(self, request, queryset):
        from django.utils import timezone
        expired = queryset.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        self.message_user(request, f'{count} expired cache entries cleared.')
    clear_expired_cache.short_description = 'Clear expired cache entries'


@admin.register(IndexingTask)
class IndexingTaskAdmin(admin.ModelAdmin):
    list_display = ['id', 'status_badge', 'progress_bar', 'total_meals', 'started_at', 'completed_at']
    list_filter = ['status', 'created_at']
    readonly_fields = ['status', 'total_meals', 'processed_meals', 'error_message',
                      'started_at', 'completed_at', 'created_at', 'progress_display']
    
    fieldsets = (
        ('Task Status', {
            'fields': ('status', 'progress_display', 'total_meals', 'processed_meals')
        }),
        ('Execution Details', {
            'fields': ('started_at', 'completed_at', 'created_at')
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        colors = {
            'pending': 'gray',
            'running': 'blue',
            'completed': 'green',
            'failed': 'red'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def progress_bar(self, obj):
        percentage = obj.progress_percentage
        return format_html(
            '<div style="width: 200px; background-color: #f0f0f0; border-radius: 5px;">'
            '<div style="width: {}%; background-color: #4CAF50; height: 20px; border-radius: 5px; text-align: center; color: white;">'
            '{}%</div></div>',
            percentage, int(percentage)
        )
    progress_bar.short_description = 'Progress'
    
    def progress_display(self, obj):
        return f"{obj.processed_meals}/{obj.total_meals} ({obj.progress_percentage:.1f}%)"
    progress_display.short_description = 'Progress'
    
    actions = ['trigger_reindex']
    
    def trigger_reindex(self, request, queryset):
        # This would trigger the actual indexing task
        self.message_user(request, 'Indexing task triggered.')
    trigger_reindex.short_description = 'Trigger re-indexing'
    
    def has_add_permission(self, request):
        return False
