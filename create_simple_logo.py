from PIL import Image, ImageDraw
import os

def create_simple_logo():
    try:
        # Criar pasta assets se não existir
        if not os.path.exists('assets'):
            os.makedirs('assets')
        
        # Criar uma nova imagem com fundo transparente
        width = 200
        height = 80
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)
        
        # Desenhar um círculo laranja preenchido
        circle_color = (255, 107, 0)  # Laranja UOL
        circle_bbox = [5, 5, 75, 75]  # Coordenadas do círculo maior
        draw.ellipse(circle_bbox, fill=circle_color)
        
        # Desenhar círculos internos em vermelho
        inner_color = (200, 0, 0)  # Vermelho
        offset = 15
        inner_bbox = [5 + offset, 5 + offset, 75 - offset, 75 - offset]
        draw.arc(inner_bbox, start=45, end=225, fill=inner_color, width=3)
        
        # Salvar a imagem
        image.save(os.path.join('assets', 'uol_logo.png'), 'PNG')
        print("Logo criado com sucesso!")
        
        # Criar o ícone
        from create_icon import create_uol_icon
        create_uol_icon()
        
    except Exception as e:
        print(f"Erro ao criar o logo: {e}")

if __name__ == "__main__":
    create_simple_logo() 