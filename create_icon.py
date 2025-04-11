from PIL import Image
import os

def create_uol_icon():
    try:
        # Garantir que a pasta assets existe
        if not os.path.exists('assets'):
            os.makedirs('assets')
        
        # Verificar se o arquivo do logo existe
        logo_path = os.path.join('assets', 'uol_logo.png')
        if not os.path.exists(logo_path):
            print("Arquivo uol_logo.png não encontrado na pasta assets!")
            return
        
        # Abrir a imagem do logo
        img = Image.open(logo_path)
        
        # Lista de tamanhos para o ícone
        sizes = [(16,16), (32,32), (48,48), (64,64), (128,128)]
        
        # Criar uma lista para armazenar as imagens redimensionadas
        icon_images = []
        
        # Redimensionar a imagem para cada tamanho necessário
        for size in sizes:
            resized_img = img.copy()
            resized_img.thumbnail(size, Image.Resampling.LANCZOS)
            icon_images.append(resized_img)
        
        # Salvar como arquivo .ico na pasta assets
        icon_path = os.path.join('assets', 'uol_icon.ico')
        icon_images[0].save(icon_path,
                          format='ICO',
                          sizes=sizes,
                          append_images=icon_images[1:])
        
        print("Ícone criado com sucesso na pasta assets!")
        
    except Exception as e:
        print(f"Erro ao criar o ícone: {e}")

if __name__ == "__main__":
    create_uol_icon() 