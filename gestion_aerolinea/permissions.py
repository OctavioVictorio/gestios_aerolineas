from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """Permite el acceso solo a usuarios con perfil 'admin'."""
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'perfil') and 
            request.user.perfil == 'admin'
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite acceso de LECTURA (GET, HEAD, OPTIONS) a cualquiera, 
    y acceso total (POST, PUT, DELETE) solo a usuarios 'admin'.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return IsAdmin().has_permission(request, view)


class IsClienteOrAdmin(permissions.BasePermission):
    """
    Permite acceso a 'admin' y acceso a la creación/consulta 
    de recursos propios al 'cliente'. Usado para Reservas/Boletos.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.perfil in ['admin', 'empleado']:
            return True
        
        if request.user.perfil == 'cliente':
            return True
            
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.perfil in ['admin', 'empleado']:
            return True
        
        if request.user.perfil == 'cliente':
            if hasattr(obj, 'usuario_reserva'):
                return obj.usuario_reserva == request.user
            elif hasattr(obj, 'reserva') and hasattr(obj.reserva, 'usuario_reserva'):
                return obj.reserva.usuario_reserva == request.user
                
        return False