import math
import random
import matplotlib.pyplot as plt
import copy

# ==========================================
# 1. ΡΥΘΜΙΣΕΙΣ (ΔΙΟΡΘΩΜΕΝΟ)
# ==========================================
NUM_CUSTOMERS = 15   #εργαζόμενοι που θα εξυπηρετηθουν     
CAPACITY = 5              # χωρητικοτητα βαν
DEPOT_COORDS = (50, 50)   #συντεταγμενες εργοστασιου
SEED_VALUE = 55           # Αλλάξαμε το seed για καλύτερη κατανομή στο χάρτη
POPULATION_SIZE = 80      
GENERATIONS = 300         
MUTATION_RATE = 0.25

# ΝΕΕΣ ΡΥΘΜΙΣΕΙΣ ΧΡΟΝΟΥ
MAX_RIDE_TIME = 45        # Όριο 45 λεπτά (όπως ζήτησες)
SPEED_FACTOR = 1.5        # Ταχύτητα: 1.5 μονάδες απόστασης ανά λεπτό (πιο γρήγορο λεωφορείο)

START_HOUR = 6   #ωρα εκκινησης
END_HOUR = 10    # τελευταια ωρα
MIN_TIME_MINUTES = START_HOUR * 60 #ωρα σε λεπτα 
MAX_TIME_MINUTES = END_HOUR * 60 #ωρα σε λεπτα 

class Customer:
    def __init__(self, id, x, y, demand=1):
        self.id = id
        self.x = x
        self.y = y
        self.demand = demand #η θεση που πιανει στο λεωφορειο
        # Παράθυρο παραλαβής 15 λεπτών
        window_start = random.randint(MIN_TIME_MINUTES, MAX_TIME_MINUTES - 60) #με γνωμονα οτι ολα τα βαν πρεπει να ειναι στη σταση μεχρι τις 10
        self.early = window_start #προσωρινες μεταβλητες
        self.late = window_start + 15 

def minutes_to_time(minutes):
    h = int(minutes // 60)
    m = int(minutes % 60)
    return f"{h:02d}:{m:02d}" #μετατροπη λεπτα σε ωρα 

def get_travel_time(c1, c2): #αποσταση για να παει απο τον πελατη c1 ston c2
    dist = math.sqrt((c1.x - c2.x)**2 + (c1.y - c2.y)**2)
    # Χρόνος = Απόσταση / Ταχύτητα
    return dist / SPEED_FACTOR #χρονος

def generate_fixed_data():
    random.seed(SEED_VALUE) 
    customers = []
    for i in range(NUM_CUSTOMERS):
        # Περιορίζουμε λίγο την ακτίνα (15-85) για να μην πέφτουν εξωφρενικά μακριά
        x = random.randint(15, 85)
        y = random.randint(15, 85)
        customers.append(Customer(i, x, y)) #δημιουργια αντικειμενων Customer
    return customers

# ==========================================
# 2. ΑΞΙΟΛΟΓΗΣΗ ΛΥΣΗΣ (LOGIC)
# ==========================================
def evaluate_solution(sequence, depot):
    total_dist = 0 #συνολικα χιλιομετρα που κανουν τα λεωφ
    vehicles = 0 #ποσα λεωφ θα χρησιμοποιηθούν
    routes = [] #λιστα επιβατων
    
    current_load = 0 #ειναι αδειο το βαν 
    current_loc = depot #ειναι στο εργοστασιο
    current_time = MIN_TIME_MINUTES #6 το πρωι
    current_route = [] # (Customer, Pickup_Time)
    route_customers = [] 

    for customer in sequence:
        travel_t = get_travel_time(current_loc, customer) #υπολογισμος χρονου απο την τωρινη τοποθεσια στον εργαζομενο 
        arrival_at_stop = current_time + travel_t #χρονος που εφτασε στον εργαζομενο
        
        # Πραγματική ώρα επιβίβασης (αν φτάσει νωρίς περιμένει)
        actual_pickup_time = max(arrival_at_stop, customer.early)
        
        # --- ΕΛΕΓΧΟΣ 45 ΛΕΠΤΟΥ ---
        # Υπολογίζουμε αν πάρουμε τον νέο εργαζόμενο και πάμε κατευθείαν στο εργοστάσιο,
        # πόση ώρα θα έχουν κάνει συνολικά ΟΛΟΙ οι επιβάτες μέσα στο όχημα.
        
        time_to_depot = get_travel_time(customer, depot) 
        arrival_at_factory = actual_pickup_time + time_to_depot #υπολογισμος απο εργατη που ειμαστε τωρα στο εργοστασιο τι ωρα θα φτασει
        
        ride_time_violation = False
        
        # Έλεγχος για τον τρέχοντα πελάτη για να μην  περασουν πανω απο 45 λεπτα για να φτασει στο εργοστασιο
        if (arrival_at_factory - actual_pickup_time) > MAX_RIDE_TIME: 
            ride_time_violation = True
            
        # Έλεγχος για τους ήδη επιβιβασμένους
        for (cust_obj, pickup_t) in current_route:
            if (arrival_at_factory - pickup_t) > MAX_RIDE_TIME:
                ride_time_violation = True
                break
        
        # Συνθήκες Αλλαγής Οχήματος:
        # 1. Γέμισε
        # 2. Άργησε στο ραντεβού (Late window)
        # 3. Παραβιάζεται το 45λεπτο για οποιονδήποτε επιβάτη
        if (current_load + customer.demand > CAPACITY or 
            arrival_at_stop > customer.late or 
            ride_time_violation):
            
            # Κλείσιμο προηγούμενης διαδρομής
            # Προσθέτουμε την απόσταση επιστροφής από τον *προηγούμενο* πελάτη
            total_dist += get_travel_time(current_loc, depot) * SPEED_FACTOR # Back to distance units
            routes.append(route_customers)
            
            # Reset για νέο όχημα
            current_route = []
            route_customers = []
            current_loc = depot
            current_load = 0
            current_time = MIN_TIME_MINUTES 
            vehicles += 1
            
            # Ξανα-υπολογισμός για το νέο όχημα
            travel_t = get_travel_time(current_loc, customer)
            arrival_at_stop = current_time + travel_t
            actual_pickup_time = max(arrival_at_stop, customer.early)
            
        # Προσθήκη
        wait_time = max(0, customer.early - arrival_at_stop)
        
        total_dist += (travel_t * SPEED_FACTOR) # Keep distance metric
        current_loc = customer
        current_route.append((customer, actual_pickup_time))
        route_customers.append(customer)
        current_load += customer.demand
        current_time = actual_pickup_time + 1.5 # 1.5 λεπτό επιβίβαση
        
    # Επιστροφή τελευταίου
    total_dist += get_travel_time(current_loc, depot) * SPEED_FACTOR
    routes.append(route_customers)
    vehicles += 1
    
    return total_dist, vehicles, routes

# ==========================================
# 3. ALGORITHMS 
# ==========================================
def local_search(solution, depot):
    best_sol = solution[:] #αντιγραφο του solution 
    best_cost, _, _ = evaluate_solution(best_sol, depot) #κραταμε μονο το πρωτο νουμερο, κοστος αποσταση
    # Swap adjacent 
    for i in range(len(solution) - 1): #συγκριση πελατων 
        new_sol = solution[:] #νεο προχειρο αντιγραφο
        new_sol[i], new_sol[i+1] = new_sol[i+1], new_sol[i] #αλλαγη θεσεων i me i+1
        cost, _, _ = evaluate_solution(new_sol, depot) 
        if cost < best_cost: #ελεγχος αν αυτη ειναι καλυτερη λυση 
            best_sol = new_sol[:]
            best_cost = cost
    return best_sol

def solve_hga(customers, depot):
    population = [] #λιστα αρχικου πληθυσμου 
    # Δημιουργία τυχαίου πληθυσμού
    for _ in range(POPULATION_SIZE): 
        c = customers[:] #αντιγραφο της λιστας με τους πελατες
        random.shuffle(c) #τυχαιο δρομολογιο
        population.append(c) #βαζουμε τυχαιο δρομολογιο στη λιστα 
    
    best_global_sol = None #καλυτερη λυση
    min_fitness = float('inf')#ελαχιστο κοστος 

    for gen in range(GENERATIONS):
        scored_pop = [] #λιστα με βαθμούς
        for sol in population: # βροχος για το πληθυσμο
            dist, veh, _ = evaluate_solution(sol, depot) 
            # Fitness: Μεγάλο βάρος στα οχήματα για να τα μειώσουμε
            fitness = (veh * 5000) + dist #fitness function 
            scored_pop.append((sol, fitness)) #αποθηκευση λυσης με το βαθμο στη λιστα 
            
            if fitness < min_fitness: 
                min_fitness = fitness
                best_global_sol = sol[:]

        # Επιλογή & Εξέλιξη
        scored_pop.sort(key=lambda x: x[1]) #ταξινομηση κοιτοντας τον βαθμο, λυσεις με μικροτερο κοστος πανε στη κορυφη
        top_solutions = [x[0] for x in scored_pop[:int(POPULATION_SIZE/2)]] #κραταμε το καλυτερο μισο του πληθυσμου 
        new_pop = top_solutions[:] #επομενη γενια 
        
        while len(new_pop) < POPULATION_SIZE:
            p1 = random.choice(top_solutions) #2 λυσεις γονεις 
            p2 = random.choice(top_solutions)
            # Crossover
            cut = random.randint(0, len(p1)-1)
            child = p1[:cut] + [x for x in p2 if x not in p1[:cut]]
            # Mutation
            if random.random() < MUTATION_RATE:
                i1, i2 = random.sample(range(len(child)), 2)
                child[i1], child[i2] = child[i2], child[i1]
            
            # Hybrid Step (κάθε 20 γενιές για ταχύτητα)
            if gen % 20 == 0:
                child = local_search(child, depot)
            new_pop.append(child)
        population = new_pop

    return local_search(best_global_sol, depot)

def solve_greedy(customers, depot):
    unvisited = customers[:]
    current_loc = depot
    solution_sequence = []
    
    # Sort by time window start (προσπάθεια να είναι λίγο λογικός ο Greedy)
    # Αλλιώς ο Greedy απλά θα πηγαίνει στον κοντινότερο
    while unvisited:
        # Επιλέγει τον κοντινότερο γεωγραφικά
        unvisited.sort(key=lambda c: get_travel_time(current_loc, c))
        next_customer = unvisited.pop(0)
        solution_sequence.append(next_customer)
        current_loc = next_customer
    return solution_sequence

# ==========================================
# 4. PLOTTING
# ==========================================
def plot_comparison(hga_seq, greedy_seq, depot):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(24, 12))
    
    def draw_routes_on_ax(ax, sequence, title):
        dist, veh, routes = evaluate_solution(sequence, depot)
        
        ax.set_title(f"{title}\nΟχήματα: {veh} | Συνολική Απόσταση: {dist:.1f}", fontsize=16, fontweight='bold')
        ax.scatter(depot.x, depot.y, c='red', s=500, marker='s', edgecolors='black', label='Factory', zorder=10)
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f']
        
        for r_idx, route in enumerate(routes):
            color = colors[r_idx % len(colors)]
            
            # Recalculate times for plotting
            current_loc = depot
            current_time = MIN_TIME_MINUTES
            
            xs = [depot.x]
            ys = [depot.y]
            
            route_data = [] 
            
            for customer in route:
                travel_t = get_travel_time(current_loc, customer)
                arrival = current_time + travel_t
                pickup = max(arrival, customer.early)
                
                route_data.append((customer, pickup))
                xs.append(customer.x)
                ys.append(customer.y)
                
                current_loc = customer
                current_time = pickup + 1.5
            
            # Back to depot
            time_back = get_travel_time(current_loc, depot)
            arrival_factory = current_time + time_back
            xs.append(depot.x)
            ys.append(depot.y)
            
            # Plot Line
            ax.plot(xs, ys, c=color, linewidth=2.5, linestyle='-', alpha=0.7, label=f'Bus {r_idx+1}')
            
            # Plot Points & Info
            for idx, (customer, pickup_t) in enumerate(route_data):
                ax.scatter(customer.x, customer.y, c='black', s=120, zorder=5, edgecolors='white')
                
                ride_time = arrival_factory - pickup_t
                pickup_str = minutes_to_time(pickup_t)
                
                # Check constraints for coloring
                box_color = 'white'
                edge_color = 'gray'
                text_weight = 'normal'
                
                # Αν ξεπερνά το 45λεπτο -> ΚΟΚΚΙΝΟ
                if ride_time > MAX_RIDE_TIME + 1: # +1 tolerance
                    box_color = '#ffcccc' 
                    edge_color = 'red'
                    text_weight = 'bold'
                
                info_text = f"#{idx+1}\n{pickup_str}\n{int(ride_time)}m"
                
                ax.text(customer.x, customer.y + 4, info_text, 
                        fontsize=9, ha='center', fontweight=text_weight,
                        bbox=dict(facecolor=box_color, alpha=0.9, edgecolor=edge_color, boxstyle='round,pad=0.3'))

        ax.grid(True, linestyle='--', alpha=0.4)
        ax.legend(loc='upper right')
        ax.set_xlabel('X Distance')
        ax.set_ylabel('Y Distance')

    draw_routes_on_ax(ax1, hga_seq, "HGA")
    draw_routes_on_ax(ax2, greedy_seq, "Greedy")
    
    plt.tight_layout()
    plt.savefig('vrp_final_45min.png', dpi=300)
    plt.show()

if __name__ == "__main__":
    depot = Customer(-1, DEPOT_COORDS[0], DEPOT_COORDS[1])
    data = generate_fixed_data()
    print(f"Εκτέλεση Προσομοίωσης (Όριο: {MAX_RIDE_TIME} λεπτά)...")
    hga_sol = solve_hga(data, depot)
    greedy_sol = solve_greedy(data, depot)
    plot_comparison(hga_sol, greedy_sol, depot)