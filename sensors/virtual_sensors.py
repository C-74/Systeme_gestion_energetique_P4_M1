class VirtualSensor:
    def __init__(self, name: str, sensor_type: str):
        """
        Initialise un capteur virtuel.
        :param name: Nom du capteur (ex: 'Compteur Principal')
        :param sensor_type: Type de capteur ('consommation', 'solaire', 'stockage')
        """
        self.name = name
        self.sensor_type = sensor_type
        self.status = "Actif"

    def read_value(self):
        """
        Méthode pour lire la valeur actuelle du capteur.
        La génération de données est désactivée pour le moment.
        """
        pass
        
    def get_info(self):
        return {
            "name": self.name,
            "type": self.sensor_type,
            "status": self.status
        }
