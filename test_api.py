#!/usr/bin/env python3
"""
Banco de Pruebas Automatizado para el Microservicio TYA (Temas y Artistas)
Prueba todos los endpoints de la API: Songs, Albums, Merchandising y Artists

CONFIGURACIÓN REQUERIDA:
    1. Configurar BASE_URL con la URL del servidor (por defecto localhost:8080)
    2. Configurar AUTH_TOKEN con un token válido del servicio de autenticación
       - El token debe ser obtenido del servicio de auth en {ip_auth}/auth/{token}
       - Este token se enviará en la cookie 'oversound_auth'
    3. Los endpoints GET (búsqueda y obtención por ID) NO requieren autenticación
    4. Los endpoints POST, PATCH y DELETE SÍ requieren autenticación

NOTA: Si AUTH_TOKEN no es válido, todas las pruebas que requieren autenticación fallarán con 401 Unauthorized
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# ============================================================================
# CONFIGURACIÓN DEL SERVIDOR Y AUTENTICACIÓN
# ============================================================================
BASE_URL = "http://localhost:8081"
AUTH_TOKEN = "7f1e62d553ae3f1a4ee6c3978dcbdd6038d3632b1482a0449b1d279f2b2f51ae0f91ab5116ab7175ac15e5af8cea985b295d24048c9328341d0c8972995b97ac"  # ⚠️ REEMPLAZAR con un token válido de autenticación

# Colores para output en consola
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

# Contadores de pruebas
tests_passed = 0
tests_failed = 0

def print_test_header(test_name: str):
    """Imprime el encabezado de una prueba"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"PRUEBA: {test_name}")
    print(f"{'='*60}{Colors.RESET}")

def print_result(success: bool, message: str):
    """Imprime el resultado de una prueba"""
    global tests_passed, tests_failed
    if success:
        print(f"{Colors.GREEN}✓ PASS: {message}{Colors.RESET}")
        tests_passed += 1
    else:
        print(f"{Colors.RED}✗ FAIL: {message}{Colors.RESET}")
        tests_failed += 1

def print_summary():
    """Imprime el resumen final de las pruebas"""
    total = tests_passed + tests_failed
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"RESUMEN DE PRUEBAS")
    print(f"{'='*60}{Colors.RESET}")
    print(f"Total: {total}")
    print(f"{Colors.GREEN}Exitosas: {tests_passed}{Colors.RESET}")
    print(f"{Colors.RED}Fallidas: {tests_failed}{Colors.RESET}")
    if tests_failed == 0:
        print(f"\n{Colors.GREEN}¡Todas las pruebas pasaron!{Colors.RESET}\n")
    else:
        print(f"\n{Colors.RED}Algunas pruebas fallaron{Colors.RESET}\n")

def make_request(method: str, endpoint: str, data: Optional[Dict] = None, expected_status: int = 200, requires_auth: bool = True) -> tuple:
    """
    Realiza una petición HTTP y verifica el código de estado
    Retorna (success, response)
    """
    url = f"{BASE_URL}{endpoint}"
    
    # Preparar cookies de autenticación si es necesario
    cookies = {}
    if requires_auth:
        cookies = {"oversound_auth": AUTH_TOKEN}
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, cookies=cookies)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"}, cookies=cookies)
        elif method.upper() == "PATCH":
            response = requests.patch(url, json=data, headers={"Content-Type": "application/json"}, cookies=cookies)
        elif method.upper() == "DELETE":
            response = requests.delete(url, cookies=cookies)
        else:
            return False, None
        
        success = response.status_code == expected_status
        return success, response
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}Error de conexión: {e}{Colors.RESET}")
        return False, None

# =============================================================================
# PRUEBAS DE AUTENTICACIÓN
# =============================================================================

def test_unauthorized_access():
    """Prueba que los endpoints protegidos rechacen peticiones sin token"""
    print_test_header("TEST: Acceso no autorizado (sin token)")
    
    # Intentar crear una canción sin token (debe devolver 401)
    song_data = {
        "title": "Unauthorized Song",
        "genres": [1],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 5.99,
        "trackId": 999999,
        "duration": 100
    }
    
    success, response = make_request("POST", "/song/upload", song_data, 401, requires_auth=False)
    print_result(success, f"POST /song/upload sin token → 401 Unauthorized - Status: {response.status_code if response else 'N/A'}")
    
    # Intentar eliminar sin token
    success, response = make_request("DELETE", "/song/1", expected_status=401, requires_auth=False)
    print_result(success, f"DELETE /song/1 sin token → 401 Unauthorized - Status: {response.status_code if response else 'N/A'}")
    
    # Intentar actualizar sin token
    success, response = make_request("PATCH", "/song/1", {"title": "Test"}, 401, requires_auth=False)
    print_result(success, f"PATCH /song/1 sin token → 401 Unauthorized - Status: {response.status_code if response else 'N/A'}")

def test_get_without_auth():
    """Prueba que los endpoints GET funcionen sin autenticación"""
    print_test_header("TEST: Endpoints GET sin autenticación (debe funcionar)")
    
    # GET de canciones sin token (debe funcionar - 200 o 404 si no existe)
    success, response = make_request("GET", "/song/1", expected_status=200, requires_auth=False)
    status_ok = response and (response.status_code == 200 or response.status_code == 404)
    print_result(status_ok, f"GET /song/1 sin token → {response.status_code if response else 'N/A'} (200 OK o 404 esperado)")
    
    # GET de álbumes sin token
    success, response = make_request("GET", "/album/1", expected_status=200, requires_auth=False)
    status_ok = response and (response.status_code == 200 or response.status_code == 404)
    print_result(status_ok, f"GET /album/1 sin token → {response.status_code if response else 'N/A'} (200 OK o 404 esperado)")
    
    # GET de merchandising sin token
    success, response = make_request("GET", "/merch/1", expected_status=200, requires_auth=False)
    status_ok = response and (response.status_code == 200 or response.status_code == 404)
    print_result(status_ok, f"GET /merch/1 sin token → {response.status_code if response else 'N/A'} (200 OK o 404 esperado)")
    
    # GET de artistas sin token
    success, response = make_request("GET", "/artist/1", expected_status=200, requires_auth=False)
    status_ok = response and (response.status_code == 200 or response.status_code == 404)
    print_result(status_ok, f"GET /artist/1 sin token → {response.status_code if response else 'N/A'} (200 OK o 404 esperado)")

def test_search_without_auth():
    """Prueba que los endpoints de búsqueda funcionen sin autenticación"""
    print_test_header("TEST: Búsqueda sin autenticación (debe funcionar)")
    
    # Búsqueda de canciones sin token (debe funcionar - 200)
    success, response = make_request("GET", "/song/search?q=test", expected_status=200, requires_auth=False)
    print_result(success, f"GET /song/search sin token → 200 OK - Status: {response.status_code if response else 'N/A'}")
    
    # Búsqueda de álbumes sin token
    success, response = make_request("GET", "/album/search?q=test", expected_status=200, requires_auth=False)
    print_result(success, f"GET /album/search sin token → 200 OK - Status: {response.status_code if response else 'N/A'}")
    
    # Búsqueda de merchandising sin token
    success, response = make_request("GET", "/merch/search?q=test", expected_status=200, requires_auth=False)
    print_result(success, f"GET /merch/search sin token → 200 OK - Status: {response.status_code if response else 'N/A'}")
    
    # Búsqueda de artistas sin token
    success, response = make_request("GET", "/artist/search?q=test", expected_status=200, requires_auth=False)
    print_result(success, f"GET /artist/search sin token → 200 OK - Status: {response.status_code if response else 'N/A'}")

def test_get_genres():
    """Prueba obtener lista de géneros (sin autenticación)"""
    print_test_header("GET /genres - Obtener lista de géneros")
    
    success, response = make_request("GET", "/genres", expected_status=200, requires_auth=False)
    
    if success and response:
        try:
            genres = response.json()
            print_result(True, f"GET /genres → 200 OK - {len(genres)} géneros recibidos")
            
            # Verificar estructura de datos
            if len(genres) > 0:
                first_genre = genres[0]
                has_id = 'id' in first_genre
                has_name = 'name' in first_genre
                print_result(has_id and has_name, f"  → Estructura correcta: {{id: {first_genre.get('id')}, name: '{first_genre.get('name')}'}}")
            else:
                print_result(True, "  → Lista vacía de géneros")
        except Exception as e:
            print_result(False, f"GET /genres → Error al parsear respuesta: {e}")
    else:
        print_result(False, f"GET /genres → Status: {response.status_code if response else 'N/A'}")

# =============================================================================
# PRUEBAS DE SONGS (Canciones)
# =============================================================================

def test_list_songs():
    """Prueba obtener lista de canciones por IDs"""
    print_test_header("GET /song/list - Obtener lista de canciones por IDs")
    
    # Primero crear algunas canciones para tener IDs válidos
    song_ids = []
    for i in range(3):
        song_data = {
            "title": f"List Test Song {i+1}",
            "genres": [1],
            "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
            "price": 5.99,
            "trackId": 700001 + i,
            "duration": 180
        }
        success, response = make_request("POST", "/song/upload", song_data, 200)
        if success and response:
            try:
                song_id = response.json().get("songId")
                song_ids.append(song_id)
            except:
                pass
    
    if len(song_ids) > 0:
        # Probar el endpoint list
        ids_param = ",".join(map(str, song_ids))
        success, response = make_request("GET", f"/song/list?ids={ids_param}", expected_status=200, requires_auth=False)
        
        if success and response:
            try:
                songs = response.json()
                print_result(len(songs) == len(song_ids), f"Recibidas {len(songs)} canciones de {len(song_ids)} solicitadas")
                
                # Verificar estructura
                if len(songs) > 0:
                    first_song = songs[0]
                    required_fields = ['songId', 'title', 'price', 'duration', 'genres', 'cover']
                    has_all_fields = all(field in first_song for field in required_fields)
                    print_result(has_all_fields, f"Estructura de datos completa")
            except Exception as e:
                print_result(False, f"Error al parsear respuesta: {e}")
        else:
            print_result(False, f"Error al obtener lista - Status: {response.status_code if response else 'N/A'}")
        
        # Limpiar
        for song_id in song_ids:
            make_request("DELETE", f"/song/{song_id}")
    else:
        print_result(False, "No se pudieron crear canciones para la prueba")

def test_list_songs_invalid_id():
    """Prueba list con ID inválido"""
    print_test_header("GET /song/list - Validación de ID inválido")
    
    success, response = make_request("GET", "/song/list?ids=1,abc,3", expected_status=400, requires_auth=False)
    print_result(success, f"Validación de ID inválido - Status: {response.status_code if response else 'N/A'}")

def test_list_songs_missing_param():
    """Prueba list sin parámetro ids"""
    print_test_header("GET /song/list - Validación sin parámetro 'ids'")
    
    success, response = make_request("GET", "/song/list", expected_status=400, requires_auth=False)
    print_result(success, f"Validación sin parámetro - Status: {response.status_code if response else 'N/A'}")

def test_filter_songs():
    """Prueba filtrar canciones por géneros y artistas"""
    print_test_header("GET /song/filter - Filtrar canciones")
    
    # Crear canción con géneros específicos
    song_data = {
        "title": "Filter Test Song",
        "genres": [1, 2],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 7.99,
        "trackId": 800001,
        "duration": 200
    }
    
    success, response = make_request("POST", "/song/upload", song_data, 200)
    song_id = None
    if success and response:
        try:
            song_id = response.json().get("songId")
        except:
            pass
    
    if song_id:
        # Filtrar por género - solo verificar que el endpoint funciona
        success, response = make_request("GET", "/song/filter?genres=1", expected_status=200, requires_auth=False)
        if success and response:
            try:
                results = response.json()
                # Verificar que devuelve resultados (puede haber muchas canciones con género 1)
                print_result(len(results) > 0, f"Filtro por género devuelve resultados: {len(results)} canciones")
            except Exception as e:
                print_result(False, f"Error al parsear respuesta: {e}")
        else:
            print_result(False, f"Error al filtrar - Status: {response.status_code if response else 'N/A'}")
        
        # Probar ordenamiento
        success, response = make_request("GET", "/song/filter?genres=1&order=date&direction=asc", expected_status=200, requires_auth=False)
        print_result(success, f"Filtro con ordenamiento - Status: {response.status_code if response else 'N/A'}")
        
        # Limpiar
        make_request("DELETE", f"/song/{song_id}")
    else:
        print_result(False, "No se pudo crear canción para la prueba")

def test_filter_songs_missing_param():
    """Prueba filter sin parámetros (ahora debe funcionar y devolver todos)"""
    print_test_header("GET /song/filter - Sin parámetros (devuelve todos)")
    
    success, response = make_request("GET", "/song/filter", expected_status=200, requires_auth=False)
    if success and response:
        try:
            results = response.json()
            print_result(True, f"Sin parámetros devuelve todos - {len(results)} canciones - Status: {response.status_code}")
        except:
            print_result(False, f"Error al parsear respuesta")
    else:
        print_result(False, f"Error - Status: {response.status_code if response else 'N/A'}")

def test_filter_songs_pagination():
    """Prueba paginación en /song/filter"""
    print_test_header("GET /song/filter - Paginación")
    
    # Crear más de 9 canciones para probar paginación
    song_ids = []
    print("  → Creando 12 canciones para probar paginación...")
    for i in range(12):
        song_data = {
            "title": f"Pagination Test Song {i+1}",
            "genres": [1],
            "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
            "price": 4.99,
            "trackId": 750000 + i,
            "duration": 180
        }
        success, response = make_request("POST", "/song/upload", song_data, 200)
        if success and response:
            try:
                song_id = response.json().get("songId")
                song_ids.append(song_id)
            except:
                pass
    
    if len(song_ids) >= 12:
        # Página 1 - debe devolver 9 resultados
        success, response = make_request("GET", "/song/filter?genres=1&page=1", expected_status=200, requires_auth=False)
        if success and response:
            try:
                page1_results = response.json()
                print_result(len(page1_results) == 9, f"Página 1: {len(page1_results)} resultados (esperado: 9)")
            except:
                print_result(False, "Error al parsear página 1")
        
        # Página 2 - debe devolver entre 1 y 9 resultados (hay más canciones en BD)
        success, response = make_request("GET", "/song/filter?genres=1&page=2", expected_status=200, requires_auth=False)
        if success and response:
            try:
                page2_results = response.json()
                print_result(1 <= len(page2_results) <= 9, f"Página 2: {len(page2_results)} resultados (esperado: 1-9)")
            except:
                print_result(False, "Error al parsear página 2")
        
        # Verificar que con paginación alta devuelve vacío
        success, response = make_request("GET", "/song/filter?genres=1&page=999", expected_status=200, requires_auth=False)
        if success and response:
            try:
                page_high_results = response.json()
                print_result(len(page_high_results) == 0, f"Página 999: {len(page_high_results)} resultados (esperado: 0)")
            except:
                print_result(False, "Error al parsear página alta")
        
        # Sin página (por defecto página 1)
        success, response = make_request("GET", "/song/filter?genres=1", expected_status=200, requires_auth=False)
        if success and response:
            try:
                default_results = response.json()
                print_result(len(default_results) == 9, f"Sin page (default): {len(default_results)} resultados (esperado: 9)")
            except:
                print_result(False, "Error al parsear sin page")
    else:
        print_result(False, f"Solo se crearon {len(song_ids)} canciones, se necesitan al menos 12")
    
    # Limpiar
    for song_id in song_ids:
        make_request("DELETE", f"/song/{song_id}")

def test_filter_albums_pagination():
    """Prueba paginación en /album/filter"""
    print_test_header("GET /album/filter - Paginación")
    
    # Crear canciones y álbumes para probar
    song_ids = []
    album_ids = []
    
    print("  → Creando 10 álbumes para probar paginación...")
    for i in range(10):
        # Crear canción con género
        song_data = {
            "title": f"Album Pagination Song {i+1}",
            "genres": [1],
            "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
            "price": 3.99,
            "trackId": 760000 + i,
            "duration": 180
        }
        success, response = make_request("POST", "/song/upload", song_data, 200)
        song_id = None
        if success and response:
            try:
                song_id = response.json().get("songId")
                song_ids.append(song_id)
            except:
                pass
        
        # Crear álbum con la canción
        if song_id:
            album_data = {
                "title": f"Pagination Album {i+1}",
                "songs": [song_id],
                "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
                "price": 12.99
            }
            success, response = make_request("POST", "/album/upload", album_data, 200)
            if success and response:
                try:
                    album_id = response.json().get("albumId")
                    album_ids.append(album_id)
                except:
                    pass
    
    if len(album_ids) >= 10:
        # Página 1 - debe devolver 9 resultados
        success, response = make_request("GET", "/album/filter?genres=1&page=1", expected_status=200, requires_auth=False)
        if success and response:
            try:
                page1_results = response.json()
                print_result(len(page1_results) == 9, f"Página 1: {len(page1_results)} resultados (esperado: 9)")
            except:
                print_result(False, "Error al parsear página 1")
        
        # Página 2 - debe devolver entre 1 y 9 resultados (hay más álbumes en BD)
        success, response = make_request("GET", "/album/filter?genres=1&page=2", expected_status=200, requires_auth=False)
        if success and response:
            try:
                page2_results = response.json()
                print_result(1 <= len(page2_results) <= 9, f"Página 2: {len(page2_results)} resultados (esperado: 1-9)")
            except:
                print_result(False, "Error al parsear página 2")
    else:
        print_result(False, f"Solo se crearon {len(album_ids)} álbumes, se necesitan al menos 10")
    
    # Limpiar
    for album_id in album_ids:
        make_request("DELETE", f"/album/{album_id}")
    for song_id in song_ids:
        make_request("DELETE", f"/song/{song_id}")

def test_filter_merch_pagination():
    """Prueba paginación en /merch/filter"""
    print_test_header("GET /merch/filter - Paginación")
    
    # Crear merchandising
    merch_ids = []
    print("  → Creando 10 merchandising para probar paginación...")
    for i in range(10):
        merch_data = {
            "title": f"Pagination Merch {i+1}",
            "description": "Test",
            "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
            "price": 25.00
        }
        success, response = make_request("POST", "/merch/upload", merch_data, 200)
        if success and response:
            try:
                merch_id = response.json().get("merchId")
                merch_ids.append(merch_id)
            except:
                pass
    
    if len(merch_ids) >= 10:
        # Página 1 - debe devolver 9 resultados
        success, response = make_request("GET", "/merch/filter?page=1", expected_status=200, requires_auth=False)
        if success and response:
            try:
                page1_results = response.json()
                print_result(len(page1_results) == 9, f"Página 1: {len(page1_results)} resultados (esperado: 9)")
            except:
                print_result(False, "Error al parsear página 1")
        
        # Página 2
        success, response = make_request("GET", "/merch/filter?page=2", expected_status=200, requires_auth=False)
        if success and response:
            try:
                page2_results = response.json()
                print_result(len(page2_results) >= 1, f"Página 2: {len(page2_results)} resultados")
            except:
                print_result(False, "Error al parsear página 2")
    else:
        print_result(False, f"Solo se crearon {len(merch_ids)} merchandising")
    
    # Limpiar
    for merch_id in merch_ids:
        make_request("DELETE", f"/merch/{merch_id}")

def test_filter_artists_pagination():
    """Prueba paginación en /artist/filter"""
    print_test_header("GET /artist/filter - Paginación")
    
    # Probar paginación con artistas existentes
    success, response = make_request("GET", "/artist/filter?page=1", expected_status=200, requires_auth=False)
    if success and response:
        try:
            page1_results = response.json()
            print_result(True, f"Página 1: {len(page1_results)} artistas (máximo 9)")
        except:
            print_result(False, "Error al parsear página 1")
    
    success, response = make_request("GET", "/artist/filter?page=2", expected_status=200, requires_auth=False)
    if success and response:
        try:
            page2_results = response.json()
            print_result(True, f"Página 2: {len(page2_results)} artistas")
        except:
            print_result(False, "Error al parsear página 2")

def test_upload_song():
    """Prueba crear una nueva canción"""
    print_test_header("POST /song/upload - Crear canción")
    
    song_data = {
        "title": "Test Song",
        "genres": [1, 2],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 9.99,
        "trackId": 100001,
        "duration": 180,
        "description": "Una canción de prueba",
        "releaseDate": "2024-01-15"
    }
    
    success, response = make_request("POST", "/song/upload", song_data, 200)
    print_result(success, f"Crear canción - Status: {response.status_code if response else 'N/A'}")
    
    if success and response:
        try:
            data = response.json()
            if "songId" in data:
                print(f"  → Song ID creado: {data['songId']}")
                return data["songId"]
        except:
            pass
    return None

def test_upload_song_with_album(album_id: int):
    """Prueba crear una canción asociada a un álbum"""
    print_test_header("POST /song/upload - Crear canción con álbum")
    
    song_data = {
        "title": "Test Song With Album",
        "genres": [1],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 7.99,
        "trackId": 100002,
        "duration": 200,
        "albumId": album_id,
        "albumOrder": 1
    }
    
    success, response = make_request("POST", "/song/upload", song_data, 200)
    print_result(success, f"Crear canción con álbum {album_id} - Status: {response.status_code if response else 'N/A'}")
    
    if success and response:
        try:
            data = response.json()
            if "songId" in data:
                return data["songId"]
        except:
            pass
    return None

def test_upload_song_invalid_album():
    """Prueba crear canción con álbum inexistente (debe fallar con 422)"""
    print_test_header("POST /song/upload - Validación álbum inexistente")
    
    song_data = {
        "title": "Invalid Album Song",
        "genres": [1],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 5.99,
        "trackId": 100003,
        "duration": 150,
        "albumId": 99999,
        "albumOrder": 1
    }
    
    success, response = make_request("POST", "/song/upload", song_data, 422)
    print_result(success, f"Validación álbum inexistente - Status: {response.status_code if response else 'N/A'}")

def test_upload_song_invalid_price():
    """Prueba crear canción con precio negativo (debe fallar con 400)"""
    print_test_header("POST /song/upload - Validación precio negativo")
    
    song_data = {
        "title": "Invalid Price Song",
        "genres": [1],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": -5.00,
        "trackId": 100004,
        "duration": 120
    }
    
    success, response = make_request("POST", "/song/upload", song_data, 400)
    print_result(success, f"Validación precio negativo - Status: {response.status_code if response else 'N/A'}")

def test_upload_song_missing_albumorder():
    """Prueba crear canción con albumId pero sin albumOrder (debe fallar con 400)"""
    print_test_header("POST /song/upload - Validación albumId sin albumOrder")
    
    song_data = {
        "title": "Missing AlbumOrder Song",
        "genres": [1],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 8.99,
        "trackId": 100005,
        "duration": 160,
        "albumId": 1
        # albumOrder falta intencionalmente
    }
    
    success, response = make_request("POST", "/song/upload", song_data, 400)
    if success:
        print_result(True, f"Validación correcta: albumId sin albumOrder → 400 Bad Request")
    else:
        print_result(False, f"Esperado 400, recibido: {response.status_code if response else 'N/A'}")

def test_get_song(song_id: int):
    """Prueba obtener una canción por ID"""
    print_test_header(f"GET /song/{song_id} - Obtener canción")
    
    success, response = make_request("GET", f"/song/{song_id}", expected_status=200, requires_auth=False)
    print_result(success, f"Obtener canción {song_id} - Status: {response.status_code if response else 'N/A'}")
    
    if success and response:
        try:
            data = response.json()
            print(f"  → Título: {data.get('title', 'N/A')}")
            print(f"  → Precio: {data.get('price', 'N/A')}")
            print(f"  → Duración: {data.get('duration', 'N/A')}s")
            print(f"  → AlbumId: {data.get('albumId', 'NULL')}")
            
            # Verificar que linked_albums esté presente
            if 'linked_albums' in data:
                linked_albums = data.get('linked_albums', [])
                print(f"  → Linked Albums: {linked_albums}")
                print_result(True, "Campo linked_albums presente en la respuesta")
            else:
                print_result(False, "Campo linked_albums NO está presente en la respuesta")
        except Exception as e:
            print_result(False, f"Error al parsear respuesta: {e}")

def test_update_song(song_id: int):
    """Prueba actualizar una canción"""
    print_test_header(f"PATCH /song/{song_id} - Actualizar canción")
    
    update_data = {
        "title": "Updated Test Song",
        "price": 12.99,
        "duration": 220
    }
    
    success, response = make_request("PATCH", f"/song/{song_id}", update_data, 200)
    print_result(success, f"Actualizar canción {song_id} - Status: {response.status_code if response else 'N/A'}")

def test_search_song():
    """Prueba buscar canciones"""
    print_test_header("GET /song/search?q=Test - Buscar canción")
    
    success, response = make_request("GET", "/song/search?q=Test", expected_status=200, requires_auth=False)
    print_result(success, f"Buscar canción - Status: {response.status_code if response else 'N/A'}")

def test_delete_song(song_id: int):
    """Prueba eliminar una canción"""
    print_test_header(f"DELETE /song/{song_id} - Eliminar canción")
    
    success, response = make_request("DELETE", f"/song/{song_id}", expected_status=200)
    print_result(success, f"Eliminar canción {song_id} - Status: {response.status_code if response else 'N/A'}")

# =============================================================================
# PRUEBAS DE ALBUMS
# =============================================================================

def test_list_albums():
    """Prueba obtener lista de álbumes por IDs"""
    print_test_header("GET /album/list - Obtener lista de álbumes por IDs")
    
    # Crear algunos álbumes
    album_ids = []
    for i in range(2):
        album_data = {
            "title": f"List Test Album {i+1}",
            "songs": [],
            "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
            "price": 15.99
        }
        success, response = make_request("POST", "/album/upload", album_data, 200)
        if success and response:
            try:
                album_id = response.json().get("albumId")
                album_ids.append(album_id)
            except:
                pass
    
    if len(album_ids) > 0:
        # Probar el endpoint list
        ids_param = ",".join(map(str, album_ids))
        success, response = make_request("GET", f"/album/list?ids={ids_param}", expected_status=200, requires_auth=False)
        
        if success and response:
            try:
                albums = response.json()
                print_result(len(albums) == len(album_ids), f"Recibidos {len(albums)} álbumes de {len(album_ids)} solicitados")
            except Exception as e:
                print_result(False, f"Error al parsear respuesta: {e}")
        else:
            print_result(False, f"Error al obtener lista - Status: {response.status_code if response else 'N/A'}")
        
        # Limpiar
        for album_id in album_ids:
            make_request("DELETE", f"/album/{album_id}")
    else:
        print_result(False, "No se pudieron crear álbumes para la prueba")

def test_filter_albums():
    """Prueba filtrar álbumes por géneros y artistas"""
    print_test_header("GET /album/filter - Filtrar álbumes")
    
    # Crear canción con género
    song_data = {
        "title": "Album Filter Test Song",
        "genres": [1],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 4.99,
        "trackId": 900001,
        "duration": 180
    }
    
    success, response = make_request("POST", "/song/upload", song_data, 200)
    song_id = None
    if success and response:
        try:
            song_id = response.json().get("songId")
        except:
            pass
    
    if song_id:
        # Crear álbum con esa canción
        album_data = {
            "title": "Filter Test Album",
            "songs": [song_id],
            "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
            "price": 12.99
        }
        
        success, response = make_request("POST", "/album/upload", album_data, 200)
        album_id = None
        if success and response:
            try:
                album_id = response.json().get("albumId")
            except:
                pass
        
        if album_id:
            # Filtrar por género
            success, response = make_request("GET", "/album/filter?genres=1", expected_status=200, requires_auth=False)
            if success and response:
                try:
                    results = response.json()  # Array de IDs
                    album_in_results = album_id in results
                    print_result(album_in_results, f"Álbum {album_id} encontrado en filtro por género")
                except Exception as e:
                    print_result(False, f"Error al parsear respuesta: {e}")
            else:
                print_result(False, f"Error al filtrar - Status: {response.status_code if response else 'N/A'}")
            
            # Limpiar
            make_request("DELETE", f"/album/{album_id}")
        
        make_request("DELETE", f"/song/{song_id}")
    else:
        print_result(False, "No se pudo crear canción para la prueba")

def test_linked_albums():
    """Prueba que linked_albums muestre correctamente álbumes donde aparece una canción"""
    print_test_header("TEST: Campo linked_albums en canciones")
    
    # Paso 1: Crear primer álbum vacío
    album1_data = {
        "title": "First Album with Song",
        "songs": [],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 10.00
    }
    
    success, response = make_request("POST", "/album/upload", album1_data, 200)
    if not success or not response:
        print_result(False, "No se pudo crear el primer álbum")
        return
    
    try:
        album1_id = response.json().get("albumId")
        print(f"  → Álbum 1 creado: {album1_id}")
    except:
        print_result(False, "Error al obtener albumId 1")
        return
    
    # Paso 2: Crear canción con albumId referenciando al primer álbum (esto establece albumog)
    song_data = {
        "title": "Song For Linked Albums Test",
        "genres": [1],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 4.99,
        "trackId": 600001,
        "duration": 195,
        "albumId": album1_id,
        "albumOrder": 1
    }
    
    success, response = make_request("POST", "/song/upload", song_data, 200)
    if not success or not response:
        print_result(False, "No se pudo crear la canción")
        make_request("DELETE", f"/album/{album1_id}")
        return
    
    try:
        song_id = response.json().get("songId")
        print(f"  → Canción creada con albumog={album1_id}: {song_id}")
    except:
        print_result(False, "Error al obtener songId")
        make_request("DELETE", f"/album/{album1_id}")
        return
    
    # Crear segundo álbum con la misma canción
    album2_data = {
        "title": "Second Album with Same Song",
        "songs": [song_id],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 12.00
    }
    
    success, response = make_request("POST", "/album/upload", album2_data, 200)
    if not success or not response:
        print_result(False, "No se pudo crear el segundo álbum")
        make_request("DELETE", f"/album/{album1_id}")
        make_request("DELETE", f"/song/{song_id}")
        return
    
    try:
        album2_id = response.json().get("albumId")
        print(f"  → Álbum 2 creado: {album2_id}")
    except:
        print_result(False, "Error al obtener albumId 2")
        make_request("DELETE", f"/album/{album1_id}")
        make_request("DELETE", f"/song/{song_id}")
        return
    
    # Obtener la canción y verificar linked_albums
    success, response = make_request("GET", f"/song/{song_id}", expected_status=200, requires_auth=False)
    if not success or not response:
        print_result(False, "No se pudo obtener la canción")
    else:
        try:
            song_info = response.json()
            linked_albums = song_info.get("linked_albums", [])
            album_id = song_info.get("albumId")
            
            print(f"  → albumId (original): {album_id}")
            print(f"  → linked_albums: {linked_albums}")
            
            # El albumId debe ser el primer álbum (albumog)
            if album_id == album1_id:
                print_result(True, f"albumId correcto: {album1_id}")
            else:
                print_result(False, f"albumId esperado {album1_id}, recibido {album_id}")
            
            # linked_albums debe contener el segundo álbum, pero NO el primero
            if album2_id in linked_albums and album1_id not in linked_albums:
                print_result(True, f"linked_albums correcto: contiene {album2_id}, excluye {album1_id}")
            else:
                print_result(False, f"linked_albums incorrecto: esperado [{album2_id}], recibido {linked_albums}")
                
        except Exception as e:
            print_result(False, f"Error al parsear respuesta: {e}")
    
    # Limpiar
    make_request("DELETE", f"/album/{album2_id}")
    make_request("DELETE", f"/album/{album1_id}")
    make_request("DELETE", f"/song/{song_id}")

def test_upload_album(song_ids_list):
    """Prueba crear un nuevo álbum"""
    print_test_header("POST /album/upload - Crear álbum")
    
    # Usar las canciones creadas previamente, o lista vacía si no hay
    songs_to_use = song_ids_list if song_ids_list else []
    
    album_data = {
        "title": "Test Album",
        "songs": songs_to_use,
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 19.99,
        "releaseDate": "2024-06-15"
    }
    
    success, response = make_request("POST", "/album/upload", album_data, 200)
    print_result(success, f"Crear álbum con {len(songs_to_use)} canciones - Status: {response.status_code if response else 'N/A'}")
    
    if success and response:
        try:
            data = response.json()
            if "albumId" in data:
                print(f"  → Album ID creado: {data['albumId']}")
                return data["albumId"]
        except:
            pass
    return None

def test_upload_album_invalid_song():
    """Prueba crear álbum con canción inexistente (debe fallar con 422)"""
    print_test_header("POST /album/upload - Validación canción inexistente")
    
    album_data = {
        "title": "Invalid Songs Album",
        "songs": [99999],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 15.99
    }
    
    success, response = make_request("POST", "/album/upload", album_data, 422)
    print_result(success, f"Validación canción inexistente - Status: {response.status_code if response else 'N/A'}")

def test_upload_album_invalid_price():
    """Prueba crear álbum con precio cero (debe fallar con 400)"""
    print_test_header("POST /album/upload - Validación precio cero")
    
    album_data = {
        "title": "Invalid Price Album",
        "songs": [],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 0
    }
    
    success, response = make_request("POST", "/album/upload", album_data, 400)
    print_result(success, f"Validación precio cero - Status: {response.status_code if response else 'N/A'}")

def test_get_album(album_id: int):
    """Prueba obtener un álbum por ID"""
    print_test_header(f"GET /album/{album_id} - Obtener álbum")
    
    success, response = make_request("GET", f"/album/{album_id}", expected_status=200, requires_auth=False)
    print_result(success, f"Obtener álbum {album_id} - Status: {response.status_code if response else 'N/A'}")
    
    if success and response:
        try:
            data = response.json()
            print(f"  → Título: {data.get('title', 'N/A')}")
            print(f"  → Precio: {data.get('price', 'N/A')}")
        except:
            pass

def test_update_album(album_id: int):
    """Prueba actualizar un álbum"""
    print_test_header(f"PATCH /album/{album_id} - Actualizar álbum")
    
    update_data = {
        "title": "Updated Test Album",
        "price": 24.99
    }
    
    success, response = make_request("PATCH", f"/album/{album_id}", update_data, 200)
    print_result(success, f"Actualizar álbum {album_id} - Status: {response.status_code if response else 'N/A'}")

def test_search_album():
    """Prueba buscar álbumes"""
    print_test_header("GET /album/search?q=Test - Buscar álbum")
    
    success, response = make_request("GET", "/album/search?q=Test", expected_status=200, requires_auth=False)
    print_result(success, f"Buscar álbum - Status: {response.status_code if response else 'N/A'}")

def test_album_song_association():
    """Prueba crear álbum vacío, añadir single, actualizar álbum y verificar asociación"""
    print_test_header("FLUJO COMPLETO: Álbum vacío -> Single -> Asociación")
    
    created_ids = {"song_id": None, "album_id": None}
    
    # Paso 1: Crear un álbum vacío
    print(f"  {Colors.BLUE}Paso 1: Creando álbum vacío...{Colors.RESET}")
    album_data = {
        "title": "Test Empty Album",
        "songs": [],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 0.01
    }
    
    success, response = make_request("POST", "/album/upload", album_data, 200)
    if not success or not response:
        print_result(False, "No se pudo crear el álbum vacío")
        return created_ids
    
    try:
        album_id = response.json().get("albumId")
        created_ids["album_id"] = album_id
        print(f"  {Colors.GREEN}→ Álbum vacío creado con ID: {album_id}{Colors.RESET}")
    except:
        print_result(False, "No se pudo obtener el ID del álbum")
        return created_ids
    
    # Paso 2: Crear canción con albumId (esto establece albumog desde el inicio)
    print(f"  {Colors.BLUE}Paso 2: Creando canción con albumId...{Colors.RESET}")
    song_data = {
        "title": "Test Song for Album Association",
        "genres": [1],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 3.99,
        "trackId": 200001,
        "duration": 195,
        "albumId": album_id,
        "albumOrder": 1
    }
    
    success, response = make_request("POST", "/song/upload", song_data, 200)
    if not success or not response:
        print_result(False, "No se pudo crear la canción")
        return created_ids
    
    try:
        single_id = response.json().get("songId")
        created_ids["song_id"] = single_id
        print(f"  {Colors.GREEN}→ Canción creada con albumId={album_id}: {single_id}{Colors.RESET}")
    except:
        print_result(False, "No se pudo obtener el ID de la canción")
        return created_ids
    
    # Paso 3: Verificar que el álbum contiene la canción
    print(f"  {Colors.BLUE}Paso 3: Verificando que el álbum contiene la canción...{Colors.RESET}")
    success, response = make_request("GET", f"/album/{album_id}", expected_status=200, requires_auth=False)
    if not success or not response:
        print_result(False, "No se pudo obtener el álbum")
        return created_ids
    
    try:
        album_info = response.json()
        songs_in_album = album_info.get("songs", [])
        if single_id in songs_in_album:
            print(f"  {Colors.GREEN}→ Verificado: La canción {single_id} está en el álbum {album_id}{Colors.RESET}")
            print_result(True, f"Asociación álbum-canción verificada correctamente")
        else:
            print(f"  {Colors.RED}→ Error: La canción {single_id} NO está en el álbum{Colors.RESET}")
            print(f"  → Canciones encontradas: {songs_in_album}")
            print_result(False, "La canción no está asociada al álbum")
    except Exception as e:
        print_result(False, f"Error al verificar la asociación: {e}")
        return created_ids
    
    # Paso 4: Verificar que la canción tiene el albumId correcto (albumog)
    print(f"  {Colors.BLUE}Paso 4: Verificando que la canción tiene albumId (albumog)...{Colors.RESET}")
    success, response = make_request("GET", f"/song/{single_id}", expected_status=200, requires_auth=False)
    if not success or not response:
        print_result(False, "No se pudo obtener la canción")
        return created_ids
    
    try:
        song_info = response.json()
        song_album_id = song_info.get("albumId")
        if song_album_id == album_id:
            print(f"  {Colors.GREEN}→ Verificado: La canción tiene albumId (albumog) = {album_id}{Colors.RESET}")
            print_result(True, f"Canción correctamente asociada al álbum con albumog")
        else:
            print(f"  {Colors.RED}→ Error: albumId de la canción es {song_album_id}, esperado {album_id}{Colors.RESET}")
            print_result(False, "La canción no tiene el albumId correcto")
    except Exception as e:
        print_result(False, f"Error al verificar albumId de la canción: {e}")
    
    return created_ids

def test_delete_album(album_id: int):
    """Prueba eliminar un álbum"""
    print_test_header(f"DELETE /album/{album_id} - Eliminar álbum")
    
    success, response = make_request("DELETE", f"/album/{album_id}", expected_status=200)
    print_result(success, f"Eliminar álbum {album_id} - Status: {response.status_code if response else 'N/A'}")

# =============================================================================
# PRUEBAS DE MERCHANDISING
# =============================================================================

def test_list_merch():
    """Prueba obtener lista de merchandising por IDs"""
    print_test_header("GET /merch/list - Obtener lista de merchandising por IDs")
    
    # Crear algunos merchandising
    merch_ids = []
    for i in range(2):
        merch_data = {
            "title": f"List Test Merch {i+1}",
            "description": "Test merch",
            "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
            "price": 20.00
        }
        success, response = make_request("POST", "/merch/upload", merch_data, 200)
        if success and response:
            try:
                merch_id = response.json().get("merchId")
                merch_ids.append(merch_id)
            except:
                pass
    
    if len(merch_ids) > 0:
        # Probar el endpoint list
        ids_param = ",".join(map(str, merch_ids))
        success, response = make_request("GET", f"/merch/list?ids={ids_param}", expected_status=200, requires_auth=False)
        
        if success and response:
            try:
                merchs = response.json()
                print_result(len(merchs) == len(merch_ids), f"Recibidos {len(merchs)} merchandising de {len(merch_ids)} solicitados")
            except Exception as e:
                print_result(False, f"Error al parsear respuesta: {e}")
        else:
            print_result(False, f"Error al obtener lista - Status: {response.status_code if response else 'N/A'}")
        
        # Limpiar
        for merch_id in merch_ids:
            make_request("DELETE", f"/merch/{merch_id}")
    else:
        print_result(False, "No se pudieron crear merchandising para la prueba")

def test_filter_merch():
    """Prueba filtrar merchandising por artistas"""
    print_test_header("GET /merch/filter - Filtrar merchandising")
    
    # Crear merchandising
    merch_data = {
        "title": "Filter Test Merch",
        "description": "Test",
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 25.00
    }
    
    success, response = make_request("POST", "/merch/upload", merch_data, 200)
    merch_id = None
    artist_id = None
    
    if success and response:
        try:
            merch_id = response.json().get("merchId")
            
            # Obtener el artista del merchandising
            success2, response2 = make_request("GET", f"/merch/{merch_id}", expected_status=200, requires_auth=False)
            if success2 and response2:
                merch_info = response2.json()
                artist_id = merch_info.get("artistId")
        except:
            pass
    
    if merch_id and artist_id:
        # Filtrar por artista
        success, response = make_request("GET", f"/merch/filter?artists={artist_id}", expected_status=200, requires_auth=False)
        if success and response:
            try:
                results = response.json()  # Array de IDs
                merch_in_results = merch_id in results
                print_result(merch_in_results, f"Merchandising {merch_id} encontrado en filtro por artista")
            except Exception as e:
                print_result(False, f"Error al parsear respuesta: {e}")
        else:
            print_result(False, f"Error al filtrar - Status: {response.status_code if response else 'N/A'}")
        
        # Limpiar
        make_request("DELETE", f"/merch/{merch_id}")
    else:
        print_result(False, "No se pudo crear merchandising para la prueba")

def test_upload_merch():
    """Prueba crear merchandising"""
    print_test_header("POST /merch/upload - Crear merchandising")
    
    merch_data = {
        "title": "Test Merch",
        "description": "Camiseta de prueba",
        "price": 25.00,
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII="
    }
    
    success, response = make_request("POST", "/merch/upload", merch_data, 200)
    print_result(success, f"Crear merchandising - Status: {response.status_code if response else 'N/A'}")
    
    if success and response:
        try:
            data = response.json()
            if "merchId" in data:
                print(f"  → Merch ID creado: {data['merchId']}")
                return data["merchId"]
        except:
            pass
    return None

def test_upload_merch_invalid_price():
    """Prueba crear merchandising con precio negativo (debe fallar con 400)"""
    print_test_header("POST /merch/upload - Validación precio negativo")
    
    merch_data = {
        "title": "Invalid Merch",
        "description": "Test",
        "price": -10.00,
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII="
    }
    
    success, response = make_request("POST", "/merch/upload", merch_data, 400)
    print_result(success, f"Validación precio negativo - Status: {response.status_code if response else 'N/A'}")

def test_get_merch(merch_id: int):
    """Prueba obtener merchandising por ID"""
    print_test_header(f"GET /merch/{merch_id} - Obtener merchandising")
    
    success, response = make_request("GET", f"/merch/{merch_id}", expected_status=200, requires_auth=False)
    print_result(success, f"Obtener merchandising {merch_id} - Status: {response.status_code if response else 'N/A'}")

def test_update_merch(merch_id: int):
    """Prueba actualizar merchandising"""
    print_test_header(f"PATCH /merch/{merch_id} - Actualizar merchandising")
    
    update_data = {
        "title": "Updated Test Merch",
        "price": 30.00
    }
    
    success, response = make_request("PATCH", f"/merch/{merch_id}", update_data, 200)
    print_result(success, f"Actualizar merchandising {merch_id} - Status: {response.status_code if response else 'N/A'}")

def test_search_merch():
    """Prueba buscar merchandising"""
    print_test_header("GET /merch/search?q=Test - Buscar merchandising")
    
    success, response = make_request("GET", "/merch/search?q=Test", expected_status=200, requires_auth=False)
    print_result(success, f"Buscar merchandising - Status: {response.status_code if response else 'N/A'}")

def test_delete_merch(merch_id: int):
    """Prueba eliminar merchandising"""
    print_test_header(f"DELETE /merch/{merch_id} - Eliminar merchandising")
    
    success, response = make_request("DELETE", f"/merch/{merch_id}", expected_status=200)
    print_result(success, f"Eliminar merchandising {merch_id} - Status: {response.status_code if response else 'N/A'}")

# =============================================================================
# PRUEBAS DE ARTISTS
# =============================================================================

def test_list_artists():
    """Prueba obtener lista de artistas por IDs"""
    print_test_header("GET /artist/list - Obtener lista de artistas por IDs")
    
    # Buscar artistas existentes
    success, response = make_request("GET", "/artist/search?q=", expected_status=200, requires_auth=False)
    artist_ids = []
    
    if success and response:
        try:
            results = response.json()
            # Tomar los primeros 2 artistas
            artist_ids = [item.get("artistId") for item in results[:2] if "artistId" in item]
        except:
            pass
    
    if len(artist_ids) > 0:
        # Probar el endpoint list
        ids_param = ",".join(map(str, artist_ids))
        success, response = make_request("GET", f"/artist/list?ids={ids_param}", expected_status=200, requires_auth=False)
        
        if success and response:
            try:
                artists = response.json()
                print_result(len(artists) > 0, f"Recibidos {len(artists)} artistas")
                
                # Verificar estructura
                if len(artists) > 0:
                    first_artist = artists[0]
                    required_fields = ['artistId', 'artisticName', 'owner_songs', 'owner_albums', 'owner_merch']
                    has_all_fields = all(field in first_artist for field in required_fields)
                    print_result(has_all_fields, f"Estructura de datos completa")
            except Exception as e:
                print_result(False, f"Error al parsear respuesta: {e}")
        else:
            print_result(False, f"Error al obtener lista - Status: {response.status_code if response else 'N/A'}")
    else:
        print_result(True, "No hay artistas para probar (OK si no hay datos)")

def test_filter_artists():
    """Prueba filtrar artistas por géneros"""
    print_test_header("GET /artist/filter - Filtrar artistas")
    
    # Crear canción con género
    song_data = {
        "title": "Artist Filter Test Song",
        "genres": [1],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 3.99,
        "trackId": 950001,
        "duration": 150
    }
    
    success, response = make_request("POST", "/song/upload", song_data, 200)
    song_id = None
    artist_id = None
    
    if success and response:
        try:
            song_id = response.json().get("songId")
            
            # Obtener el artista de la canción
            success2, response2 = make_request("GET", f"/song/{song_id}", expected_status=200, requires_auth=False)
            if success2 and response2:
                song_info = response2.json()
                artist_id = song_info.get("artistId")
        except:
            pass
    
    if song_id and artist_id:
        # Filtrar por género
        success, response = make_request("GET", "/artist/filter?genres=1", expected_status=200, requires_auth=False)
        if success and response:
            try:
                results = response.json()  # Array de IDs
                artist_in_results = int(artist_id) in results
                print_result(artist_in_results, f"Artista {artist_id} encontrado en filtro por género")
            except Exception as e:
                print_result(False, f"Error al parsear respuesta: {e}")
        else:
            print_result(False, f"Error al filtrar - Status: {response.status_code if response else 'N/A'}")
        
        # Limpiar
        make_request("DELETE", f"/song/{song_id}")
    else:
        print_result(False, "No se pudo crear canción para la prueba")

def test_upload_artist():
    """Prueba crear un artista"""
    print_test_header("POST /artist/upload - Crear artista")
    
    artist_data = {
        "artisticName": "Test Artist",
        "artisticBiography": "Un artista de prueba",
        "artisticImage": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "artisticEmail": "test@artist.com",
        "socialMediaUrl": "https://twitter.com/testartist",
        "userId": 1
    }
    
    success, response = make_request("POST", "/artist/upload", artist_data, 200)
    print_result(success, f"Crear artista - Status: {response.status_code if response else 'N/A'}")
    
    if success and response:
        try:
            data = response.json()
            if "artistId" in data:
                print(f"  → Artist ID creado: {data['artistId']}")
                return data["artistId"]
        except:
            pass
    return None

def test_get_artist(artist_id: int):
    """Prueba obtener un artista por ID"""
    print_test_header(f"GET /artist/{artist_id} - Obtener artista")
    
    success, response = make_request("GET", f"/artist/{artist_id}", expected_status=200, requires_auth=False)
    print_result(success, f"Obtener artista {artist_id} - Status: {response.status_code if response else 'N/A'}")

def test_update_artist(artist_id: int):
    """Prueba actualizar un artista"""
    print_test_header(f"PATCH /artist/{artist_id} - Actualizar artista")
    
    update_data = {
        "artisticName": "Updated Test Artist",
        "artisticEmail": "updated@artist.com"
    }
    
    success, response = make_request("PATCH", f"/artist/{artist_id}", update_data, 200)
    print_result(success, f"Actualizar artista {artist_id} - Status: {response.status_code if response else 'N/A'}")

def test_search_artist():
    """Prueba buscar artistas"""
    print_test_header("GET /artist/search?q=Test - Buscar artista")
    
    success, response = make_request("GET", "/artist/search?q=Test", expected_status=200, requires_auth=False)
    print_result(success, f"Buscar artista - Status: {response.status_code if response else 'N/A'}")

def test_delete_artist(artist_id: int):
    """Prueba eliminar un artista"""
    print_test_header(f"DELETE /artist/{artist_id} - Eliminar artista")
    
    success, response = make_request("DELETE", f"/artist/{artist_id}", expected_status=200)
    print_result(success, f"Eliminar artista {artist_id} - Status: {response.status_code if response else 'N/A'}")

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def cleanup_all(song_ids, album_ids, merch_ids, artist_ids):
    """Elimina todos los objetos creados"""
    for sid in song_ids:
        make_request("DELETE", f"/song/{sid}", expected_status=200)
    for aid in album_ids:
        make_request("DELETE", f"/album/{aid}", expected_status=200)
    for mid in merch_ids:
        make_request("DELETE", f"/merch/{mid}", expected_status=200)
    for arid in artist_ids:
        make_request("DELETE", f"/artist/{arid}", expected_status=200)

def main():
    print(f"{Colors.YELLOW}")
    print("=" * 60)
    print("BANCO DE PRUEBAS AUTOMATIZADO - MICROSERVICIO TYA")
    print("Temas y Artistas - OverSounds Project")
    print("=" * 60)
    print(f"{Colors.RESET}")
    print(f"Servidor: {BASE_URL}")
    print(f"Token de Auth: {'configurado' if AUTH_TOKEN != 'your_test_token_here' else f'{Colors.RED}NO CONFIGURADO ⚠️{Colors.RESET}'}")
    
    # Advertir si el token no está configurado
    if AUTH_TOKEN == "your_test_token_here":
        print(f"\n{Colors.YELLOW}{'='*60}")
        print("⚠️  ADVERTENCIA: El token de autenticación NO está configurado")
        print("{'='*60}{Colors.RESET}")
        print("Las pruebas que requieren autenticación (upload, delete, patch)")
        print("fallarán con 401 Unauthorized.")
        print("\nPara configurar el token:")
        print("1. Edita el archivo test_api.py")
        print("2. Reemplaza 'your_test_token_here' con un token válido")
        print("3. El token debe ser obtenido del servicio de autenticación")
        print(f"{Colors.YELLOW}{'='*60}{Colors.RESET}\n")
        
        response = input("¿Deseas continuar de todos modos? (s/n): ")
        if response.lower() != 's':
            print("Pruebas canceladas.")
            sys.exit(0)
    
    print(f"\nIniciando pruebas...\n")
    
    # Verificar que el servidor esté disponible
    try:
        response = requests.get(BASE_URL)
        print(f"{Colors.GREEN}✓ Servidor disponible{Colors.RESET}\n")
    except:
        print(f"{Colors.RED}✗ Error: No se puede conectar al servidor en {BASE_URL}{Colors.RESET}")
        print(f"Asegúrate de que el servidor esté ejecutándose antes de ejecutar las pruebas.\n")
        sys.exit(1)
    
    # =========================================================================
    # SECCIÓN 1: ARTIST - Crear y probar todas las funcionalidades
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SECCIÓN 1: PRUEBAS COMPLETAS DE ARTIST")
    print(f"{'='*60}{Colors.RESET}")
    
    artist_id = test_upload_artist()
    if artist_id:
        test_get_artist(artist_id)
        test_update_artist(artist_id)
        test_search_artist()
    
    # NO limpiar el artist, lo necesitamos para el resto de pruebas
    
    # =========================================================================
    # SECCIÓN 2: ALBUM - Crear álbum sin canciones y probar
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SECCIÓN 2: PRUEBAS DE ALBUM (sin canciones)")
    print(f"{'='*60}{Colors.RESET}")
    
    album_ids = []
    album_id = test_upload_album([])
    if album_id:
        album_ids.append(album_id)
        test_get_album(album_id)
        test_update_album(album_id)
        test_search_album()
        test_upload_album_invalid_price()
    
    # Limpiar
    cleanup_all([], album_ids, [], [])
    
    # =========================================================================
    # SECCIÓN 2.5: NUEVOS ENDPOINTS DE ALBUM (list y filter)
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SECCIÓN 2.5: PRUEBAS DE NUEVOS ENDPOINTS DE ALBUM (list y filter)")
    print(f"{'='*60}{Colors.RESET}")
    
    test_list_albums()
    test_filter_albums()
    test_filter_albums_pagination()
    
    # =========================================================================
    # SECCIÓN 3: SONG SINGLE - Crear canción sin álbum y probar
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SECCIÓN 3: PRUEBAS DE SONG SINGLE (sin álbum)")
    print(f"{'='*60}{Colors.RESET}")
    
    song_ids = []
    song_id = test_upload_song()
    if song_id:
        song_ids.append(song_id)
        test_get_song(song_id)
        test_update_song(song_id)
        test_search_song()
        test_upload_song_invalid_price()
    
    # Limpiar
    cleanup_all(song_ids, [], [], [])
    
    # =========================================================================
    # SECCIÓN 3.5: NUEVOS ENDPOINTS DE SONG (list y filter)
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SECCIÓN 3.5: PRUEBAS DE NUEVOS ENDPOINTS DE SONG (list y filter)")
    print(f"{'='*60}{Colors.RESET}")
    
    test_list_songs()
    test_list_songs_invalid_id()
    test_list_songs_missing_param()
    test_filter_songs()
    test_filter_songs_missing_param()
    test_filter_songs_pagination()
    
    # =========================================================================
    # SECCIÓN 4: SONG con albumId desde creación
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SECCIÓN 4: Crear álbum vacío + canción con albumId desde inicio")
    print(f"{'='*60}{Colors.RESET}")
    
    song_ids = []
    album_ids = []
    
    # Crear álbum vacío
    print_test_header("Crear álbum vacío")
    empty_album_data = {
        "title": "Empty Album for Song Test",
        "songs": [],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 15.99
    }
    success, response = make_request("POST", "/album/upload", empty_album_data, 200)
    empty_album_id = None
    if success and response:
        try:
            empty_album_id = response.json().get("albumId")
            album_ids.append(empty_album_id)
            print_result(True, f"Álbum vacío creado con ID: {empty_album_id}")
        except:
            print_result(False, "Error al parsear respuesta de álbum vacío")
    else:
        print_result(False, f"Error al crear álbum vacío - Status: {response.status_code if response else 'N/A'}")
    
    # Crear canción con referencia al álbum
    if empty_album_id:
        print_test_header("Crear canción con albumId desde inicio")
        song_with_album_data = {
            "title": "Song With AlbumId",
            "genres": [1],
            "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
            "price": 4.99,
            "trackId": 300001,
            "duration": 180,
            "albumId": empty_album_id,
            "albumOrder": 1
        }
        success, response = make_request("POST", "/song/upload", song_with_album_data, 200)
        song_with_album_id = None
        if success and response:
            try:
                song_with_album_id = response.json().get("songId")
                song_ids.append(song_with_album_id)
                print_result(True, f"Canción creada con ID: {song_with_album_id}")
            except:
                print_result(False, "Error al parsear respuesta de canción")
        else:
            print_result(False, f"Error al crear canción - Status: {response.status_code if response else 'N/A'}")
        
        # Verificar que la canción está en el álbum
        if song_with_album_id:
            print_test_header("Verificar que canción está en el álbum")
            success, response = make_request("GET", f"/album/{empty_album_id}", expected_status=200)
            if success and response:
                try:
                    album_data = response.json()
                    songs_in_album = album_data.get("songs", [])
                    if song_with_album_id in songs_in_album:
                        print_result(True, f"✅ Canción {song_with_album_id} está en álbum {empty_album_id}")
                    else:
                        print_result(False, f"❌ Canción NO está en el álbum. Songs: {songs_in_album}")
                except Exception as e:
                    print_result(False, f"Error al parsear respuesta: {e}")
            else:
                print_result(False, f"Error al obtener álbum - Status: {response.status_code if response else 'N/A'}")
    
    # Limpiar
    cleanup_all(song_ids, album_ids, [], [])
    
    # =========================================================================
    # SECCIÓN 5: Crear álbum y song separados, luego UPDATE album
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SECCIÓN 5: Crear álbum y song separados + UPDATE álbum")
    print(f"{'='*60}{Colors.RESET}")
    
    song_ids = []
    album_ids = []
    
    # Crear álbum vacío
    print_test_header("Crear álbum vacío")
    album_for_update_data = {
        "title": "Album To Update",
        "songs": [],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 19.99
    }
    success, response = make_request("POST", "/album/upload", album_for_update_data, 200)
    album_update_id = None
    if success and response:
        try:
            album_update_id = response.json().get("albumId")
            album_ids.append(album_update_id)
            print_result(True, f"Álbum creado con ID: {album_update_id}")
        except:
            print_result(False, "Error al parsear respuesta de álbum")
    else:
        print_result(False, f"Error al crear álbum - Status: {response.status_code if response else 'N/A'}")
    
    # Crear canción CON albumId desde el inicio (esto establece albumog)
    if album_update_id:
        print_test_header("Crear canción con albumId desde inicio")
        song_with_album_data = {
            "title": "Song With AlbumId From Start",
            "genres": [1],
            "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
            "price": 3.99,
            "trackId": 400001,
            "duration": 200,
            "albumId": album_update_id,
            "albumOrder": 1
        }
        success, response = make_request("POST", "/song/upload", song_with_album_data, 200)
        single_update_id = None
        if success and response:
            try:
                single_update_id = response.json().get("songId")
                song_ids.append(single_update_id)
                print_result(True, f"Canción creada con albumId={album_update_id}: {single_update_id}")
            except:
                print_result(False, "Error al parsear respuesta de canción")
        else:
            print_result(False, f"Error al crear canción - Status: {response.status_code if response else 'N/A'}")
        
        # Verificar que la canción tiene el albumId correcto
        if single_update_id:
            print_test_header("Verificar que canción tiene albumId")
            success, response = make_request("GET", f"/song/{single_update_id}", expected_status=200, requires_auth=False)
            if success and response:
                try:
                    song_data = response.json()
                    song_album_id = song_data.get("albumId")
                    if song_album_id == album_update_id:
                        print_result(True, f"✅ Canción tiene albumId = {album_update_id}")
                    else:
                        print_result(False, f"❌ Canción albumId = {song_album_id}, esperado {album_update_id}")
                except Exception as e:
                    print_result(False, f"Error al parsear respuesta: {e}")
            else:
                print_result(False, f"Error al obtener canción - Status: {response.status_code if response else 'N/A'}")
    
    # Limpiar
    cleanup_all(song_ids, album_ids, [], [])
    
    # =========================================================================
    # SECCIÓN 6: MERCH - Crear y probar todas las funcionalidades
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SECCIÓN 6: PRUEBAS COMPLETAS DE MERCH")
    print(f"{'='*60}{Colors.RESET}")
    
    merch_ids = []
    merch_id = test_upload_merch()
    if merch_id:
        merch_ids.append(merch_id)
        test_get_merch(merch_id)
        test_update_merch(merch_id)
        test_search_merch()
        test_upload_merch_invalid_price()
    
    # Limpiar
    cleanup_all([], [], merch_ids, [])
    
    # =========================================================================
    # SECCIÓN 6.5: NUEVOS ENDPOINTS DE MERCH (list y filter)
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SECCIÓN 6.5: PRUEBAS DE NUEVOS ENDPOINTS DE MERCH (list y filter)")
    print(f"{'='*60}{Colors.RESET}")
    
    test_list_merch()
    test_filter_merch()
    test_filter_merch_pagination()
    
    # =========================================================================
    # SECCIÓN 7: Verificar campos owner_* en Artist
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SECCIÓN 7: Verificar campos owner_songs, owner_albums, owner_merch")
    print(f"{'='*60}{Colors.RESET}")
    
    song_ids = []
    album_ids = []
    merch_ids = []
    artist_ids = []
    
    # Crear artista (automático por autenticación)
    print_test_header("Crear objetos para verificar owner_*")
    
    # Crear álbum
    album_owner_data = {
        "title": "Owner Test Album",
        "songs": [],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 20.00
    }
    success, response = make_request("POST", "/album/upload", album_owner_data, 200)
    owner_album_id = None
    if success and response:
        try:
            owner_album_id = response.json().get("albumId")
            album_ids.append(owner_album_id)
            print_result(True, f"Álbum creado: {owner_album_id}")
        except:
            print_result(False, "Error al parsear respuesta de álbum")
    else:
        print_result(False, f"Error al crear álbum - Status: {response.status_code if response else 'N/A'}")
    
    # Crear canción
    song_owner_data = {
        "title": "Owner Test Song",
        "genres": [1],
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 5.00,
        "trackId": 500001,
        "duration": 190
    }
    success, response = make_request("POST", "/song/upload", song_owner_data, 200)
    owner_song_id = None
    if success and response:
        try:
            owner_song_id = response.json().get("songId")
            song_ids.append(owner_song_id)
            print_result(True, f"Canción creada: {owner_song_id}")
        except:
            print_result(False, "Error al parsear respuesta de canción")
    else:
        print_result(False, f"Error al crear canción - Status: {response.status_code if response else 'N/A'}")
    
    # Crear merch
    merch_owner_data = {
        "title": "Owner Test Merch",
        "description": "Merch para test owner",
        "cover": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAIAQMAAAD+wSzIAAAABlBMVEX///+/v7+jQ3Y5AAAADklEQVQI12P4AIX8EAgALgAD/aNpbtEAAAAASUVORK5CYII=",
        "price": 30.00
    }
    success, response = make_request("POST", "/merch/upload", merch_owner_data, 200)
    owner_merch_id = None
    if success and response:
        try:
            owner_merch_id = response.json().get("merchId")
            merch_ids.append(owner_merch_id)
            print_result(True, f"Merch creado: {owner_merch_id}")
        except:
            print_result(False, "Error al parsear respuesta de merch")
    else:
        print_result(False, f"Error al crear merch - Status: {response.status_code if response else 'N/A'}")
    
    # Obtener ID del artista del usuario autenticado buscando por nombre
    print_test_header("Obtener Artist del usuario autenticado")
    artist_name = "Test Artist"  # Reemplaza con el nombre del artista a buscar
    success, response = make_request("GET", f"/artist/search?q={artist_name}", expected_status=200, requires_auth=False)
    current_artist_id = None
    if success and response:
        try:
            artists = response.json()
            if len(artists) > 0:
                # Tomar el último artista (el más reciente)
                current_artist_id = artists[-1].get("artistId")
                artist_ids.append(current_artist_id)
                print_result(True, f"Artist encontrado: {current_artist_id}")
            else:
                print_result(False, "No se encontraron artistas")
        except:
            print_result(False, "Error al parsear respuesta de búsqueda")
    else:
        print_result(False, f"Error al buscar artista - Status: {response.status_code if response else 'N/A'}")
    
    # Verificar campos owner_* en el artista
    if current_artist_id:
        print_test_header("Verificar campos owner_* en Artist")
        success, response = make_request("GET", f"/artist/{current_artist_id}", expected_status=200, requires_auth=True)
        if success and response:
            try:
                artist_data = response.json()
                owner_songs = artist_data.get("owner_songs", [])
                owner_albums = artist_data.get("owner_albums", [])
                owner_merch = artist_data.get("owner_merch", [])
                
                print(f"  → owner_songs: {owner_songs}")
                print(f"  → owner_albums: {owner_albums}")
                print(f"  → owner_merch: {owner_merch}")
                
                checks = {
                    "owner_songs contiene la canción": owner_song_id in owner_songs if owner_song_id else False,
                    "owner_albums contiene el álbum": owner_album_id in owner_albums if owner_album_id else False,
                    "owner_merch contiene el merch": owner_merch_id in owner_merch if owner_merch_id else False
                }
                
                all_ok = all(checks.values())
                print_result(all_ok, f"✅ Todos los owner_* correctos" if all_ok else f"❌ Fallos: {[k for k, v in checks.items() if not v]}")
            except Exception as e:
                print_result(False, f"Error al parsear respuesta: {e}")
        else:
            print_result(False, f"Error al obtener artist - Status: {response.status_code if response else 'N/A'}")
    
    # Limpiar
    cleanup_all(song_ids, album_ids, merch_ids, [])
    
    # =========================================================================
    # SECCIÓN 7.5: NUEVOS ENDPOINTS DE ARTIST (list y filter)
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SECCIÓN 7.5: PRUEBAS DE NUEVOS ENDPOINTS DE ARTIST (list y filter)")
    print(f"{'='*60}{Colors.RESET}")
    
    test_list_artists()
    test_filter_artists()
    test_filter_artists_pagination()
    
    # =========================================================================
    # PRUEBAS ADICIONALES
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SECCIÓN 8: PRUEBAS DE AUTENTICACIÓN Y VALIDACIONES")
    print(f"{'='*60}{Colors.RESET}")
    
    test_unauthorized_access()
    test_search_without_auth()
    test_get_genres()
    test_upload_song_invalid_album()
    test_upload_song_missing_albumorder()
    test_upload_album_invalid_song()
    
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("SECCIÓN 9: PRUEBAS DE LINKED_ALBUMS")
    print(f"{'='*60}{Colors.RESET}")
    
    test_linked_albums()
    
    # =========================================================================
    # LIMPIEZA FINAL - Eliminar el artista creado al inicio
    # =========================================================================
    print(f"\n{Colors.YELLOW}{'='*60}")
    print("LIMPIEZA FINAL: Eliminar artista del usuario")
    print(f"{'='*60}{Colors.RESET}")
    
    if artist_id:
        test_delete_artist(artist_id)
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    print_summary()
    
    # Retornar código de salida apropiado
    sys.exit(0 if tests_failed == 0 else 1)

if __name__ == "__main__":
    main()

