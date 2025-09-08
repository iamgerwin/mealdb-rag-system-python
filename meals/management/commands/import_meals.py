from django.core.management.base import BaseCommand
from django.utils import timezone
from meals.models import Meal, Ingredient, IndexingTask, APIConfiguration
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from src.indexer import build_index


class Command(BaseCommand):
    help = 'Import meals from TheMealDB API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--from-cache',
            action='store_true',
            help='Load from existing cache/JSON file instead of fetching from API',
        )
        parser.add_argument(
            '--json-file',
            type=str,
            default='data/meals.json',
            help='Path to JSON file (if using --from-cache)',
        )

    def handle(self, *args, **options):
        task = IndexingTask.objects.create(
            status='running',
            started_at=timezone.now()
        )
        
        try:
            if options['from_cache']:
                self.stdout.write(self.style.SUCCESS(f'Loading from {options["json_file"]}...'))
                json_path = os.path.join(os.getcwd(), options['json_file'])
                
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        data = json.load(f)
                        meals_data = data.get('meals', []) if isinstance(data, dict) else data
                    self.stdout.write(self.style.SUCCESS(f'Loaded {len(meals_data)} meals from file'))
                else:
                    self.stdout.write(self.style.ERROR(f'File not found: {json_path}'))
                    task.status = 'failed'
                    task.error_message = f'File not found: {json_path}'
                    task.completed_at = timezone.now()
                    task.save()
                    return
            else:
                self.stdout.write(self.style.SUCCESS('Fetching meals from API...'))
                # Try to get API configuration
                try:
                    api_config = APIConfiguration.objects.get(provider='themealdb', is_active=True)
                    os.environ['THEMEALDB_API_KEY'] = api_config.api_key
                except APIConfiguration.DoesNotExist:
                    self.stdout.write(self.style.WARNING('No TheMealDB API config found, using default'))
                
                # Run the existing indexer
                build_index()
                
                # Load the generated JSON
                json_path = 'data/meals.json'
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        meals_data = json.load(f)
                else:
                    raise FileNotFoundError(f"Generated JSON not found at {json_path}")
            
            task.total_meals = len(meals_data)
            task.save()
            
            # Import meals into Django models
            imported = 0
            for meal_data in meals_data:
                try:
                    meal_id = int(meal_data.get('idMeal'))
                    
                    # Create or update meal
                    meal, created = Meal.objects.update_or_create(
                        meal_id=meal_id,
                        defaults={
                            'name': meal_data.get('strMeal', ''),
                            'category': meal_data.get('strCategory', ''),
                            'area': meal_data.get('strArea', ''),
                            'instructions': meal_data.get('strInstructions', ''),
                            'thumbnail': meal_data.get('strMealThumb', ''),
                            'tags': meal_data.get('strTags', ''),
                            'youtube_url': meal_data.get('strYoutube', ''),
                            'source_url': meal_data.get('strSource', ''),
                            'is_indexed': True,
                            'last_fetched': timezone.now()
                        }
                    )
                    
                    # Clear existing ingredients
                    meal.ingredients.all().delete()
                    
                    # Add ingredients
                    for i in range(1, 21):
                        ingredient_name = meal_data.get(f'strIngredient{i}', '').strip()
                        measure = meal_data.get(f'strMeasure{i}', '').strip()
                        
                        if ingredient_name:
                            Ingredient.objects.create(
                                meal=meal,
                                name=ingredient_name,
                                measure=measure,
                                order=i
                            )
                    
                    imported += 1
                    task.processed_meals = imported
                    
                    if imported % 10 == 0:
                        task.save()
                        self.stdout.write(f'Imported {imported}/{len(meals_data)} meals...')
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error importing meal {meal_data.get("idMeal")}: {e}'))
            
            task.status = 'completed'
            task.completed_at = timezone.now()
            task.save()
            
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {imported} meals'))
            
        except Exception as e:
            task.status = 'failed'
            task.error_message = str(e)
            task.completed_at = timezone.now()
            task.save()
            self.stdout.write(self.style.ERROR(f'Import failed: {e}'))