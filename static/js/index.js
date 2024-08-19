function addClassToElementById(elementId, className) {
    // Espera a que el contenido del DOM esté completamente cargado
    document.addEventListener('DOMContentLoaded', () => {
        // Obtén el elemento por su ID
        const element = document.getElementById(elementId);

        // Verifica si el elemento existe
        if (element) {
            // Agrega la clase al elemento
            element.classList.add(className);
        } else {
            console.error(`No se encontró el elemento con el ID '${elementId}'.`);
        }
    });
}
