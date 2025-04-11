import requests
from PIL import Image
from io import BytesIO
import os

def download_uol_logo():
    try:
        # Criar pasta assets se não existir
        if not os.path.exists('assets'):
            os.makedirs('assets')
        
        # URL do logo da UOL
        url = "https://logodownload.org/wp-content/uploads/2014/09/uol-logo-1.png"
        
        # Fazer o download da imagem
        response = requests.get(url)
        if response.status_code == 200:
            # Abrir a imagem baixada
            img = Image.open(BytesIO(response.content))
            
            # Converter para RGBA para garantir transparência
            img = img.convert('RGBA')
            
            # Redimensionar mantendo a proporção
            max_width = 200
            aspect_ratio = img.height / img.width
            new_height = int(max_width * aspect_ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Salvar na pasta assets
            img.save(os.path.join('assets', 'uol_logo.png'), 'PNG')
            print("Logo da UOL baixado e salvo com sucesso!")
            
            # Criar o ícone também
            from create_icon import create_uol_icon
            create_uol_icon()
            
        else:
            print("Erro ao baixar o logo da UOL")
    
    except Exception as e:
        print(f"Erro: {e}")
        print("Tentando usar logo alternativo...")
        
        try:
            # Criar um logo simples com texto
            width = 200
            height = 80
            img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            
            # Salvar na pasta assets
            img.save(os.path.join('assets', 'uol_logo.png'), 'PNG')
            print("Logo alternativo criado com sucesso!")
            
            # Criar o ícone
            from create_icon import create_uol_icon
            create_uol_icon()
            
        except Exception as e:
            print(f"Erro ao criar logo alternativo: {e}")

if __name__ == "__main__":
    download_uol_logo() 