from pydub import AudioSegment
import os
import re
from typing import List, Optional


def find_audio_files(directory: str = ".", pattern: str = "output_") -> List[str]:
    """
    Encuentra archivos de audio que coincidan con el patrón especificado.

    Args:
        directory (str): Directorio donde buscar los archivos
        pattern (str): Patrón inicial del nombre de archivo

    Returns:
        List[str]: Lista de rutas completas de los archivos encontrados, ordenados numéricamente
    """
    # Encontrar todos los archivos que coincidan con el patrón
    audio_files = [
        f for f in os.listdir(directory) if f.startswith(pattern) and f.endswith(".wav")
    ]
    print(
        f"Encontrados {len(audio_files)} archivos que coinciden con el patrón '{pattern}'"
    )

    # Extraer números y ordenar archivos
    def get_number(filename: str) -> int:
        match = re.search(rf"{pattern}(\d+)", filename)
        return int(match.group(1)) if match else -1

    audio_files.sort(key=get_number)

    # Devolver las rutas completas
    return [os.path.join(directory, f) for f in audio_files]


def combine_audio_files(
    audio_paths: List[str], output_file: str = "combined_output.wav"
) -> Optional[str]:
    """
    Combina una lista de archivos de audio en un solo archivo.

    Args:
        audio_paths (List[str]): Lista de rutas de archivos de audio a combinar
        output_file (str): Nombre del archivo de salida

    Returns:
        Optional[str]: Ruta del archivo combinado o None si hay un error
    """
    if not audio_paths:
        print("No hay archivos para combinar.")
        return None

    try:
        # Cargar el primer archivo como base
        print(f"Iniciando combinación de {len(audio_paths)} archivos...")
        combined = AudioSegment.from_file(audio_paths[0])
        print(f"Añadido: {os.path.basename(audio_paths[0])}")

        # Añadir el resto de archivos
        for audio_path in audio_paths[1:]:
            try:
                audio = AudioSegment.from_file(audio_path)
                combined += audio
                print(f"Añadido: {os.path.basename(audio_path)}")
            except Exception as e:
                print(f"Error al procesar {audio_path}: {str(e)}")
                continue

        # Guardar el resultado
        combined.export(output_file, format="wav")
        print(f"\nArchivo final guardado como: {output_file}")
        return output_file

    except Exception as e:
        print(f"Error durante la combinación: {str(e)}")
        return None


def execute_audio_combination(
    directory: str = ".",
    pattern: str = "output_",
    output_file: str = "combined_output.wav",
):
    """
    Función principal que orquesta el proceso de búsqueda y combinación.

    Args:
        directory (str): Directorio donde buscar los archivos
        pattern (str): Patrón inicial del nombre de archivo
        output_file (str): Nombre del archivo de salida
    """
    # Encontrar archivos
    audio_paths = find_audio_files(directory, pattern)

    if not audio_paths:
        print(
            f"No se encontraron archivos que coincidan con el patrón '{pattern}' en {directory}"
        )
        return

    # Combinar archivos
    result = combine_audio_files(audio_paths, output_file)

    if result:
        print("Proceso completado exitosamente")
    else:
        print("El proceso falló")


if __name__ == "__main__":
    # Ejemplo de uso
    execute_audio_combination(
        directory=".", pattern="output_", output_file="combined_output.wav"
    )
