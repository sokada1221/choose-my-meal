import os
import sys
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.progress import track

from places_client import PlacesClient
from menu_analyzer import MenuAnalyzer

# Load environment variables
load_dotenv()

def main():
    console = Console()
    
    # Check for API keys
    google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    if not google_maps_key or not gemini_key:
        console.print("[bold red]Error:[/bold red] Missing API keys. Please check your .env file.")
        return

    # Initialize clients
    places_client = PlacesClient(google_maps_key)
    menu_analyzer = MenuAnalyzer(gemini_key)

    console.print("[bold green]Restaurants Menu Researcher[/bold green]")
    console.print("Enter restaurant names (comma separated) or type 'exit' to quit.")
    
    while True:
        user_input = console.input("\n[bold yellow]Restaurants > [/bold yellow]")
        
        if user_input.lower() == 'exit':
            break
            
        restaurant_names = [name.strip() for name in user_input.split(',') if name.strip()]
        
        if not restaurant_names:
            continue

        results = []
        
        for name in track(restaurant_names, description="Researching..."):
            # 1. Find Place
            place_id = places_client.find_place(name)
            
            if not place_id:
                results.append({
                    "name": name,
                    "rating": "N/A",
                    "count": 0,
                    "menu": ["Restaurant not found"]
                })
                continue
                
            # 2. Get Details
            details = places_client.get_place_details(place_id)
            real_name = details.get('name', name)
            rating = details.get('rating', 'N/A')
            count = details.get('user_ratings_total', 0)
            reviews_data = details.get('reviews', [])
            reviews_text = []
            for r in reviews_data:
                # Handle both legacy and new API formats just in case, but primarily new
                text_obj = r.get('text')
                if isinstance(text_obj, dict):
                    reviews_text.append(text_obj.get('text', ''))
                elif isinstance(text_obj, str):
                    reviews_text.append(text_obj)
            
            # 3. Analyze Menu
            recommended_menu = menu_analyzer.analyze_reviews(real_name, reviews_text)
            
            results.append({
                "name": real_name,
                "rating": rating,
                "count": count,
                "menu": recommended_menu
            })

        # Sort by rating (handling N/A)
        results.sort(key=lambda x: x['rating'] if isinstance(x['rating'], (int, float)) else -1, reverse=True)

        # Display Table
        table = Table(title="Restaurant Recommendations")
        table.add_column("Restaurant Name", style="cyan", no_wrap=True)
        table.add_column("Rating", style="magenta")
        table.add_column("Reviews", style="green")
        table.add_column("Recommended Menu", style="yellow")

        for r in results:
            menu_str = ", ".join(r['menu'])
            table.add_row(
                r['name'],
                str(r['rating']),
                str(r['count']),
                menu_str
            )

        console.print(table)

if __name__ == "__main__":
    main()
