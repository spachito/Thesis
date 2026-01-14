import pygame
import random
import sys

# --- Ρυθμίσεις Προσομοίωσης ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
ROAD_WIDTH = 100
WHITE = (255, 255, 255)
BLACK = (50, 50, 50)
GRAY = (100, 100, 100)
DARK_GRAY = (30, 30, 30)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
YELLOW = (255, 215, 0)
BLUE = (100, 150, 255)
CYAN = (0, 255, 255)

# --- Ρυθμίσεις Χρόνου & Κυκλοφορίας ---
FPS = 60
PHASE_DURATION_SEC = 300
PHASE_FRAMES = PHASE_DURATION_SEC * FPS

# Παράμετροι (Ρυθμισμένες για να φαίνονται οι ουρές)
CAR_SPEED = 2
ARRIVAL_RATE = 0.01     
STATIC_CYCLE = 1800      
MIN_GREEN_TIME = 600    

# Αρχικοποίηση Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) #δημιουργια του παραθυρου
pygame.display.set_caption("Thesis Simulation: Automated Benchmark") #ορισμος τιτλου του παραθυρου
clock = pygame.time.Clock() #δημιουργια clock

# Fonts
font_small = pygame.font.SysFont("Consolas", 18) #δημιουργία γραμματοσειρών
font_large = pygame.font.SysFont("Arial", 32, bold=True)
font_huge = pygame.font.SysFont("Arial", 50, bold=True)

class Car:
    def __init__(self, direction, lane_pos):
        self.direction = direction
        self.width = 20
        self.height = 40
        self.color = BLUE
        self.speed = CAR_SPEED
        self.waiting = False #μεταβλητη που γινεται true οταν το αμαξι περιμενει
        
        if direction == 'vertical':
            self.rect = pygame.Rect(lane_pos, -50, self.width, self.height)
        else:
            self.rect = pygame.Rect(-50, lane_pos, self.height, self.width)

    def move(self, stop_line, is_green, car_ahead):
        should_move = True
        
        # 1. Έλεγχος Φαναριού
        if not is_green:
            if self.direction == 'vertical':
                if self.rect.bottom < stop_line and self.rect.bottom + self.speed >= stop_line:
                    should_move = False
            else:
                if self.rect.right < stop_line and self.rect.right + self.speed >= stop_line:
                    should_move = False

        # 2. Έλεγχος Προπορευόμενου (Collision Avoidance)
        if car_ahead:
            distance = 0
            if self.direction == 'vertical':
                distance = car_ahead.rect.top - self.rect.bottom
            else:
                distance = car_ahead.rect.left - self.rect.right
            
            # Αν είναι πολύ κοντά, σταμάτα
            if distance < 15:
                should_move = False

        if should_move:
            self.waiting = False
            if self.direction == 'vertical':
                self.rect.y += self.speed
            else:
                self.rect.x += self.speed
        else:
            self.waiting = True

    def is_off_screen(self):
        return self.rect.top > SCREEN_HEIGHT or self.rect.left > SCREEN_WIDTH

def draw_road():
    screen.fill(GRAY)
    pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - ROAD_WIDTH//2, 0, ROAD_WIDTH, SCREEN_HEIGHT))
    pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT//2 - ROAD_WIDTH//2, SCREEN_WIDTH, ROAD_WIDTH))
    pygame.draw.line(screen, WHITE, (SCREEN_WIDTH//2, 0), (SCREEN_WIDTH//2, SCREEN_HEIGHT), 2)
    pygame.draw.line(screen, WHITE, (0, SCREEN_HEIGHT//2), (SCREEN_WIDTH, SCREEN_HEIGHT//2), 2)

def draw_info_panel(phase, time_left, avg_wait):
    panel_rect = pygame.Rect(10, 10, 300, 150)
    pygame.draw.rect(screen, DARK_GRAY, panel_rect)
    pygame.draw.rect(screen, WHITE, panel_rect, 2)
    
    color = RED if phase == "STATIC" else GREEN
    
    screen.blit(font_large.render(f"PHASE: {phase}", True, color), (20, 20))
    screen.blit(font_small.render(f"Time Remaining: {time_left}s", True, WHITE), (20, 70))
    screen.blit(font_small.render(f"Current Avg Wait: {avg_wait:.2f}s", True, CYAN), (20, 100))

def draw_final_results(static_res, smart_res):
    screen.fill(DARK_GRAY)
    
    title = font_huge.render("SIMULATION COMPLETED", True, WHITE)
    screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
    
    # Static Column
    pygame.draw.rect(screen, (60, 0, 0), (100, 150, 350, 400))
    pygame.draw.rect(screen, RED, (100, 150, 350, 400), 3)
    
    s_title = font_large.render("STATIC CONTROL", True, RED)
    s_wait = font_small.render(f"Total Wait Time: {static_res['total_time']:.1f}s", True, WHITE)
    s_avg = font_huge.render(f"{static_res['avg']:.2f} sec", True, WHITE)
    s_sub = font_small.render("Average Delay per Car", True, GRAY)
    
    screen.blit(s_title, (140, 180))
    screen.blit(s_wait, (140, 250))
    screen.blit(s_avg, (140, 300))
    screen.blit(s_sub, (140, 350))

    # Smart Column
    pygame.draw.rect(screen, (0, 60, 0), (550, 150, 350, 400))
    pygame.draw.rect(screen, GREEN, (550, 150, 350, 400), 3)
    
    m_title = font_large.render("SMART CONTROL", True, GREEN)
    m_wait = font_small.render(f"Total Wait Time: {smart_res['total_time']:.1f}s", True, WHITE)
    m_avg = font_huge.render(f"{smart_res['avg']:.2f} sec", True, WHITE)
    m_sub = font_small.render("Average Delay per Car", True, GRAY)
    
    screen.blit(m_title, (590, 180))
    screen.blit(m_wait, (590, 250))
    screen.blit(m_avg, (590, 300))
    screen.blit(m_sub, (590, 350))
    
    # Improvement Calculation
    if static_res['avg'] > 0:
        imp = ((static_res['avg'] - smart_res['avg']) / static_res['avg']) * 100
        imp_text = font_huge.render(f"IMPROVEMENT: {imp:.1f}%", True, CYAN)
        screen.blit(imp_text, (SCREEN_WIDTH//2 - imp_text.get_width()//2, 600))

    hint = font_small.render("Press ESC to Exit", True, WHITE)
    screen.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, 750))
    
    pygame.display.flip()

def main():
    cars_vertical = []
    cars_horizontal = []
    
    # Simulation State
    phase = "STATIC"
    vertical_green = True # πρασινο το φαναρι στο καθετο δρομο
    light_timer = 0 # χρονομετρο φαναριου
    
    # Stats State
    total_wait_frames = 0 # χρνος αναμονης αυτοκινητων 
    total_cars = 0 # συνολο αμαξιων 
    phase_frame_counter = 0 # γενικο χρονομετρο οταν φτασει 5400 frames σταματαει
    
    static_results = {'avg': 0, 'total_time': 0}
    smart_results = {'avg': 0, 'total_time': 0}

    v_stop = SCREEN_HEIGHT//2 - ROAD_WIDTH//2 - 10 #γραφικα για το που σταματανε τα αμαξια
    h_stop = SCREEN_WIDTH//2 - ROAD_WIDTH//2 - 10 

    running = True
    while running:
        if phase == "FINISHED":
            draw_final_results(static_results, smart_results)
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
            continue

        screen.fill(GRAY)
        draw_road()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Check Phase Timer
        phase_frame_counter += 1 #ποσα καρε εχουν περασει 
        time_left = max(0, int((PHASE_FRAMES - phase_frame_counter) / FPS)) #τα καρε se sec
        
        if phase_frame_counter >= PHASE_FRAMES:
            avg = (total_wait_frames / 60) / total_cars if total_cars > 0 else 0
            total_sec = total_wait_frames / 60
            
            if phase == "STATIC":
                static_results = {'avg': avg, 'total_time': total_sec}
                phase = "SMART"
                cars_vertical.clear()
                cars_horizontal.clear()
                total_wait_frames = 0
                total_cars = 0
                phase_frame_counter = 0
                light_timer = 0
                vertical_green = True
            elif phase == "SMART":
                smart_results = {'avg': avg, 'total_time': total_sec}
                phase = "FINISHED"

        # Spawning
        if random.random() < ARRIVAL_RATE:
            cars_vertical.append(Car('vertical', SCREEN_WIDTH//2 - 20))
            total_cars += 1
        if random.random() < ARRIVAL_RATE:
             cars_horizontal.append(Car('horizontal', SCREEN_HEIGHT//2 - 20))
             total_cars += 1

        # Calculate Logic & Stats
        queue_v = sum(1 for c in cars_vertical if c.waiting)
        queue_h = sum(1 for c in cars_horizontal if c.waiting)
        total_wait_frames += (queue_v + queue_h)
       
       # --- 2. Λογική Ελέγχου Φαναριών (Decision) ---
        # ΕΔΩ ΜΠΑΙΝΕΙ Ο ΝΕΟΣ ΚΩΔΙΚΑΣ
        switch_needed = False
        
        # --- ΛΟΓΙΚΗ STATIC ---
        if phase == "STATIC":
            if light_timer > STATIC_CYCLE:
                switch_needed = True

        # --- ΛΟΓΙΚΗ SMART ---
        elif phase == "SMART":
            # ΚΡΙΤΗΡΙΟ 1: Ασφάλεια (Min Green)
            if light_timer > MIN_GREEN_TIME:
                
                # ΚΡΙΤΗΡΙΟ 2: Εντοπισμός Κενού (Gap Logic)
                # Αν άδειασε το πράσινο αλλά έχει ουρά το κόκκινο -> Αλλαγή
                if vertical_green and queue_v == 0 and queue_h > 0:
                    switch_needed = True
                elif not vertical_green and queue_h == 0 and queue_v > 0:
                    switch_needed = True

                # ΚΡΙΤΗΡΙΟ 3: Εξισορρόπηση (Queue Balancing)
                # Αν η ουρά στο κόκκινο είναι πολύ μεγαλύτερη -> Αλλαγή
                if vertical_green and queue_h > queue_v + 3:
                    switch_needed = True
                elif not vertical_green and queue_v > queue_h + 3:
                    switch_needed = True

        # Εκτέλεση Αλλαγής
        if switch_needed:
            vertical_green = not vertical_green
            light_timer = 0
        else:
            light_timer += 1

        # Move Cars 
        for i, car in enumerate(cars_vertical):
            car_ahead = cars_vertical[i-1] if i > 0 else None
            car.move(v_stop, vertical_green, car_ahead)
            pygame.draw.rect(screen, car.color, car.rect)
            
        for i, car in enumerate(cars_horizontal):
            car_ahead = cars_horizontal[i-1] if i > 0 else None
            car.move(h_stop, not vertical_green, car_ahead)
            pygame.draw.rect(screen, YELLOW, car.rect)
            
        # Clean up off-screen cars
        cars_vertical = [c for c in cars_vertical if not c.is_off_screen()]
        cars_horizontal = [c for c in cars_horizontal if not c.is_off_screen()]
        
        # Lights
        pygame.draw.circle(screen, GREEN if vertical_green else RED, (SCREEN_WIDTH//2 + 60, SCREEN_HEIGHT//2 - 60), 15)
        pygame.draw.circle(screen, RED if vertical_green else GREEN, (SCREEN_WIDTH//2 - 60, SCREEN_HEIGHT//2 + 60), 15)

        # UI
        current_avg = (total_wait_frames / 60) / total_cars if total_cars > 0 else 0
        draw_info_panel(phase, time_left, current_avg)
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()