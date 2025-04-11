from PIL import Image
import os

def process_logo():
    try:
        # Criar pasta assets se não existir
        if not os.path.exists('assets'):
            os.makedirs('assets')
        
        # Abrir a imagem do logo
        logo = Image.open('grupo_uol.png')
        
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
        
        # Redimensionar para o tamanho desejado
        width = 120
        height = 40
        logo = logo.resize((width, height), Image.Resampling.LANCZOS)
        
        # Salvar na pasta assets
        logo.save(os.path.join('assets', 'uol_logo.png'), 'PNG')
        print("Logo processado e salvo com sucesso!")
        
        # Criar o ícone
        from create_icon import create_uol_icon
        create_uol_icon()
        
    except FileNotFoundError:
        print("Erro: Arquivo 'grupo_uol.png' não encontrado. Por favor, salve a imagem na pasta do projeto.")
    except Exception as e:
        print(f"Erro ao processar o logo: {e}")

if __name__ == "__main__":
    process_logo() 