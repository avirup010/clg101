import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLineEdit, QPushButton, QLabel, 
                           QScrollArea, QFrame, QGridLayout, QSplitter)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QPoint, QParallelAnimationGroup, QSequentialAnimationGroup
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QPixmap, QImage, QGraphicsDropShadowEffect, QGraphicsOpacityEffect

class ModernButton(QPushButton):
    def __init__(self, text, parent=None, primary=True):
        super().__init__(text, parent)
        self.primary = primary
        self.setup_ui()
        
    def setup_ui(self):
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #6200EA;
                    color: white;
                    border-radius: 8px;
                    padding: 12px 20px;
                    font-weight: bold;
                    font-size: 14px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #7C4DFF;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                }
                QPushButton:pressed {
                    background-color: #5502C8;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #E0E0E0;
                    color: #424242;
                    border-radius: 8px;
                    padding: 12px 20px;
                    font-weight: bold;
                    font-size: 14px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #EEEEEE;
                }
                QPushButton:pressed {
                    background-color: #BDBDBD;
                }
            """)

class ModernLineEdit(QLineEdit):
    def __init__(self, parent=None, placeholder=""):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setup_ui()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 12px 15px;
                background-color: #FAFAFA;
                color: #212121;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit:focus {
                border: 2px solid #7C4DFF;
                background-color: white;
            }
        """)

class IngredientTag(QFrame):
    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.setup_ui()
        
    def setup_ui(self):
        self.setObjectName("ingredientTag")
        self.setStyleSheet("""
            #ingredientTag {
                background-color: #EDE7F6;
                border-radius: 20px;
                padding: 8px;
                margin: 4px;
                border: none;
            }
            QLabel {
                color: #4527A0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton {
                background-color: #7C4DFF;
                color: white;
                border-radius: 10px;
                border: none;
                font-size: 14px;
                font-weight: bold;
                padding: 4px;
                margin: 0px;
                min-width: 20px;
                max-width: 20px;
                min-height: 20px;
                max-height: 20px;
            }
            QPushButton:hover {
                background-color: #6200EA;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 5, 8, 5)
        layout.setSpacing(8)
        
        label = QLabel(self.text)
        remove_btn = QPushButton("×")
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.clicked.connect(self.remove_tag)
        
        layout.addWidget(label)
        layout.addWidget(remove_btn)
        
    def remove_tag(self):
        # Animation for removal
        animation = QPropertyAnimation(self, b"geometry")
        animation.setDuration(300)
        animation.setStartValue(self.geometry())
        animation.setEndValue(QRect(self.geometry().x(), self.geometry().y(), 0, self.geometry().height()))
        animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        def finish_removal():
            parent_widget = self.parent()
            if hasattr(parent_widget, 'remove_ingredient'):
                parent_widget.remove_ingredient(self.text)
            self.deleteLater()
            
        animation.finished.connect(finish_removal)
        animation.start()

class RecipeCard(QFrame):
    def __init__(self, recipe_data):
        super().__init__()
        self.recipe_data = recipe_data
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        self.setObjectName("recipeCard")
        self.setStyleSheet("""
            #recipeCard {
                background-color: white;
                border-radius: 12px;
                border: none;
            }
            #titleLabel {
                color: #212121;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
                font-size: 16px;
            }
            #matchLabel {
                color: #6200EA;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
                font-size: 12px;
            }
            .sectionLabel {
                color: #424242;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-weight: bold;
                font-size: 14px;
                margin-top: 10px;
            }
            .contentText {
                color: #616161;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        
        # Shadow effect
        self.setGraphicsEffect(None)  # Clear any existing effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Recipe title
        self.title_label = QLabel(self.recipe_data.get("title", "Recipe"))
        self.title_label.setObjectName("titleLabel")
        self.title_label.setWordWrap(True)
        
        # Match information
        match_count = self.recipe_data.get("matching_count", 0)
        total_count = len(self.recipe_data.get("ingredients", []))
        match_label = QLabel(f"{match_count} of {total_count} ingredients matched")
        match_label.setObjectName("matchLabel")
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #E0E0E0; min-height: 1px; max-height: 1px;")
        
        # Ingredients section
        ingredients_label = QLabel("Ingredients")
        ingredients_label.setProperty("class", "sectionLabel")
        
        ingredients_text = QLabel()
        ingredients_text.setProperty("class", "contentText")
        ingredients_text.setWordWrap(True)
        
        # Highlight matching ingredients
        ingredients_html = ""
        for ing in self.recipe_data.get("ingredients", []):
            if ing.lower() in [i.lower() for i in self.recipe_data.get("matched_ingredients", [])]:
                ingredients_html += f"• <span style='color: #6200EA; font-weight: bold;'>{ing}</span><br>"
            else:
                ingredients_html += f"• {ing}<br>"
        
        ingredients_text.setText(ingredients_html)
        
        # Instructions section
        instructions_label = QLabel("Instructions")
        instructions_label.setProperty("class", "sectionLabel")
        
        instructions_text = QLabel(self.recipe_data.get("instructions", "No instructions available."))
        instructions_text.setProperty("class", "contentText")
        instructions_text.setWordWrap(True)
        
        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(match_label)
        layout.addWidget(divider)
        layout.addWidget(ingredients_label)
        layout.addWidget(ingredients_text)
        layout.addWidget(instructions_label)
        layout.addWidget(instructions_text)
        
        self.setMinimumHeight(400)
        self.setMaximumHeight(500)
        self.setMinimumWidth(340)
        
    def setup_animations(self):
        # Scale animation
        self.scaleAnimation = QPropertyAnimation(self, b"geometry")
        self.scaleAnimation.setDuration(200)
        self.scaleAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Shadow animation - we need to implement this through property animation
        self.shadowAnimation = QPropertyAnimation(self.graphicsEffect(), b"blurRadius")
        self.shadowAnimation.setDuration(200)
        
        # Group animations
        self.enterAnimGroup = QParallelAnimationGroup()
        self.enterAnimGroup.addAnimation(self.scaleAnimation)
        self.enterAnimGroup.addAnimation(self.shadowAnimation)
        
        self.leaveAnimGroup = QParallelAnimationGroup()
        self.leaveAnimGroup.addAnimation(QPropertyAnimation(self, b"geometry"))
        self.leaveAnimGroup.addAnimation(QPropertyAnimation(self.graphicsEffect(), b"blurRadius"))
        
    def enterEvent(self, event):
        # Save original geometry
        original_geometry = self.geometry()
        
        # Create a slightly larger geometry
        new_geometry = QRect(
            original_geometry.x() - 5,
            original_geometry.y() - 5,
            original_geometry.width() + 10,
            original_geometry.height() + 10
        )
        
        # Set up animations
        self.scaleAnimation.setStartValue(original_geometry)
        self.scaleAnimation.setEndValue(new_geometry)
        
        self.shadowAnimation.setStartValue(20)
        self.shadowAnimation.setEndValue(30)
        
        # Start animation group
        self.enterAnimGroup.start()
        
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        # Get current geometry
        current_geometry = self.geometry()
        
        # Create the target geometry (original size)
        target_geometry = QRect(
            current_geometry.x() + 5,
            current_geometry.y() + 5,
            current_geometry.width() - 10,
            current_geometry.height() - 10
        )
        
        # Set up new animations for leaving
        geometry_anim = QPropertyAnimation(self, b"geometry")
        geometry_anim.setDuration(200)
        geometry_anim.setStartValue(current_geometry)
        geometry_anim.setEndValue(target_geometry)
        geometry_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        shadow_anim = QPropertyAnimation(self.graphicsEffect(), b"blurRadius")
        shadow_anim.setDuration(200)
        shadow_anim.setStartValue(30)
        shadow_anim.setEndValue(20)
        
        # Clear and rebuild the leave animation group
        self.leaveAnimGroup = QParallelAnimationGroup()
        self.leaveAnimGroup.addAnimation(geometry_anim)
        self.leaveAnimGroup.addAnimation(shadow_anim)
        
        # Start animation group
        self.leaveAnimGroup.start()
        
        super().leaveEvent(event)

class RecipeFinderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ingredients = []
        self.recipes = self.load_sample_recipes()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Recipe Finder")
        self.setMinimumSize(1100, 800)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9E9E9E;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QLabel#emptyMessage {
                color: #9E9E9E;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6200EA, stop:1 #7C4DFF);
            min-height: 140px;
        """)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(50, 30, 50, 30)
        
        title_label = QLabel("Recipe Finder")
        title_label.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
        """)
        
        subtitle_label = QLabel("Find delicious recipes with ingredients you have at home")
        subtitle_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8);
            font-size: 16px;
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        # Main content area
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            background-color: #FAFAFA;
            border-top-left-radius: 20px;
            border-top-right-radius: 20px;
            margin-top: -20px;
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(30)
        
        # Search section
        search_widget = QWidget()
        search_widget.setStyleSheet("""
            background-color: white;
            border-radius: 12px;
            padding: 20px;
        """)
        search_layout = QVBoxLayout(search_widget)
        
        search_title = QLabel("What ingredients do you have?")
        search_title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #212121;
            margin-bottom: 10px;
        """)
        
        # Input area
        input_layout = QHBoxLayout()
        self.ingredient_input = ModernLineEdit(placeholder="Type an ingredient and press Enter")
        self.ingredient_input.returnPressed.connect(self.add_ingredient)
        
        add_button = ModernButton("Add", primary=True)
        add_button.setFixedWidth(100)
        add_button.clicked.connect(self.add_ingredient)
        
        input_layout.addWidget(self.ingredient_input)
        input_layout.addWidget(add_button)
        
        # Tags area
        tags_scroll = QScrollArea()
        tags_scroll.setWidgetResizable(True)
        tags_scroll.setStyleSheet("background-color: transparent;")
        
        self.tags_container = QWidget()
        self.tags_container.setStyleSheet("background-color: transparent;")
        self.tags_layout = QHBoxLayout(self.tags_container)
        self.tags_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tags_layout.setContentsMargins(0, 10, 0, 10)
        self.tags_layout.setSpacing(5)
        
        tags_scroll.setWidget(self.tags_container)
        tags_scroll.setMaximumHeight(80)
        
        # Find recipes button
        self.find_button = ModernButton("Find Recipes", primary=True)
        self.find_button.setFixedWidth(200)
        self.find_button.clicked.connect(self.search_recipes)
        find_button_layout = QHBoxLayout()
        find_button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        find_button_layout.addWidget(self.find_button)
        
        # Add all to search widget
        search_layout.addWidget(search_title)
        search_layout.addLayout(input_layout)
        search_layout.addWidget(tags_scroll)
        search_layout.addLayout(find_button_layout)
        
        # Results section
        results_title = QLabel("Recipes")
        results_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #212121;
            margin-top: 10px;
        """)
        
        # Results container
        results_scroll = QScrollArea()
        results_scroll.setWidgetResizable(True)
        results_scroll.setStyleSheet("""
            background-color: transparent;
            border: none;
        """)
        
        self.results_container = QWidget()
        self.results_container.setStyleSheet("background-color: transparent;")
        self.results_layout = QGridLayout(self.results_container)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(20)
        
        results_scroll.setWidget(self.results_container)
        
        # Add placeholder message
        self.empty_message = QLabel("Add ingredients and click 'Find Recipes' to see matching recipes")
        self.empty_message.setObjectName("emptyMessage")
        self.empty_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_layout.addWidget(self.empty_message, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        
        # Add all sections to content layout
        content_layout.addWidget(search_widget)
        content_layout.addWidget(results_title)
        content_layout.addWidget(results_scroll, 1)
        
        # Assemble the main UI
        main_layout.addWidget(header_widget)
        main_layout.addWidget(content_widget, 1)
        
        self.setCentralWidget(central_widget)
        
    def add_ingredient(self):
        ingredient = self.ingredient_input.text().strip().lower()
        if ingredient and ingredient not in self.ingredients:
            self.ingredients.append(ingredient)
            
            # Add tag to UI
            tag = IngredientTag(ingredient, self)
            self.tags_layout.addWidget(tag)
            
            # Clear input
            self.ingredient_input.clear()
            
            # Animate tag appearing
            tag.setVisible(False)
            
            # Start position animation (appear from below)
            pos_animation = QPropertyAnimation(tag, b"pos")
            pos_animation.setDuration(300)
            pos_animation.setStartValue(QPoint(tag.pos().x(), tag.pos().y() + 20))
            pos_animation.setEndValue(tag.pos())
            pos_animation.setEasingCurve(QEasingCurve.Type.OutQuint)
            
            # Opacity animation
            opacity_effect = QGraphicsOpacityEffect(tag)
            tag.setGraphicsEffect(opacity_effect)
            opacity_animation = QPropertyAnimation(opacity_effect, b"opacity")
            opacity_animation.setDuration(300)
            opacity_animation.setStartValue(0)
            opacity_animation.setEndValue(1)
            opacity_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # Animation group
            animation_group = QParallelAnimationGroup()
            animation_group.addAnimation(pos_animation)
            animation_group.addAnimation(opacity_animation)
            
            # Show tag and start animation
            tag.setVisible(True)
            animation_group.start()
    
    def remove_ingredient(self, ingredient):
        if ingredient in self.ingredients:
            self.ingredients.remove(ingredient)
    
    def search_recipes(self):
        # Clear existing results
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.ingredients:
            self.empty_message = QLabel("Add ingredients and click 'Find Recipes' to see matching recipes")
            self.empty_message.setObjectName("emptyMessage")
            self.empty_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.addWidget(self.empty_message, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
            return
        
        # Find matching recipes
        matching_recipes = []
        for recipe in self.recipes:
            recipe_ingredients = [ing.lower() for ing in recipe.get("ingredients", [])]
            matching_count = 0
            matched_ingredients = []
            
            for ing in self.ingredients:
                if ing in recipe_ingredients:
                    matching_count += 1
                    matched_ingredients.append(ing)
            
            if matching_count > 0:  # At least one ingredient matches
                recipe_copy = recipe.copy()
                recipe_copy["matching_count"] = matching_count
                recipe_copy["matched_ingredients"] = matched_ingredients
                matching_recipes.append(recipe_copy)
        
        # Sort by most matching ingredients
        matching_recipes.sort(key=lambda x: x["matching_count"], reverse=True)
        
        # Display results
        if not matching_recipes:
            no_results = QLabel("No recipes found with your ingredients. Try adding more!")
            no_results.setObjectName("emptyMessage")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.results_layout.addWidget(no_results, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
            return
        
        # Create recipe cards with animations
        animation_group = QSequentialAnimationGroup()
        
        for i, recipe in enumerate(matching_recipes):
            row = i // 3
            col = i % 3
            
            recipe_card = RecipeCard(recipe)
            # Initially invisible
            recipe_card.setVisible(False)
            self.results_layout.addWidget(recipe_card, row, col)
            
            # Create card appearance animation
            opacity_effect = QGraphicsOpacityEffect(recipe_card)
            recipe_card.setGraphicsEffect(opacity_effect)
            opacity_effect.setOpacity(0)
            
            opacity_anim = QPropertyAnimation(opacity_effect, b"opacity")
            opacity_anim.setDuration(200)
            opacity_anim.setStartValue(0)
            opacity_anim.setEndValue(1)
            opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # Set up a position animation
            pos_anim = QPropertyAnimation(recipe_card, b"pos")
            pos_anim.setDuration(200)
            
            # Store the original position we'll animate to
            original_pos = recipe_card.pos()
            # Start position (coming from below)
            start_pos = QPoint(original_pos.x(), original_pos.y() + 30)
            
            pos_anim.setStartValue(start_pos)
            pos_anim.setEndValue(original_pos)
            pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            # Create a parallel animation group for this card
            card_anim_group = QParallelAnimationGroup()
            card_anim_group.addAnimation(opacity_anim)
            card_anim_group.addAnimation(pos_anim)
            
            # Function to show the card before animation starts
            def make_show_card(card):
                def show_card():
                    card.setVisible(True)
                return show_card
                
            card_anim_group.aboutToStart.connect(make_show_card(recipe_card))
            
            # Add to sequential group for staggered appearance
            animation_group.addAnimation(card_anim_group)
        
        # Start the animations
        animation_group.start()
    
    def load_sample_recipes(self):
        """Load sample recipes for demonstration purposes"""
        return [
            {
                "title": "Spaghetti Carbonara",
                "ingredients": ["pasta", "eggs", "bacon", "parmesan cheese", "black pepper", "salt", "olive oil", "garlic"],
                "instructions": "1. Cook pasta according to package directions until al dente.\n2. In a large skillet, cook bacon until crispy. Add minced garlic and cook for 30 seconds.\n3. In a bowl, whisk eggs, grated parmesan, and black pepper.\n4. Drain pasta, reserving 1/2 cup pasta water.\n5. Working quickly, add hot pasta to the skillet with bacon. Remove from heat.\n6. Pour egg mixture over pasta and toss quickly to coat (the heat will cook the eggs).\n7. Add pasta water as needed to create a silky sauce.\n8. Season with salt to taste and serve immediately with extra cheese and pepper."
            },
            {
                "title": "Classic Margherita Pizza",
                "ingredients": ["pizza dough", "tomatoes", "mozzarella cheese", "basil", "olive oil", "salt", "garlic"],
                "instructions": "1. Preheat oven to 475°F (245°C) with a pizza stone if available.\n2. Roll out the pizza dough on a floured surface.\n3. Rub the dough with olive oil and minced garlic.\n4. Arrange thinly sliced tomatoes and torn mozzarella on top.\n5. Bake for 10-12 minutes until crust is golden and cheese is bubbly.\n6. Remove from oven and immediately top with fresh basil leaves.\n7. Drizzle with olive oil and sprinkle with salt before serving."
            },
            {
                "title": "Thai-Inspired Vegetable Stir Fry",
                "ingredients": ["rice", "broccoli", "carrots", "bell peppers", "onions", "garlic", "soy sauce", "vegetable oil", "ginger", "lime", "peanuts"],
                "instructions": "1. Cook rice according to package directions.\n2. In a small bowl, mix soy sauce, lime juice, and a pinch of sugar.\n3. Heat oil in a wok or large skillet over high heat.\n4. Add minced garlic and ginger, stir for 30 seconds.\n5. Add vegetables, starting with the firmest (carrots, broccoli), then onions and peppers.\n6. Stir-fry until vegetables are tender-crisp, about 5-7 minutes.\n7. Pour sauce over vegetables and toss to coat.\n8. Serve over rice and garnish with chopped peanuts and lime wedges."
            },
            {
                "title": "Perfect Chocolate Chip Cookies",
                "ingredients": ["flour", "butter", "sugar", "brown sugar", "eggs", "vanilla extract", "baking soda", "salt", "chocolate chips"],
                "instructions": "1. Preheat oven to 375°F (190°C).\n2. In a bowl, cream together softened butter, white sugar, and brown sugar until light and fluffy.\n3. Beat in eggs one at a time, then stir in vanilla.\n4. In a separate bowl, combine flour, baking soda, and salt.\n5. Gradually blend dry mixture into the wet ingredients.\n6. Fold in chocolate chips.\n7. Drop rounded tablespoons of dough onto ungreased baking sheets.\n8. Bake for 9-11 minutes or until golden brown.\n9. Let stand on baking sheet for 2 minutes before transferring to wire racks to cool completely."
            },
            {
                "title": "Creamy Chicken Curry",
                "ingredients": ["chicken", "onions", "garlic", "ginger", "curry powder", "coconut milk", "tomatoes", "rice", "cilantro", "vegetable oil", "salt"],
                "instructions": "1. Heat oil in a large pot over medium heat.\n2. Add diced onions and cook until translucent, about 5 minutes.\n3. Add minced garlic and ginger, cook for 1 minute until fragrant.\n4. Stir in curry powder and cook for 30 seconds.\n5. Add diced chicken and cook until no longer pink on the outside.\n6. Add diced tomatoes and coconut milk, bring to a simmer.\n7. Reduce heat and simmer uncovered for 20-25 minutes until chicken is cooked through and sauce thickens.\n8. Season with salt to taste.\n9. Serve over cooked rice and garnish with fresh cilantro."
            },
            {
                "title": "Classic Mushroom Risotto",
                "ingredients": ["arborio rice", "mushrooms", "onions", "garlic", "white wine", "vegetable broth", "parmesan cheese", "butter", "olive oil", "thyme"],
                "instructions": "1. Heat olive oil and butter in a large pan over medium heat.\n2. Add diced onions and cook until translucent, about 3-4 minutes.\n3. Add minced garlic and cook for 30 seconds until fragrant.\n4. Add sliced mushrooms and thyme, cook until mushrooms are golden brown.\n5. Add arborio rice and stir to coat with oil for 1-2 minutes.\n6. Pour in white wine and stir until absorbed.\n7. Add hot vegetable broth one ladle at a time, stirring constantly and allowing each addition to be absorbed before adding more.\n8. Continue for about 18-20 minutes until rice is creamy and al dente.\n9. Remove from heat, stir in grated parmesan cheese and a knob of butter.\n10. Season with salt and pepper to taste. Serve immediately garnished with thyme."
            },
            {
                "title": "Avocado Toast with Poached Egg",
                "ingredients": ["bread", "avocado", "eggs", "cherry tomatoes", "feta cheese", "lemon juice", "red pepper flakes", "salt", "olive oil"],
                "instructions": "1. Toast bread until golden and crisp.\n2. In a small bowl, mash avocado with lemon juice and salt.\n3. Bring a pot of water to a simmer for poaching eggs. Add a splash of vinegar.\n4. Gently crack an egg into a small cup, then slide into the simmering water.\n5. Poach for 3-4 minutes for a runny yolk.\n6. Spread mashed avocado on toast.\n7. Top with poached egg, halved cherry tomatoes, and crumbled feta.\n8. Drizzle with olive oil and sprinkle with red pepper flakes.\n9. Season with additional salt and black pepper as desired."
            },
            {
                "title": "Simple Vegetable Soup",
                "ingredients": ["carrots", "celery", "onions", "potatoes", "garlic", "vegetable broth", "thyme", "bay leaves", "salt", "pepper", "olive oil"],
                "instructions": "1. Heat olive oil in a large pot over medium heat.\n2. Add diced onions, carrots, and celery (mirepoix) and cook until softened, about 5 minutes.\n3. Add minced garlic and cook for 30 seconds.\n4. Add diced potatoes, vegetable broth, thyme, and bay leaves.\n5. Bring to a boil, then reduce to a simmer.\n6. Cover and cook for 20-25 minutes until vegetables are tender.\n7. Remove bay leaves and thyme sprigs.\n8. Season with salt and pepper to taste.\n9. Serve hot, garnished with fresh herbs if desired."
            }
        ]

    def load_recipes_from_file(self, filename):
        """Load recipes from a JSON file"""
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            # Return sample recipes if file can't be loaded
            return self.load_sample_recipes()

    def save_recipes_to_file(self, filename):
        """Save current recipes to a JSON file"""
        with open(filename, 'w') as file:
            json.dump(self.recipes, file, indent=4)

def main():
    app = QApplication(sys.argv)
    window = RecipeFinderApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
