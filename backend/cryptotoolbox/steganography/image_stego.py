"""
Stéganographie dans les images
Technique : LSB (Least Significant Bit)
"""

from PIL import Image
import io
import base64
import numpy as np


def hide_text_in_image(image_data, secret_message, method='lsb'):
    """
    Cache un message secret dans une image
    
    Args:
        image_data: Données de l'image (bytes ou chemin)
        secret_message: Message secret à cacher
        method: Méthode à utiliser ('lsb' pour l'instant)
    
    Returns:
        dict: {
            'stego_image': image avec message caché (base64),
            'method': méthode utilisée,
            'message_length': longueur du message,
            'pixels_used': nombre de pixels modifiés
        }
    """
    if method == 'lsb':
        return _hide_lsb(image_data, secret_message)
    else:
        raise ValueError(f"Méthode inconnue: {method}")


def extract_text_from_image(image_data, method='lsb'):
    """
    Extrait un message secret d'une image stéganographiée
    
    Args:
        image_data: Données de l'image (bytes ou chemin)
        method: Méthode utilisée pour cacher le message
    
    Returns:
        dict: {
            'secret_message': message extrait,
            'method': méthode utilisée,
            'success': bool
        }
    """
    if method == 'lsb':
        return _extract_lsb(image_data)
    else:
        raise ValueError(f"Méthode inconnue: {method}")


# ============= MÉTHODE LSB (Least Significant Bit) =============

def _hide_lsb(image_data, secret_message):
    """
    Cache le message en modifiant les bits de poids faible des pixels
    Méthode LSB : modifie le dernier bit de chaque composante RGB
    """
    # Charger l'image
    if isinstance(image_data, str):
        img = Image.open(image_data)
    elif isinstance(image_data, bytes):
        img = Image.open(io.BytesIO(image_data))
    else:
        raise ValueError("image_data doit être un chemin ou des bytes")
    
    # Convertir en RGB si nécessaire
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convertir l'image en array numpy
    img_array = np.array(img)
    height, width, channels = img_array.shape
    
    # Préparer le message : longueur (4 bytes) + message + délimiteur
    delimiter = "<<<END>>>"
    full_message = secret_message + delimiter
    
    # Convertir le message en binaire
    message_length = len(secret_message)
    length_binary = format(message_length, '032b')  # 32 bits pour la longueur
    message_binary = ''.join(format(ord(char), '08b') for char in full_message)
    binary_data = length_binary + message_binary
    
    # Vérifier si l'image est assez grande
    max_bytes = height * width * channels
    if len(binary_data) > max_bytes:
        raise ValueError(f"Image trop petite pour cacher le message (besoin de {len(binary_data)} bits, disponibles: {max_bytes})")
    
    # Cacher le message dans les LSB
    data_index = 0
    pixels_modified = 0
    
    for i in range(height):
        for j in range(width):
            for k in range(channels):
                if data_index < len(binary_data):
                    # Récupérer la valeur du pixel
                    pixel_value = img_array[i, j, k]
                    
                    # Modifier le LSB
                    if binary_data[data_index] == '0':
                        # Mettre le LSB à 0
                        img_array[i, j, k] = pixel_value & 0xFE  # 11111110
                    else:
                        # Mettre le LSB à 1
                        img_array[i, j, k] = pixel_value | 0x01  # 00000001
                    
                    data_index += 1
                    pixels_modified += 1
                else:
                    break
    
    # Créer une nouvelle image avec les données modifiées
    stego_img = Image.fromarray(img_array)
    
    # Convertir en base64 pour le transport
    buffer = io.BytesIO()
    stego_img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return {
        'stego_image': img_base64,
        'method': 'lsb',
        'message_length': message_length,
        'pixels_used': pixels_modified,
        'image_size': f"{width}x{height}",
        'capacity': max_bytes,
        'usage_percent': round((len(binary_data) / max_bytes) * 100, 2),
        'explanation': 'Message caché dans les bits de poids faible (LSB) des pixels RGB'
    }


def _extract_lsb(image_data):
    """
    Extrait le message des bits de poids faible des pixels
    """
    # Charger l'image
    if isinstance(image_data, str):
        img = Image.open(image_data)
    elif isinstance(image_data, bytes):
        img = Image.open(io.BytesIO(image_data))
    elif isinstance(image_data, dict) and 'stego_image' in image_data:
        # Décoder depuis base64
        img_bytes = base64.b64decode(image_data['stego_image'])
        img = Image.open(io.BytesIO(img_bytes))
    else:
        raise ValueError("Format d'image non reconnu")
    
    # Convertir en RGB
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convertir en array numpy
    img_array = np.array(img)
    height, width, channels = img_array.shape
    
    # Extraire les LSB
    binary_data = ''
    
    # D'abord extraire la longueur (32 bits)
    bits_count = 0
    for i in range(height):
        for j in range(width):
            for k in range(channels):
                if bits_count < 32:
                    binary_data += str(img_array[i, j, k] & 1)
                    bits_count += 1
                else:
                    break
            if bits_count >= 32:
                break
        if bits_count >= 32:
            break
    
    # Décoder la longueur
    if len(binary_data) < 32:
        return {
            'secret_message': '',
            'method': 'lsb',
            'success': False,
            'error': 'Impossible de lire la longueur du message'
        }
    
    message_length = int(binary_data[:32], 2)
    
    # Vérifier que la longueur est raisonnable
    if message_length <= 0 or message_length > 10000:
        return {
            'secret_message': '',
            'method': 'lsb',
            'success': False,
            'error': f'Longueur de message invalide: {message_length}'
        }
    
    # Calculer le nombre de bits nécessaires (message + délimiteur)
    delimiter = "<<<END>>>"
    total_chars = message_length + len(delimiter)
    total_bits = total_chars * 8
    
    # Extraire le reste des bits
    binary_data = binary_data[32:]  # Enlever les 32 bits de longueur
    
    for i in range(height):
        for j in range(width):
            for k in range(channels):
                if len(binary_data) < total_bits + 32:
                    if bits_count >= 32:  # Sauter les 32 premiers bits déjà extraits
                        binary_data += str(img_array[i, j, k] & 1)
                    bits_count += 1
                else:
                    break
            if len(binary_data) >= total_bits:
                break
        if len(binary_data) >= total_bits:
            break
    
    # Convertir binaire en texte
    message = ''
    for i in range(0, len(binary_data), 8):
        if i + 8 <= len(binary_data):
            byte = binary_data[i:i+8]
            char_code = int(byte, 2)
            if 32 <= char_code <= 126 or char_code in [10, 13]:  # Caractères imprimables + newlines
                message += chr(char_code)
    
    # Chercher le délimiteur
    if delimiter in message:
        message = message[:message.index(delimiter)]
    
    return {
        'secret_message': message,
        'method': 'lsb',
        'success': len(message) > 0,
        'extracted_length': len(message),
        'expected_length': message_length
    }


# ============= FONCTIONS UTILITAIRES =============

def create_sample_image(width=200, height=200, color=(255, 255, 255)):
    """
    Crée une image blanche simple pour les tests
    """
    img = Image.new('RGB', (width, height), color)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def analyze_image_capacity(image_data):
    """
    Analyse la capacité d'une image à cacher des messages
    """
    # Charger l'image
    if isinstance(image_data, str):
        img = Image.open(image_data)
    elif isinstance(image_data, bytes):
        img = Image.open(io.BytesIO(image_data))
    else:
        raise ValueError("image_data doit être un chemin ou des bytes")
    
    width, height = img.size
    channels = len(img.getbands())
    
    total_bits = width * height * channels
    max_chars = total_bits // 8
    
    return {
        'width': width,
        'height': height,
        'channels': channels,
        'format': img.format,
        'mode': img.mode,
        'total_pixels': width * height,
        'total_bits': total_bits,
        'max_characters': max_chars,
        'max_characters_kb': round(max_chars / 1024, 2),
        'recommended_message_length': max_chars // 2  # 50% de capacité recommandée
    }


def compare_images(original_path, stego_path):
    """
    Compare deux images pour détecter les modifications
    """
    img1 = Image.open(original_path)
    img2 = Image.open(stego_path)
    
    if img1.size != img2.size:
        return {'error': 'Images de tailles différentes'}
    
    arr1 = np.array(img1)
    arr2 = np.array(img2)
    
    diff = np.abs(arr1.astype(int) - arr2.astype(int))
    
    return {
        'identical': np.array_equal(arr1, arr2),
        'max_difference': int(np.max(diff)),
        'mean_difference': float(np.mean(diff)),
        'pixels_modified': int(np.sum(diff > 0)),
        'modification_percent': round((np.sum(diff > 0) / diff.size) * 100, 4)
    }


def get_image_methods():
    """
    Retourne les méthodes disponibles pour la stéganographie d'images
    """
    return {
        'lsb': {
            'name': 'LSB (Least Significant Bit)',
            'description': 'Modifie les bits de poids faible des pixels RGB',
            'visibility': 'Invisible à l\'œil nu',
            'robustness': 'Faible (sensible aux compressions)',
            'capacity': 'Élevée (1 bit par composante RGB)',
            'quality_loss': 'Négligeable'
        }
    }
