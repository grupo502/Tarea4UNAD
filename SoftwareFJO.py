"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas - Software FJ
Programación Orientada a Objetos con manejo avanzado de excepciones
"""

import re
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Dict, Any

# ==================== CONFIGURACIÓN DE LOGS ====================

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    filename='logs/eventos.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def registrar_evento(mensaje: str, nivel: str = "info"):
    """Registra eventos y errores en el archivo de logs"""
    if nivel == "error":
        logging.error(mensaje)
    elif nivel == "warning":
        logging.warning(mensaje)
    else:
        logging.info(mensaje)


# ==================== EXCEPCIONES PERSONALIZADAS ====================

class DatosClienteInvalidosError(Exception):
    """Excepción lanzada cuando los datos del cliente no son válidos"""
    pass


class ServicioNoDisponibleError(Exception):
    """Excepción lanzada cuando el servicio solicitado no está disponible"""
    pass


class ReservaInvalidaError(Exception):
    """Excepción lanzada cuando los parámetros de la reserva son incorrectos"""
    pass


class ClienteNoEncontradoError(Exception):
    """Excepción lanzada cuando no se encuentra un cliente"""
    pass


# ==================== CLASE CLIENTE ====================

class Cliente:
    """
    Clase que representa un cliente del sistema.
    Implementa encapsulación con properties y validaciones robustas.
    """
    
    def __init__(self, nombre: str, email: str, telefono: str):
        self._nombre = None
        self._email = None
        self._telefono = None
        self._activo = True
        
        self.nombre = nombre
        self.email = email
        self.telefono = telefono
        
        registrar_evento(f"Cliente creado exitosamente: {self._nombre}")
    
    @property
    def nombre(self) -> str:
        return self._nombre
    
    @nombre.setter
    def nombre(self, valor: str):
        if not valor or len(valor.strip()) < 3:
            raise DatosClienteInvalidosError(
                f"El nombre debe tener al menos 3 caracteres. Valor recibido: '{valor}'"
            )
        if len(valor.strip()) > 100:
            raise DatosClienteInvalidosError(
                f"El nombre no puede exceder los 100 caracteres"
            )
        self._nombre = valor.strip()
    
    @property
    def email(self) -> str:
        return self._email
    
    @email.setter
    def email(self, valor: str):
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not valor or not re.match(patron, valor):
            raise DatosClienteInvalidosError(
                f"Formato de email inválido. Debe ser usuario@dominio.com"
            )
        self._email = valor.lower().strip()
    
    @property
    def telefono(self) -> str:
        return self._telefono
    
    @telefono.setter
    def telefono(self, valor: str):
        if not valor:
            raise DatosClienteInvalidosError("El teléfono no puede estar vacío")
        if not valor.isdigit():
            raise DatosClienteInvalidosError(
                f"El teléfono debe contener solo dígitos"
            )
        if len(valor) < 7 or len(valor) > 15:
            raise DatosClienteInvalidosError(
                f"El teléfono debe tener entre 7 y 15 dígitos"
            )
        self._telefono = valor
    
    @property
    def activo(self) -> bool:
        return self._activo
    
    def desactivar(self):
        self._activo = False
        registrar_evento(f"Cliente {self._nombre} ha sido desactivado")
    
    def __str__(self) -> str:
        estado = "Activo" if self._activo else "Inactivo"
        return f"{self._nombre} | Email: {self._email} | Tel: {self._telefono} | {estado}"


# ==================== CLASE ABSTRACTA SERVICIO ====================

class Servicio(ABC):
    """Clase abstracta que define el contrato para todos los servicios"""
    
    def __init__(self, nombre: str, precio_base: float, descripcion: str = ""):
        self.nombre = nombre
        self.precio_base = precio_base
        self.descripcion = descripcion
        self._disponible = True
    
    @abstractmethod
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        pass
    
    @abstractmethod
    def describir(self) -> str:
        pass
    
    def validar_parametros(self, duracion: float, **kwargs) -> bool:
        if duracion <= 0:
            raise ValueError(f"La duración debe ser positiva. Recibido: {duracion}")
        if duracion > 720:
            raise ValueError(f"La duración no puede exceder 720 horas")
        return True
    
    @property
    def disponible(self) -> bool:
        return self._disponible


# ==================== SERVICIOS CONCRETOS ====================

class ReservaSala(Servicio):
    def __init__(self, nombre: str = "Sala de Conferencias", precio_base: float = 50000, 
                 capacidad: int = 10):
        super().__init__(nombre, precio_base, "Reserva de salas para reuniones")
        self.capacidad = capacidad
        self._costo_extra_hora = 15000
    
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        self.validar_parametros(duracion)
        incluye_catering = kwargs.get('incluye_catering', False)
        
        if duracion <= 2:
            costo = self.precio_base
        else:
            costo = self.precio_base + (duracion - 2) * self._costo_extra_hora
        
        if incluye_catering:
            costo += duracion * 8000
        return costo
    
    def describir(self) -> str:
        return f"🏢 {self.nombre} | Capacidad: {self.capacidad} | Base: ${self.precio_base:,.0f} (2h) | Hora extra: ${self._costo_extra_hora:,.0f}"


class AlquilerEquipo(Servicio):
    def __init__(self, nombre: str = "Laptop", precio_base: float = 30000,
                 especificaciones: str = ""):
        super().__init__(nombre, precio_base, "Alquiler de equipos tecnológicos")
        self.especificaciones = especificaciones or "Equipo estándar"
        self._costo_seguro_diario = 5000
    
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        self.validar_parametros(duracion)
        seguro = kwargs.get('seguro', False)
        
        costo = self.precio_base * duracion
        if seguro:
            costo += duracion * self._costo_seguro_diario
        return costo
    
    def describir(self) -> str:
        return f"💻 {self.nombre} | ${self.precio_base:,.0f}/día | Seguro: ${self._costo_seguro_diario:,.0f}/día"


class AsesoriaEspecializada(Servicio):
    def __init__(self, nombre: str = "Asesoría Técnica", precio_base: float = 45000,
                 especialidad: str = ""):
        super().__init__(nombre, precio_base, "Asesorías especializadas por hora")
        self.especialidad = especialidad or "Desarrollo de software"
        self._descuento_paquete = 0.10
    
    def calcular_costo(self, duracion: float, **kwargs) -> float:
        self.validar_parametros(duracion)
        es_paquete = kwargs.get('es_paquete', duracion > 5)
        
        costo = self.precio_base * duracion
        if es_paquete and duracion > 5:
            costo *= (1 - self._descuento_paquete)
        return costo
    
    def describir(self) -> str:
        return f"🎓 {self.nombre} | ${self.precio_base:,.0f}/hora | Especialidad: {self.especialidad} | Descuento 10% (5+ horas)"


# ==================== CLASE RESERVA ====================

class Reserva:
    _contador = 1
    
    def __init__(self, cliente: Cliente, servicio: Servicio, duracion: float, 
                 fecha: Optional[datetime] = None, notas: str = ""):
        
        if not cliente.activo:
            raise ReservaInvalidaError(f"El cliente {cliente.nombre} está inactivo")
        
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible")
        
        self.id = Reserva._contador
        Reserva._contador += 1
        
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.fecha = fecha or datetime.now()
        self.notas = notas
        self._estado = "PENDIENTE"
        self._costo_total = None
        
        registrar_evento(f"Reserva #{self.id} creada para {cliente.nombre}")
    
    @property
    def estado(self) -> str:
        return self._estado
    
    def confirmar(self) -> 'Reserva':
        try:
            self.servicio.validar_parametros(self.duracion)
            
            if self._estado == "CANCELADA":
                raise ReservaInvalidaError("No se puede confirmar una reserva cancelada")
            
            if self._estado == "CONFIRMADA":
                return self
            
        except ValueError as e:
            raise ReservaInvalidaError(f"Error en validación: {e}")
        
        self._estado = "CONFIRMADA"
        registrar_evento(f"Reserva #{self.id} confirmada")
        return self
    
    def cancelar(self, motivo: str = "Sin especificar") -> 'Reserva':
        if self._estado == "CANCELADA":
            raise ReservaInvalidaError("La reserva ya estaba cancelada")
        
        if self._estado == "PROCESADA":
            raise ReservaInvalidaError("No se puede cancelar una reserva procesada")
        
        self._estado = "CANCELADA"
        registrar_evento(f"Reserva #{self.id} cancelada. Motivo: {motivo}")
        return self
    
    def procesar(self) -> float:
        if self._estado != "CONFIRMADA":
            raise ReservaInvalidaError(
                f"No se puede procesar una reserva en estado '{self._estado}'"
            )
        
        self._costo_total = self.servicio.calcular_costo(self.duracion)
        self._estado = "PROCESADA"
        registrar_evento(f"Reserva #{self.id} procesada. Costo: ${self._costo_total:,.2f}")
        return self._costo_total
    
    # Método sobrecargado (simulado con parámetros por defecto)
    def calcular_costo_con_impuestos(self, tasa_impuesto: float = 0.19, 
                                      descuento: float = 0.0) -> float:
        costo_base = self.servicio.calcular_costo(self.duracion)
        costo_con_impuesto = costo_base * (1 + tasa_impuesto)
        costo_final = costo_con_impuesto * (1 - descuento)
        return costo_final
    
    def __str__(self) -> str:
        costo_str = f"${self._costo_total:,.2f}" if self._costo_total else "Pendiente"
        return f"Reserva #{self.id} | {self.cliente.nombre} | {self.servicio.nombre} | {self._estado} | Costo: {costo_str}"


# ==================== GESTOR DEL SISTEMA ====================

class GestorSistema:
    def __init__(self):
        self.clientes: List[Cliente] = []
        self.servicios: List[Servicio] = []
        self.reservas: List[Reserva] = []
        self._inicializar_servicios()
    
    def _inicializar_servicios(self):
        self.servicios = [
            ReservaSala("Sala Ejecutiva", 80000, capacidad=20),
            ReservaSala("Sala de Reuniones", 35000, capacidad=6),
            AlquilerEquipo("Laptop HP ProBook", 45000, "Intel i7, 16GB RAM"),
            AlquilerEquipo("iPad Pro", 25000, "12.9\", 256GB"),
            AsesoriaEspecializada("Python Avanzado", 60000, "Desarrollo Backend"),
            AsesoriaEspecializada("Arquitectura Software", 75000, "Diseño sistemas")
        ]
        registrar_evento(f"Sistema inicializado con {len(self.servicios)} servicios")
    
    def registrar_cliente(self, nombre: str, email: str, telefono: str) -> Cliente:
        cliente = Cliente(nombre, email, telefono)
        self.clientes.append(cliente)
        registrar_evento(f"Cliente registrado: {nombre}")
        return cliente
    
    def crear_reserva(self, cliente_id: int, servicio_id: int, duracion: float, 
                     notas: str = "") -> Reserva:
        if cliente_id < 0 or cliente_id >= len(self.clientes):
            raise ClienteNoEncontradoError(f"Cliente con ID {cliente_id} no encontrado")
        
        if servicio_id < 0 or servicio_id >= len(self.servicios):
            raise ServicioNoDisponibleError(f"Servicio con ID {servicio_id} no encontrado")
        
        cliente = self.clientes[cliente_id]
        servicio = self.servicios[servicio_id]
        
        reserva = Reserva(cliente, servicio, duracion, notas=notas)
        reserva.confirmar()
        self.reservas.append(reserva)
        
        registrar_evento(f"Reserva creada: #{reserva.id}")
        return reserva
    
    def procesar_reserva(self, reserva_id: int) -> float:
        for reserva in self.reservas:
            if reserva.id == reserva_id:
                return reserva.procesar()
        raise ReservaInvalidaError(f"Reserva con ID {reserva_id} no existe")
    
    def cancelar_reserva(self, reserva_id: int, motivo: str = "") -> bool:
        for reserva in self.reservas:
            if reserva.id == reserva_id:
                reserva.cancelar(motivo or "Cancelado por usuario")
                return True
        raise ReservaInvalidaError(f"Reserva con ID {reserva_id} no existe")
    
    def listar_clientes(self) -> List[str]:
        return [f"{i}. {c}" for i, c in enumerate(self.clientes)]
    
    def listar_servicios(self) -> List[str]:
        return [f"{i}. {s.describir()}" for i, s in enumerate(self.servicios)]
    
    def listar_reservas(self) -> List[str]:
        return [str(r) for r in self.reservas] if self.reservas else ["No hay reservas"]
    
    def obtener_resumen(self) -> Dict[str, Any]:
        return {
            "total_clientes": len(self.clientes),
            "clientes_activos": sum(1 for c in self.clientes if c.activo),
            "total_servicios": len(self.servicios),
            "total_reservas": len(self.reservas),
            "reservas_confirmadas": sum(1 for r in self.reservas if r.estado == "CONFIRMADA"),
            "reservas_procesadas": sum(1 for r in self.reservas if r.estado == "PROCESADA"),
            "reservas_canceladas": sum(1 for r in self.reservas if r.estado == "CANCELADA")
        }


# ==================== MENÚ INTERACTIVO ====================

def limpiar_pantalla():
    """Limpia la consola"""
    os.system('cls' if os.name == 'nt' else 'clear')


def pausa():
    """Pausa hasta que el usuario presione Enter"""
    input("\nPresione Enter para continuar...")


def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "="*70)
    print("           SISTEMA INTEGRAL SOFTWARE FJ - MENÚ INTERACTIVO")
    print("="*70)
    print("  1. Registrar cliente")
    print("  2. Listar clientes")
    print("  3. Ver servicios disponibles")
    print("  4. Crear reserva")
    print("  5. Procesar reserva")
    print("  6. Cancelar reserva")
    print("  7. Listar reservas")
    print("  8. Ver resumen del sistema")
    print("  9. Calcular costo con impuestos (Método sobrecargado)")
    print("  0. Salir")
    print("="*70)


def menu_interactivo():
    """Función principal del menú interactivo"""
    gestor = GestorSistema()
    
    print("\n" + "="*70)
    print("   SISTEMA INTEGRAL DE GESTIÓN - SOFTWARE FJ")
    print("="*70)
    print("\n📁 Todos los eventos se registran en 'logs/eventos.log'")
    print("✅ Sistema listo para operar\n")
    
    while True:
        mostrar_menu()
        opcion = input("\n🔹 Seleccione una opción: ").strip()
        
        try:
            # Opción 1: Registrar cliente
            if opcion == "1":
                print("\n--- REGISTRAR CLIENTE ---")
                nombre = input("Nombre (mínimo 3 caracteres): ").strip()
                email = input("Email (ejemplo@dominio.com): ").strip()
                telefono = input("Teléfono (solo números, 7-15 dígitos): ").strip()
                
                cliente = gestor.registrar_cliente(nombre, email, telefono)
                print(f"\n✅ Cliente registrado exitosamente!")
                print(f"   {cliente}")
                registrar_evento(f"Operación exitosa: Cliente registrado - {nombre}")
            
            # Opción 2: Listar clientes
            elif opcion == "2":
                print("\n--- LISTA DE CLIENTES ---")
                clientes = gestor.listar_clientes()
                if clientes:
                    for c in clientes:
                        print(f"  {c}")
                else:
                    print("  ⚠️ No hay clientes registrados.")
            
            # Opción 3: Ver servicios
            elif opcion == "3":
                print("\n--- SERVICIOS DISPONIBLES ---")
                servicios = gestor.listar_servicios()
                for s in servicios:
                    print(f"  {s}")
            
            # Opción 4: Crear reserva
            elif opcion == "4":
                print("\n--- CREAR RESERVA ---")
                
                if not gestor.clientes:
                    print("❌ No hay clientes registrados. Registre un cliente primero.")
                    pausa()
                    continue
                
                print("\n📋 Clientes disponibles:")
                for c in gestor.listar_clientes():
                    print(f"   {c}")
                
                cliente_id = int(input("\nID del cliente: "))
                
                print("\n📋 Servicios disponibles:")
                for s in gestor.listar_servicios():
                    print(f"   {s}")
                
                servicio_id = int(input("ID del servicio: "))
                duracion = float(input("Duración (en horas): "))
                notas = input("Notas adicionales (opcional): ")
                
                reserva = gestor.crear_reserva(cliente_id, servicio_id, duracion, notas)
                print(f"\n✅ Reserva creada exitosamente!")
                print(f"   {reserva}")
                registrar_evento(f"Operación exitosa: Reserva creada - ID {reserva.id}")
            
            # Opción 5: Procesar reserva
            elif opcion == "5":
                print("\n--- PROCESAR RESERVA ---")
                
                if not gestor.reservas:
                    print("⚠️ No hay reservas para procesar.")
                    pausa()
                    continue
                
                print("\n📋 Reservas disponibles:")
                for r in gestor.listar_reservas():
                    print(f"   {r}")
                
                reserva_id = int(input("\nID de la reserva a procesar: "))
                costo = gestor.procesar_reserva(reserva_id)
                print(f"\n✅ Reserva procesada exitosamente!")
                print(f"   Costo total: ${costo:,.2f}")
                registrar_evento(f"Operación exitosa: Reserva procesada - ID {reserva_id}")
            
            # Opción 6: Cancelar reserva
            elif opcion == "6":
                print("\n--- CANCELAR RESERVA ---")
                
                if not gestor.reservas:
                    print("⚠️ No hay reservas para cancelar.")
                    pausa()
                    continue
                
                print("\n📋 Reservas activas:")
                for r in gestor.reservas:
                    if r.estado != "CANCELADA":
                        print(f"   {r}")
                
                reserva_id = int(input("\nID de la reserva a cancelar: "))
                motivo = input("Motivo de cancelación (opcional): ")
                
                gestor.cancelar_reserva(reserva_id, motivo)
                print(f"\n✅ Reserva #{reserva_id} cancelada exitosamente!")
                registrar_evento(f"Operación exitosa: Reserva cancelada - ID {reserva_id}")
            
            # Opción 7: Listar reservas
            elif opcion == "7":
                print("\n--- LISTA DE RESERVAS ---")
                reservas = gestor.listar_reservas()
                for r in reservas:
                    print(f"  • {r}")
            
            # Opción 8: Resumen del sistema
            elif opcion == "8":
                print("\n--- RESUMEN DEL SISTEMA ---")
                resumen = gestor.obtener_resumen()
                print(f"\n📊 CLIENTES:")
                print(f"   Total: {resumen['total_clientes']}")
                print(f"   Activos: {resumen['clientes_activos']}")
                print(f"\n📊 SERVICIOS:")
                print(f"   Disponibles: {resumen['total_servicios']}")
                print(f"\n📊 RESERVAS:")
                print(f"   Total: {resumen['total_reservas']}")
                print(f"   Confirmadas: {resumen['reservas_confirmadas']}")
                print(f"   Procesadas: {resumen['reservas_procesadas']}")
                print(f"   Canceladas: {resumen['reservas_canceladas']}")
            
            # Opción 9: Método sobrecargado
            elif opcion == "9":
                print("\n--- CÁLCULO CON IMPUESTOS Y DESCUENTOS (Método Sobrecargado) ---")
                
                if not gestor.reservas:
                    print("⚠️ No hay reservas para calcular.")
                    pausa()
                    continue
                
                print("\n📋 Reservas disponibles:")
                for r in gestor.reservas:
                    if r.estado == "PROCESADA":
                        print(f"   {r}")
                
                reserva_id = int(input("\nID de la reserva: "))
                
                # Buscar la reserva
                reserva_encontrada = None
                for r in gestor.reservas:
                    if r.id == reserva_id:
                        reserva_encontrada = r
                        break
                
                if not reserva_encontrada:
                    print("❌ Reserva no encontrada")
                else:
                    print("\n📊 Opciones de cálculo:")
                    print("  1. Solo impuesto (19%)")
                    print("  2. Impuesto (19%) + Descuento (10%)")
                    
                    subopcion = input("Seleccione: ")
                    
                    if subopcion == "1":
                        costo = reserva_encontrada.calcular_costo_con_impuestos(0.19, 0)
                        print(f"\n✅ Costo con 19% de impuesto: ${costo:,.2f}")
                    elif subopcion == "2":
                        costo = reserva_encontrada.calcular_costo_con_impuestos(0.19, 0.10)
                        print(f"\n✅ Costo con 19% impuesto + 10% descuento: ${costo:,.2f}")
                    else:
                        print("❌ Opción no válida")
            
            # Opción 0: Salir
            elif opcion == "0":
                print("\n" + "="*70)
                print("👋 ¡Gracias por usar el Sistema Integral FJ!")
                print("📁 Revisa los logs en la carpeta 'logs/eventos.log'")
                print("="*70)
                break
            
            else:
                print("❌ Opción no válida. Intente nuevamente.")
        
        except DatosClienteInvalidosError as e:
            print(f"\n❌ ERROR EN DATOS DEL CLIENTE: {e}")
            registrar_evento(f"Error: {e}", nivel="error")
        
        except ServicioNoDisponibleError as e:
            print(f"\n❌ ERROR EN SERVICIO: {e}")
            registrar_evento(f"Error: {e}", nivel="error")
        
        except ReservaInvalidaError as e:
            print(f"\n❌ ERROR EN RESERVA: {e}")
            registrar_evento(f"Error: {e}", nivel="error")
        
        except ClienteNoEncontradoError as e:
            print(f"\n❌ ERROR: {e}")
            registrar_evento(f"Error: {e}", nivel="error")
        
        except ValueError as e:
            print(f"\n❌ ERROR DE VALOR: Ingrese un número válido")
            registrar_evento(f"Error de valor: {e}", nivel="error")
        
        except Exception as e:
            print(f"\n❌ ERROR INESPERADO: {e}")
            registrar_evento(f"Error inesperado: {e}", nivel="error")
        
        pausa()


# ==================== PUNTO DE ENTRADA ====================

if __name__ == "__main__":
    menu_interactivo()