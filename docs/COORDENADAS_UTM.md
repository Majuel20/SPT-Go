# Coordenadas UTM

Indica zona UTM de 1 a 60, hemisferio Norte o Sur, y coordenadas Este/Norte en metros. El origen es común para corriente, potencial y circunferencias. El segundo punto de corriente solo fija la dirección; la distancia al pozo define la ubicación efectiva de C100%. En OFF, cada par `Este, Norte;` fija una dirección independiente de potencial desde el mismo origen. En ON se usa la dirección de corriente.

Confirma zona, hemisferio, datum y unidades antes de trabajar. La aplicación transforma desde el EPSG UTM WGS84 correspondiente hacia WGS84 geográfico; no convierte otros datums locales. La vista no muestra terreno, obstáculos ni servidumbres. Para ubicar el pozo exactamente en el segundo punto, usa la distancia euclidiana entre origen y punto de dirección.
