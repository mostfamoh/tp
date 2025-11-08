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
    
    # Convertir en array numpy et aplatir
    img_array = np.array(img)
    height, width, channels = img_array.shape
    flat = img_array.reshape(-1)
    bits = flat & 1  # tableau des LSB

    # Vérifier qu'on a au moins 32 bits pour la longueur
    if bits.size < 32:
        return {
            'secret_message': '',
            'method': 'lsb',
            'success': False,
            'error': 'Image trop petite pour contenir la longueur (32 bits)'
        }

    # Lire la longueur (32 bits)
    length_bits = bits[:32]
    length_str = ''.join('1' if b & 1 else '0' for b in length_bits)
    try:
        message_length = int(length_str, 2)
    except Exception:
        return {
            'secret_message': '',
            'method': 'lsb',
            'success': False,
            'error': 'Longueur encodée invalide'
        }

    # Bornes raisonnables et capacité
    delimiter = "<<<END>>>"
    capacity_bits = bits.size
    max_chars_by_capacity = max(0, (capacity_bits - 32) // 8)
    if message_length <= 0 or message_length > max_chars_by_capacity or message_length > 1_000_000:
        return {
            'secret_message': '',
            'method': 'lsb',
            'success': False,
            'error': f'Longueur de message invalide ou dépasse la capacité ({message_length} chars)'
        }

    total_chars = message_length + len(delimiter)
    total_bits = total_chars * 8
    if 32 + total_bits > capacity_bits:
        return {
            'secret_message': '',
            'method': 'lsb',
            'success': False,
            'error': 'Données insuffisantes pour extraire le message complet'
        }

    data_bits = bits[32:32 + total_bits]
    # Convertir en texte (8 bits -> 1 octet)
    message_bytes = bytearray()
    for i in range(0, data_bits.size, 8):
        byte_val = 0
        for j in range(8):
            if data_bits[i + j] & 1:
                byte_val |= (1 << (7 - j))
        message_bytes.append(byte_val)

    try:
        msg_full = message_bytes.decode('utf-8', errors='ignore')
    except Exception:
        # Fallback ASCII
        msg_full = ''.join(chr(b) for b in message_bytes if 32 <= b <= 126 or b in (10, 13))

    # Tronquer au délimiteur
    if delimiter in msg_full:
        message = msg_full[:msg_full.index(delimiter)]
    else:
        # Si pas de délimiteur, on coupe à message_length
        message = msg_full[:message_length]

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
