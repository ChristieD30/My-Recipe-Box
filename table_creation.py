"""
Create the database tables for the recipe box application
"""

import sqlite3
from datetime import datetime

def create_tables():
    conn = sqlite3.connect('recipe_box.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Drop existing tables (be careful with this in production!)
    # cursor.execute("DROP TABLE IF EXISTS favorites;")
    # cursor.execute("DROP TABLE IF EXISTS recipes;")
    # cursor.execute("DROP TABLE IF EXISTS users;")

    users_table_creation_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(25) NOT NULL,
        password VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(users_table_creation_query)

    recipes_table_creation_query = """
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        ingredients TEXT NOT NULL,
        instructions TEXT NOT NULL,
        category TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """
    cursor.execute(recipes_table_creation_query)

    favorites_table_creation_query = """
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        recipe_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (recipe_id) REFERENCES recipes (id)
    );
    """
    cursor.execute(favorites_table_creation_query)

    # Add a default admin user if it doesn't exist
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, email, name, password) VALUES (?, ?, ?, ?)",
        ('admin', 'admin@example.com', 'Admin', 'admin123')
    )

    # Get the admin user's ID
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    admin_id = cursor.fetchone()[0]

    default_recipes = [
    # -------------------
    # BREAKFAST (5)
        (
            'Vegan Pancakes',
            '1 cup flour\n1 tbsp sugar\n1 tbsp baking powder\n1/4 tsp salt\n1 cup almond milk\n1 tbsp vegetable oil\n1 tsp vanilla extract',
            '1. In a bowl, mix flour, sugar, baking powder, and salt.\n2. Add almond milk, vegetable oil, and vanilla, mix until smooth.\n3. Heat a non‑stick skillet over medium heat and pour batter into circles.\n4. Cook until bubbles form on the surface, then flip and cook until golden brown.',
            Category.BREAKFAST.value,
            admin_id
        ),
        (
            'Chia Pudding with Berries',
            '1/2 cup chia seeds\n2 cups almond milk\n1 tbsp maple syrup\n1 tsp vanilla extract\n1 cup mixed berries',
            '1. Mix chia seeds, almond milk, maple syrup, and vanilla in a jar.\n2. Refrigerate for at least 4 hours or overnight.\n3. Serve with fresh berries on top.',
            Category.BREAKFAST.value,
            admin_id
        ),
        (
            'Oatmeal with Banana and Almond Butter',
            '1 cup rolled oats\n2 cups almond milk\n1 banana, sliced\n2 tbsp almond butter\n1 tbsp maple syrup',
            '1. Cook oats with almond milk according to package instructions.\n2. Top with banana slices, almond butter, and maple syrup.',
            Category.BREAKFAST.value,
            admin_id
        ),
        (
            'Tofu Scramble',
            '1 block firm tofu, crumbled\n1 tbsp olive oil\n1/2 onion, diced\n1/2 bell pepper, diced\n1/2 tsp turmeric\nSalt and pepper to taste',
            '1. Heat olive oil in a pan and sauté onion and bell pepper until soft.\n2. Add crumbled tofu, turmeric, salt, and pepper.\n3. Cook for 5‑7 minutes, stirring occasionally.',
            Category.BREAKFAST.value,
            admin_id
        ),
        (
            'Apple Cinnamon Overnight Oats',
            '1/2 cup rolled oats\n1/2 cup almond milk\n1/2 apple, chopped\n1/4 tsp cinnamon\n1 tbsp maple syrup',
            '1. Combine all ingredients in a jar.\n2. Refrigerate overnight.\n3. Serve cold or at room temperature.',
            Category.BREAKFAST.value,
            admin_id
        ),

        # -------------------
        # DESSERT (5)
        (
            'Vegan Chocolate Chip Cookies',
            '2 1/4 cups all‑purpose flour\n1 cup vegan butter, softened\n3/4 cup organic sugar\n3/4 cup brown sugar\n1/4 cup applesauce (egg replacement)\n1 tsp vanilla extract\n1 tsp baking soda\n1/2 tsp salt\n2 cups dairy‑free chocolate chips',
            '1. Preheat oven to 375°F (190°C)\n2. Cream together vegan butter and sugars\n3. Mix in applesauce and vanilla\n4. Mix in dry ingredients\n5. Stir in dairy‑free chocolate chips\n6. Drop by rounded tablespoons onto ungreased baking sheets\n7. Bake for 10 to 12 minutes or until golden brown',
            Category.DESSERT.value,
            admin_id
        ),
        (
            'Vegan Chocolate Cake',
            '1 1/2 cups flour\n1 cup sugar\n1/2 cup cocoa powder\n1 tsp baking powder\n1/2 tsp baking soda\n1/2 tsp salt\n1 cup almond milk\n1/2 cup vegetable oil\n1 tsp vanilla extract\n1 tbsp vinegar',
            '1. Preheat oven to 350°F (175°C).\n2. In a large bowl, mix all dry ingredients.\n3. Add wet ingredients and mix until smooth.\n4. Pour into a greased cake pan and bake for 30‑35 minutes.',
            Category.DESSERT.value,
            admin_id
        ),
        (
            'Vegan Banana Bread',
            '3 ripe bananas, mashed\n1 cup sugar\n2 cups flour\n1 tsp baking soda\n1/2 tsp salt\n1/4 cup almond milk\n1/4 cup vegetable oil\n1 tsp vanilla extract',
            '1. Preheat oven to 350°F (175°C).\n2. Mix all ingredients in a bowl until smooth.\n3. Pour into a loaf pan and bake for 45‑50 minutes.',
            Category.DESSERT.value,
            admin_id
        ),
        (
            'Vegan Apple Crumble',
            '4 apples, peeled and sliced\n1 cup oats\n1/2 cup flour\n1/4 cup coconut sugar\n1/4 cup coconut oil',
            '1. Preheat oven to 350°F (175°C).\n2. Toss apples with a little sugar and cinnamon.\n3. Combine oats, flour, coconut sugar, and coconut oil for the crumble topping.\n4. Spread apples in a baking dish, sprinkle topping, bake for ~30 minutes until golden.',
            Category.DESSERT.value,
            admin_id
        ),
        (
            'Berry Parfait',
            '2 cups mixed berries\n1 cup yogurt (or vegan yogurt)\n1/4 cup granola\n1 tbsp honey or maple syrup',
            '1. Layer yogurt and berries in a glass.\n2. Top with granola and drizzle with honey or maple.\n3. Serve immediately.',
            Category.DESSERT.value,
            admin_id
        ),

        # -------------------
        # DINNER (5)
        (
            'Lentil Mushroom Bolognese',
            '1 lb whole grain spaghetti\n2 cups brown lentils, cooked\n16 oz mushrooms, finely chopped\n1 onion, diced\n4 cloves garlic, minced\n2 cans (14 oz each) crushed tomatoes\n3 tbsp olive oil\n2 tbsp nutritional yeast\n1 tsp dried basil\n1 tsp dried oregano\n1/2 tsp red pepper flakes\nSalt and pepper to taste',
            '1. Cook spaghetti according to package directions\n2. In a large pan, heat olive oil and sauté onion and garlic until soft\n3. Add mushrooms and cook until they release their moisture\n4. Add cooked lentils, tomatoes, and herbs\n5. Simmer for 20 minutes, stirring occasionally\n6. Add nutritional yeast and season with salt and pepper\n7. Serve over spaghetti with extra nutritional yeast if desired',
            'Main',
            admin_id
        ),
        (
            'Vegan Tacos',
            '12 corn tortillas\n2 cups cooked black beans\n1 avocado, sliced\n1 cup salsa\n1/2 cup cilantro, chopped\nLime wedges for serving',
            '1. Heat tortillas in a skillet.\n2. Fill with black beans, avocado slices, salsa, and cilantro.\n3. Serve with lime wedges.',
            Category.DINNER.value,
            admin_id
        ),
        (
            'Vegan Stir Fry',
            '2 cups broccoli florets\n1 cup bell peppers, sliced\n1 cup carrots, julienned\n2 tbsp soy sauce\n1 tbsp sesame oil\n2 cloves garlic, minced\n1 tbsp ginger, minced',
            '1. In a pan, heat sesame oil and sauté garlic and ginger.\n2. Add vegetables and stir‑fry for 5‑7 minutes.\n3. Add soy sauce and stir to coat.\n4. Serve over rice.',
            Category.DINNER.value,
            admin_id
        ),
        (
            'Grilled Salmon with Vegetables',
            '2 salmon fillets\n1 zucchini, sliced\n1 red bell pepper, sliced\n2 tbsp olive oil\nSalt, pepper, lemon wedges',
            '1. Preheat grill or grill pan to medium‑high heat.\n2. Brush salmon and vegetables with olive oil, season with salt and pepper.\n3. Grill salmon ~4‑5 minutes each side, grill vegetables until tender.\n4. Serve with lemon wedges.',
            Category.DINNER.value,
            admin_id
        ),
        (
            'Chicken and Rice Skillet',
            '1 lb chicken breast, diced\n1 cup rice\n2 cups chicken broth\n1 onion, chopped\n1 bell pepper, sliced\n1 tbsp olive oil\nSalt and pepper',
            '1. In a large skillet, heat olive oil and sauté onion and bell pepper until soft.\n2. Add chicken, cook until no longer pink.\n3. Add rice and chicken broth, bring to a boil, then reduce heat, cover, and simmer for 20 minutes.\n4. Season with salt and pepper and serve.',
            Category.DINNER.value,
            admin_id
        ),

        # -------------------
        # LUNCH (5)
        (
            'Vegan Avocado Toast',
            '2 slices whole wheat bread\n1 avocado\n1 tbsp lemon juice\nSalt and pepper to taste\n1 tbsp chili flakes (optional)',
            '1. Toast bread.\n2. Mash avocado with lemon juice, salt, and pepper.\n3. Spread on toast and sprinkle chili flakes.',
            Category.LUNCH.value,
            admin_id
        ),
        (
            'Vegan Hummus Wrap',
            '1 whole wheat tortilla\n1/2 cup hummus\n1 cup spinach\n1/2 cucumber, sliced\n1/4 cup shredded carrots',
            '1. Spread hummus on the tortilla.\n2. Add spinach, cucumber, and carrots.\n3. Roll up and serve.',
            Category.LUNCH.value,
            admin_id
        ),
        (
            'Quinoa & Black Bean Salad',
            '1 cup cooked quinoa\n1 cup black beans, drained and rinsed\n1/2 cup corn\n1/4 cup red onion, chopped\n2 tbsp lime juice\nSalt and pepper',
            '1. Combine quinoa, black beans, corn, and red onion in a bowl.\n2. Drizzle with lime juice and season with salt and pepper.\n3. Mix and serve chilled or at room temperature.',
            Category.LUNCH.value,
            admin_id
        ),
        (
            'Turkey Sandwich',
            '2 slices whole grain bread\n4 slices turkey breast\n1 slice cheddar cheese\nLettuce\nTomato\n1 tbsp mustard',
            '1. Spread mustard on bread slices.\n2. Stack turkey, cheese, lettuce, and tomato.\n3. Close sandwich and serve.',
            Category.LUNCH.value,
            admin_id
        ),
        (
            'Caprese Salad Sandwich',
            '2 slices ciabatta bread\nFresh mozzarella\nTomato slices\nBasil leaves\nBalsamic glaze',
            '1. On ciabatta bread, layer fresh mozzarella, tomato, and basil.\n2. Drizzle with balsamic glaze.\n3. Close sandwich and serve immediately.',
            Category.LUNCH.value,
            admin_id
        ),

        # -------------------
        # SALADS (5)
        (
            'Vegan Caesar Salad',
            '4 cups romaine lettuce\n1/2 cup vegan Caesar dressing\n1/4 cup croutons\n1 tbsp nutritional yeast',
            '1. Toss lettuce with dressing.\n2. Add croutons and nutritional yeast.\n3. Serve immediately.',
            Category.SALADS.value,
            admin_id
        ),
        (
            'Mediterranean Salad',
            '2 cups mixed greens\n1/2 cup cucumber, diced\n1/4 cup red onion, diced\n1/4 cup olives\n1/4 cup tomatoes, chopped\n1/4 cup balsamic vinaigrette',
            '1. Combine all ingredients in a large bowl.\n2. Toss with balsamic vinaigrette and serve.',
            Category.SALADS.value,
            admin_id
        ),
        (
            'Greek Salad',
            '2 cups chopped romaine\n1/2 cup cucumber, diced\n1/4 cup red onion, sliced\n1/4 cup feta cheese\n1/4 cup kalamata olives\n2 tbsp olive oil\n1 tbsp red wine vinegar',
            '1. Toss romaine, cucumber, red onion, feta, and olives.\n2. Drizzle with olive oil and red wine vinegar.\n3. Serve chilled.',
            Category.SALADS.value,
            admin_id
        ),
        (
            'Kale and Quinoa Salad',
            '2 cups kale, chopped\n1 cup cooked quinoa\n1/4 cup dried cranberries\n1/4 cup chopped almonds\n2 tbsp lemon juice\n1 tbsp olive oil',
            '1. Massage kale with a little lemon juice and olive oil.\n2. Add quinoa, cranberries, and almonds.\n3. Toss and serve.',
            Category.SALADS.value,
            admin_id
        ),
        (
            'Spinach Strawberry Salad',
            '2 cups baby spinach\n1/2 cup sliced strawberries\n1/4 cup sliced almonds\n2 tbsp poppy seed dressing',
            '1. Combine baby spinach, strawberries, and almonds in a bowl.\n2. Drizzle with poppy seed dressing and serve.',
            Category.SALADS.value,
            admin_id
        ),

        # -------------------
        # SOUP (5)
        (
            'Vegan Tomato Soup',
            '4 cups tomatoes, diced\n1 onion, chopped\n3 cloves garlic, minced\n1 cup vegetable broth\n1 tbsp olive oil\nSalt and pepper to taste',
            '1. Sauté onion and garlic in olive oil.\n2. Add tomatoes and vegetable broth.\n3. Simmer for 20 minutes, then blend until smooth.',
            Category.SOUP.value,
            admin_id
        ),
        (
            'Vegan Lentil Soup',
            '1 cup lentils\n1 onion, chopped\n2 carrots, chopped\n2 celery stalks, chopped\n4 cups vegetable broth\n1 tsp cumin\n1 tsp turmeric',
            '1. Sauté onion, carrots, and celery.\n2. Add lentils, vegetable broth, and spices.\n3. Simmer for 30 minutes until lentils are tender.',
            Category.SOUP.value,
            admin_id
        ),
        (
            'Chicken Noodle Soup',
            '1 tbsp olive oil\n1 onion, diced\n2 carrots, sliced\n2 celery stalks, sliced\n6 cups chicken broth\n1 lb shredded chicken\n2 cups egg noodles\nSalt and pepper',
            '1. Heat olive oil in a large pot, sauté onion, carrots, and celery until soft.\n2. Add chicken broth and shredded chicken; bring to a boil.\n3. Add egg noodles, reduce heat, simmer until noodles are tender. Season with salt & pepper.',
            Category.SOUP.value,
            admin_id
        ),
        (
            'Butternut Squash Soup',
            '1 butternut squash (peeled & cubed)\n1 onion, chopped\n2 cups vegetable broth\n1/2 cup coconut milk\n1 tbsp olive oil\nSalt and pepper',
            '1. Preheat oven to 400°F (200°C). Roast squash and onion with olive oil until soft.\n2. Transfer to a pot, add vegetable broth, simmer 10 minutes.\n3. Blend until smooth. Stir in coconut milk. Season and serve.',
            Category.SOUP.value,
            admin_id
        ),
        (
            'Minestrone Soup',
            '1 tbsp olive oil\n1 onion, diced\n2 carrots, diced\n2 celery stalks, diced\n1 zucchini, diced\n1 can diced tomatoes\n4 cups vegetable broth\n1 cup pasta\nSalt, pepper, Italian herbs',
            '1. Heat olive oil, sauté onion, carrots, celery until soft.\n2. Add zucchini, tomatoes, vegetable broth, and pasta. Simmer until pasta is tender.\n3. Season with salt, pepper, and Italian herbs. Serve hot.',
            Category.SOUP.value,
            admin_id
        ),

        # -------------------
        # SNACKS (5)
        (
            'Vegan Energy Balls',
            '1 cup oats\n1/2 cup peanut butter\n1/4 cup maple syrup\n1/2 cup dark chocolate chips\n1/4 cup chia seeds',
            '1. Mix all ingredients in a bowl.\n2. Roll into small balls.\n3. Chill in the fridge for 1 hour before serving.',
            Category.SNACKS.value,
            admin_id
        ),
        (
            'Vegan Granola Bars',
            '2 cups oats\n1/4 cup maple syrup\n1/4 cup peanut butter\n1/2 cup dried fruit\n1/4 cup seeds or nuts',
            '1. Preheat oven to 350°F (175°C).\n2. Mix all ingredients and press into a baking pan.\n3. Bake for 20‑25 minutes.',
            Category.SNACKS.value,
            admin_id
        ),
        (
            'Homemade Popcorn',
            '1/4 cup popcorn kernels\n1 tbsp olive oil\nSalt to taste',
            '1. Heat olive oil in a large pot over medium heat.\n2. Add popcorn kernels, cover, and shake pot occasionally until popping slows.\n3. Remove from heat, season with salt, and serve.',
            Category.SNACKS.value,
            admin_id
        ),
        (
            'Fruit & Nut Trail Mix',
            '1 cup almonds\n1 cup cashews\n1/2 cup dried cranberries\n1/2 cup dark chocolate pieces\n1/4 cup pumpkin seeds',
            '1. Combine all ingredients in a bowl.\n2. Store in an airtight container and serve as needed.',
            Category.SNACKS.value,
            admin_id
        ),
        (
            'Guacamole & Veggie Sticks',
            '2 ripe avocados\n1/4 cup red onion, finely chopped\n1 tbsp lime juice\nSalt and pepper\nCarrot sticks, cucumber sticks, bell pepper slices',
            '1. Mash avocados with red onion, lime juice, salt and pepper.\n2. Serve with fresh veggie sticks.',
            Category.SNACKS.value,
            admin_id
        ),
    ]


    # Insert each default recipe only if it doesn't already exist for this user
    for name, ingredients, instructions, category, user_id in default_recipes:
        cursor.execute(
            "SELECT 1 FROM recipes WHERE name = ? AND user_id = ?",
            (name, user_id)
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO recipes (name, ingredients, instructions, category, user_id) VALUES (?, ?, ?, ?, ?)",
                (name, ingredients, instructions, category, user_id)
            )

    conn.commit()
    conn.close()
    print("Database tables created successfully with default admin user and recipes")

if __name__ == '__main__':
    create_tables()