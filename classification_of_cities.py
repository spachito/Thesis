import math
import operator

class UrbanClassifier:
    def __init__(self):
        # ==============================================================================
        # 1.ΟΙ ΠΑΡΟΝΟΜΑΣΤΕΣ ΓΙΑ ΤΗΝ ΚΑΝΟΝΙΚΟΠΟΙΗΣΗ
        # ==============================================================================
        self.MAX_VALS = {
            "population": 40_000_000,    # Safety Cap (Tokyo Metro is ~38M)
            "density": 46_000,           # Manila (people/km2)
            "tourists": 30_000_000,      # Top Global Destinations annually
            "gdp_per_capita": 140_000,   # dollars $
            "traffic_index": 120,        # Hours lost per year in traffic
            "internet_speed": 350,       # Mbps
            "innovation_score": 100      # Global Innovation Index
        }

        # ==============================================================================
        # 2. PROFILES (CLUSTER CENTROIDS)
        # Οι τιμές προκύπτουν από τον Μέσο Όρο των 5 Πόλεων Αναφοράς του Brookings.
        # ==============================================================================
        self.profiles = {
            # ΚΑΤΗΓΟΡΙΑ 1: GLOBAL GIANTS
            # Πόλεις: Λονδίνο, Τόκιο, Νέα Υόρκη, Χονγκ Κονγκ, Λος Άντζελες
            
            "1. Global Giants": {
                "population": 0.60,     
                "density": 0.45,        
                "tourists": 0.85,       
                "gdp_per_capita": 0.80, 
                "traffic_index": 0.85,  
                "internet_speed": 0.80, 
                "innovation_score": 0.95
            },
            
            # ΚΑΤΗΓΟΡΙΑ 2: ASIAN ANCHORS
            # Πόλεις: Σιγκαπούρη, Σεούλ, Πεκίνο, Οσάκα, Μόσχα
            
            "2. Asian Anchors": {
                "population": 0.55,     
                "density": 0.60,        
                "tourists": 0.50,       
                "gdp_per_capita": 0.55, 
                "traffic_index": 0.80,  
                "internet_speed": 0.90, 
                "innovation_score": 0.85 
            },

            # ΚΑΤΗΓΟΡΙΑ 3: EMERGING GATEWAYS
            # Πόλεις: Σάο Πάολο, Γιοχάνεσμπουργκ, Μπογκοτά, Πόλη του Μεξικό, Τζακάρτα
            
            "3. Emerging Gateways": {
                "population": 0.55,     
                "density": 0.50,        
                "tourists": 0.25,       
                "gdp_per_capita": 0.15, 
                "traffic_index": 0.98,  
                "internet_speed": 0.30, 
                "innovation_score": 0.35 
            },

            # ΚΑΤΗΓΟΡΙΑ 4: INDUSTRIAL ENGINES
            # Πόλεις: Τιαντζίν, Σεντζέν, Γουχάν, Ντονγκουάν, Τσονγκίνγκ
            
            "4. Industrial Engines": {
                "population": 0.45,     
                "density": 0.55,        
                "tourists": 0.15,       
                "gdp_per_capita": 0.30, 
                "traffic_index": 0.75,  
                "internet_speed": 0.65, 
                "innovation_score": 0.65 
            },

            # ΚΑΤΗΓΟΡΙΑ 5: KNOWLEDGE CAPITALS
            # Πόλεις: Στοκχόλμη, Βοστόνη, Άμστερνταμ, Σαν Φρανσίσκο, Κοπεγχάγη
            
            "5. Knowledge Capitals": {
                "population": 0.10,     
                "density": 0.15,        
                "tourists": 0.40,       
                "gdp_per_capita": 0.90, 
                "traffic_index": 0.35,  
                "internet_speed": 0.90, 
                "innovation_score": 1.00 
            },

            # ΚΑΤΗΓΟΡΙΑ 6: AMERICAN MIDDLEWEIGHTS
            # Πόλεις: Σακραμέντο, Ντένβερ, Ατλάντα, Όστιν, Σαρλότ
            
            "6. American Middleweights": {
                "population": 0.08,     
                "density": 0.05,        
                "tourists": 0.20,       
                "gdp_per_capita": 0.60, 
                "traffic_index": 0.55,  
                "internet_speed": 0.65, 
                "innovation_score": 0.60 
            },

            # ΚΑΤΗΓΟΡΙΑ 7: INTERNATIONAL MIDDLEWEIGHTS
            # Πόλεις: Τορόντο, Βερολίνο, Σίδνεϊ, Βανκούβερ, Βιέννη
            
            "7. International Middleweights": {
                "population": 0.15,     
                "density": 0.15,        
                "tourists": 0.45,       
                "gdp_per_capita": 0.65, 
                "traffic_index": 0.45,  
                "internet_speed": 0.75, 
                "innovation_score": 0.75 
            },

            # ΚΑΤΗΓΟΡΙΑ 8: TOURIST & CULTURAL
            # Πόλεις: Αθήνα, Βαρκελώνη, Ρώμη, Κιότο, Βενετία
        
            "8. Tourist & Cultural": {
                "population": 0.08,     
                "density": 0.35,        
                "tourists": 0.90,       
                "gdp_per_capita": 0.40, 
                "traffic_index": 0.65,  
                "internet_speed": 0.50, 
                "innovation_score": 0.45 
            }
        }

    def normalize(self, raw_data):
        """Μετατροπή σε κλίμακα 0-1 (Min-Max Scaling)"""
        vector = {}
        for key, val in raw_data.items():
            vector[key] = min(val / self.MAX_VALS[key], 1.0)
        return vector

    def classify(self, city_name, raw_data):
        print(f"\n{'='*60}")
        print(f"ANALYZING UNSEEN CITY: {city_name.upper()}")
        print(f"{'='*60}")
        
        city_vec = self.normalize(raw_data)
        
        scores = {}
        for category, target_vec in self.profiles.items():
            dist = 0
            common_keys = set(city_vec.keys()) & set(target_vec.keys())
            
            for key in common_keys:
                diff = city_vec[key] - target_vec[key]
                dist += diff ** 2
            
            scores[category] = 1 / (1 + math.sqrt(dist))
        
        sorted_scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=True)
        best_match = sorted_scores[0]
        runner_up = sorted_scores[1]
        
        print(f"-> CLASSIFICATION:   {best_match[0]}")
        print(f"   Confidence Score: {best_match[1]*100:.1f}%")
        print(f"-> Runner-up:        {runner_up[0]}")
        
        return best_match[0]

# ==============================================================================
# VALIDATION PHASE: ΕΛΕΓΧΟΣ ΜΕ ΠΟΛΕΙΣ ΕΚΤΟΣ ΛΙΣΤΑΣ
# ==============================================================================
if __name__ == "__main__":
    classifier = UrbanClassifier()
    
    # TEST 1: ΠΑΡΙΣΙ (Δεν είναι στη λίστα Global Giants, αλλά θα έπρεπε να βγει εκεί)
    
    paris_data = {
        "population": 11_000_000,   
        "density": 20_000,          
        "tourists": 28_000_000,    
        "gdp_per_capita": 75_000,   
        "traffic_index": 95,        
        "internet_speed": 230,      
        "innovation_score": 92      
    }
    classifier.classify("Paris (France)", paris_data)

    # TEST 2: ΜΟΝΑΧΟ (Δεν είναι στη λίστα International Middleweights)
    munich_data = {
        "population": 2_600_000,    
        "density": 4_800,           
        "tourists": 8_000_000,      
        "gdp_per_capita": 90_000,   
        "traffic_index": 50,        
        "internet_speed": 180,
        "innovation_score": 95      
    }
    classifier.classify("Munich (Germany)", munich_data)

    # TEST 3: ΒΟΜΒΑΗ (MUMBAI) (Δεν είναι στη λίστα Emerging Gateways)
    

    mumbai_data = {
        "population": 21_000_000,  
        "density": 32_000,          
        "tourists": 5_000_000,      
        "gdp_per_capita": 12_000,   
        "traffic_index": 115,       
        "internet_speed": 80,       
        "innovation_score": 45
    }
    classifier.classify("Mumbai (India)", mumbai_data)