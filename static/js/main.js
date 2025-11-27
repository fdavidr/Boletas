// BOLETAS-V1 - JavaScript Principal

// Función para mostrar alertas
function showAlert(message, type = 'success') {
    const alertDiv = document.getElementById('alert');
    if (alertDiv) {
        alertDiv.className = `alert alert-${type} show`;
        alertDiv.textContent = message;
        
        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            alertDiv.classList.remove('show');
        }, 5000);
    }
}

// Función para formatear números como moneda
function formatCurrency(value) {
    return parseFloat(value || 0).toFixed(2);
}

// Función para validar fecha formato dd/mm/yyyy
function isValidDate(dateString) {
    const regex = /^\d{2}\/\d{2}\/\d{4}$/;
    if (!regex.test(dateString)) return false;
    
    const parts = dateString.split('/');
    const day = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10);
    const year = parseInt(parts[2], 10);
    
    if (year < 1900 || year > 2100) return false;
    if (month < 1 || month > 12) return false;
    if (day < 1 || day > 31) return false;
    
    return true;
}

// Función para calcular días entre dos fechas
function calculateDaysBetween(startDate, endDate) {
    try {
        const start = parseDate(startDate);
        const end = parseDate(endDate);
        const diffTime = Math.abs(end - start);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
        return diffDays;
    } catch {
        return 0;
    }
}

// Función para parsear fecha dd/mm/yyyy a objeto Date
function parseDate(dateString) {
    const parts = dateString.split('/');
    return new Date(parts[2], parts[1] - 1, parts[0]);
}

// Función para obtener fecha actual en formato dd/mm/yyyy
function getCurrentDate() {
    const today = new Date();
    const day = String(today.getDate()).padStart(2, '0');
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const year = today.getFullYear();
    return `${day}/${month}/${year}`;
}

// Función para descargar PDF
function downloadPDF(filename) {
    window.location.href = `/api/download/${filename}`;
}

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    // Resaltar enlace activo en navegación
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Establecer fecha actual en campos de fecha de emisión
    const fechaEmisionInputs = document.querySelectorAll('input[name="fecha_emision"]');
    fechaEmisionInputs.forEach(input => {
        if (!input.value) {
            input.value = getCurrentDate();
        }
    });
});

// Manejo de inputs numéricos para formatear automáticamente
document.addEventListener('DOMContentLoaded', function() {
    const numericInputs = document.querySelectorAll('input[type="number"]');
    
    numericInputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.value) {
                this.value = formatCurrency(this.value);
            }
        });
    });
});
