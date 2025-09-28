"""
Загрузчик HTML шаблонов
"""
import os
from pathlib import Path

class TemplateLoader:
    """Класс для загрузки HTML шаблонов"""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = Path(templates_dir)
    
    def load_template(self, template_name: str) -> str:
        """Загружает шаблон из файла"""
        template_path = self.templates_dir / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Шаблон {template_name} не найден")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def render_template(self, template_name: str, **context) -> str:
        """Рендерит шаблон с контекстом"""
        template_content = self.load_template(template_name)
        
        # Простая замена переменных
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            if isinstance(value, (list, dict)):
                import json
                template_content = template_content.replace(placeholder, json.dumps(value, ensure_ascii=False))
            else:
                template_content = template_content.replace(placeholder, str(value))
        
        return template_content

# Глобальный экземпляр
template_loader = TemplateLoader()