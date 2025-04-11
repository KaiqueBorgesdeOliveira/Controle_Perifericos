import requests
from PIL import Image
from io import BytesIO
import os

def download_and_process_logo():
    try:
        # Criar pasta assets se não existir
        if not os.path.exists('assets'):
            os.makedirs('assets')
        
        # URL da imagem do Grupo UOL
        url = "https://logodownload.org/wp-content/uploads/2014/09/grupo-uol-logo-0.png"
        
        # Baixar a imagem
        response = requests.get(url)
        if response.status_code == 200:
            # Abrir a imagem baixada
            logo = Image.open(BytesIO(response.content))
            
            # Converter para RGBA para garantir canal alpha
            logo = logo.convert('RGBA')
            
            # Processar pixels para remover fundo branco
            data = logo.getdata()
            new_data = []
            
            for item in data:
                # Se o pixel for branco ou próximo do branco, tornar transparente
                if item[0] > 240 and item[1] > 240 and item[2] > 240:
                    new_data.append((255, 255, 255, 0))
                else:
                    new_data.append(item)
            
            # Atualizar os dados da imagem
            logo.putdata(new_data)
            
            # Criar uma nova imagem com fundo transparente
            width = 200
            height = 80
            new_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            
            # Redimensionar mantendo a proporção
            logo.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Calcular posição para centralizar
            x = (width - logo.width) // 2
            y = (height - logo.height) // 2
            
            # Colar a imagem processada na imagem base
            new_image.paste(logo, (x, y), logo)
            
            # Salvar na pasta assets
            new_image.save(os.path.join('assets', 'uol_logo.png'), 'PNG')
            print("Logo processado e salvo com sucesso!")
            
            # Criar o ícone
            from create_icon import create_uol_icon
            create_uol_icon()
        else:
            print("Erro ao baixar a imagem")
            
    except Exception as e:
        print(f"Erro ao processar o logo: {e}")

if __name__ == "__main__":
    download_and_process_logo() 