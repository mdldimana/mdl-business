from locust import HttpUser, task, between
import random


class MDLBusinessUser(HttpUser):
    """Simule un utilisateur de MDL Business"""

    wait_time = between(1, 5)  # Temps d'attente entre 1 et 5 secondes

    # Identifiants de test
    test_email = "admin@mdlbusiness.com"
    test_password = "admin123"

    def on_start(self):
        """Actions au début de la session"""
        # Visiter la page d'accueil
        self.client.get("/")
        print("✅ Début de la session")

    @task(3)  # 3 fois plus de chance d'être exécuté
    def accueil(self):
        """Visite la page d'accueil"""
        self.client.get("/")

    @task(2)
    def produits(self):
        """Visite la page des produits"""
        self.client.get("/produits")

    @task(2)
    def services(self):
        """Visite la page des services"""
        self.client.get("/services")

    @task(1)
    def detail_produit(self):
        """Visite le détail d'un produit aléatoire"""
        # Récupérer la liste des produits (simulé)
        product_slugs = [
            "rolex-submariner",
            "apple-watch-ultra",
            "sac-cuir-vintage",
            "portefeuille-cuir-homme",
            "sony-wh-1000xm5",
            "jbl-charge-5"
        ]
        slug = random.choice(product_slugs)
        self.client.get(f"/produit/{slug}")

    @task(1)
    def connexion(self):
        """Simule une tentative de connexion"""
        self.client.post("/connexion", {
            "email": self.test_email,
            "mot_de_passe": self.test_password
        })

    @task(1)
    def panier(self):
        """Visite la page du panier"""
        self.client.get("/panier")

    @task(1)
    def admin(self):
        """Visite le tableau de bord admin (si connecté)"""
        self.client.get("/admin")

    @task(2)
    def categories(self):
        """Visite les catégories"""
        categories = ["montres", "accessoires", "electronique", "services"]
        slug = random.choice(categories)
        self.client.get(f"/categorie/{slug}")