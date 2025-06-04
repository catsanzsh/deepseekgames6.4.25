import tkinter as tk
import winsound
from PIL import Image, ImageTk
import math
import random

class BreakoutGame:
    def __init__(self, root):
        self.root = root
        self.root.title("BREAKOUT 4K")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#121212")
        
        # Create container frame
        self.container = tk.Frame(root)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Create frames for different screens
        self.menu_frame = tk.Frame(self.container, bg="#121212")
        self.game_frame = tk.Frame(self.container, bg="black")
        self.game_over_frame = tk.Frame(self.container, bg="#121212")
        self.win_frame = tk.Frame(self.container, bg="#121212")
        
        for frame in (self.menu_frame, self.game_frame, self.game_over_frame, self.win_frame):
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Create the main menu
        self.create_menu()
        
        # Show menu initially
        self.show_menu()
    
    def create_menu(self):
        # Title with gradient effect
        title_frame = tk.Frame(self.menu_frame, bg="#121212")
        title_frame.pack(pady=40)
        
        title_label = tk.Label(
            title_frame, 
            text="BREAKOUT 4K", 
            font=("Impact", 48, "bold"),
            fg="#FF5722",
            bg="#121212"
        )
        title_label.pack()
        
        # Create gradient effect for subtitle
        subtitle_label = tk.Label(
            title_frame, 
            text="ULTIMATE EDITION", 
            font=("Arial", 16),
            fg="#E91E63",
            bg="#121212"
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Buttons with hover effects
        button_frame = tk.Frame(self.menu_frame, bg="#121212")
        button_frame.pack(pady=20)
        
        buttons = [
            ("START GAME", self.start_game, "#4CAF50", "#388E3C"),
            ("CONTROLS", self.show_controls, "#2196F3", "#1976D2"),
            ("EXIT", self.exit_game, "#F44336", "#D32F2F")
        ]
        
        for text, command, color, hover_color in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Arial", 14, "bold"),
                bg=color,
                fg="white",
                activebackground=hover_color,
                activeforeground="white",
                relief="flat",
                width=15,
                height=2,
                cursor="hand2",
                command=command
            )
            btn.pack(pady=10, padx=20)
            btn.bind("<Enter>", lambda e, b=btn, c=hover_color: b.config(bg=c))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
        
        # Footer
        footer = tk.Label(
            self.menu_frame,
            text="© 2023 BREAKOUT 4K - ALL RIGHTS RESERVED",
            font=("Arial", 8),
            fg="#777",
            bg="#121212"
        )
        footer.pack(side=tk.BOTTOM, pady=10)
    
    def show_controls(self):
        # Create a popup for controls
        controls_window = tk.Toplevel(self.root)
        controls_window.title("Game Controls")
        controls_window.geometry("400x300")
        controls_window.resizable(False, False)
        controls_window.configure(bg="#2c3e50")
        controls_window.grab_set()
        
        # Title
        tk.Label(
            controls_window,
            text="GAME CONTROLS",
            font=("Arial", 20, "bold"),
            fg="#ecf0f1",
            bg="#2c3e50"
        ).pack(pady=20)
        
        # Controls content
        content = tk.Frame(controls_window, bg="#2c3e50")
        content.pack(pady=10)
        
        controls = [
            ("Mouse Movement", "Move paddle left and right"),
            ("Ball Physics", "Ball bounces at different angles based on where it hits the paddle"),
            ("Bricks", "Break all bricks to win the game"),
            ("Game Over", "If the ball falls below the paddle, game ends")
        ]
        
        for i, (title, desc) in enumerate(controls):
            tk.Label(
                content,
                text=title,
                font=("Arial", 12, "bold"),
                fg="#3498db",
                bg="#2c3e50",
                anchor="w"
            ).grid(row=i, column=0, sticky="w", padx=20, pady=5)
            
            tk.Label(
                content,
                text=desc,
                font=("Arial", 10),
                fg="#ecf0f1",
                bg="#2c3e50",
                anchor="w"
            ).grid(row=i, column=1, sticky="w", padx=20, pady=5)
        
        # Close button
        tk.Button(
            controls_window,
            text="CLOSE",
            font=("Arial", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            command=controls_window.destroy
        ).pack(pady=20)
    
    def start_game(self):
        self.show_game()
        
        # Initialize game elements
        self.canvas = tk.Canvas(self.game_frame, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Paddle
        self.paddle_width = 100
        self.paddle = self.canvas.create_rectangle(
            250, 380, 250 + self.paddle_width, 390, 
            fill="#3498db", outline="#2980b9", width=2
        )
        
        # Ball
        self.ball = self.canvas.create_oval(
            290, 340, 310, 360, 
            fill="#e74c3c", outline="#c0392b", width=2
        )
        
        # Set initial ball speed
        self.ball_speed = 4
        angle = random.uniform(math.pi/4, 3*math.pi/4)  # Random angle between 45-135 degrees
        self.ball_dx = self.ball_speed * math.cos(angle)
        self.ball_dy = -self.ball_speed * math.sin(angle)
        
        # Bricks
        self.bricks = []
        colors = ["#e74c3c", "#f39c12", "#2ecc71", "#9b59b6", "#3498db"]
        for i in range(5):
            for j in range(7):
                brick = self.canvas.create_rectangle(
                    j*85, i*30+50,
                    j*85+80, i*30+70,
                    fill=colors[i], outline="#2c3e50", width=1
                )
                self.bricks.append(brick)
        
        # Score
        self.score = 0
        self.score_text = self.canvas.create_text(
            50, 20, 
            text=f"SCORE: {self.score}", 
            fill="white", 
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        
        # Level
        self.level = 1
        self.level_text = self.canvas.create_text(
            550, 20, 
            text=f"LEVEL: {self.level}", 
            fill="white", 
            font=("Arial", 12, "bold"),
            anchor="e"
        )
        
        # Mouse controls
        self.root.bind("<Motion>", self.on_mouse_move)
        
        self.game_active = True
        self.game_loop()
    
    def on_mouse_move(self, event):
        """Handle mouse movement"""
        if not self.game_active:
            return
            
        paddle_width = self.paddle_width
        x = event.x - paddle_width/2
        x = max(0, min(x, 600 - paddle_width))
        self.canvas.coords(self.paddle, x, 380, x + paddle_width, 390)
    
    def game_loop(self):
        if not self.game_active:
            return
            
        self.canvas.move(self.ball, self.ball_dx, self.ball_dy)
        pos = self.canvas.coords(self.ball)
        
        # Wall collisions
        if pos[0] <= 0 or pos[2] >= 600:
            self.ball_dx *= -1
            winsound.Beep(400, 20)
        if pos[1] <= 0:
            self.ball_dy *= -1
            winsound.Beep(400, 20)
        
        # Paddle collision
        paddle_pos = self.canvas.coords(self.paddle)
        if (pos[2] >= paddle_pos[0] and pos[0] <= paddle_pos[2] and 
            pos[3] >= paddle_pos[1] and pos[3] <= paddle_pos[3]):
            # Calculate hit position for directional bounce
            relative_x = (pos[0] + pos[2])/2 - (paddle_pos[0] + paddle_pos[2])/2
            normalized_x = relative_x / (self.paddle_width / 2)
            angle = normalized_x * (math.pi/3)  # Max 60 degrees from vertical
            
            # Update ball direction
            speed = math.sqrt(self.ball_dx**2 + self.ball_dy**2)
            self.ball_dx = speed * math.sin(angle)
            self.ball_dy = -speed * math.cos(angle)
            
            winsound.Beep(660, 25)
        
        # Brick collisions
        for brick in self.bricks[:]:
            brick_pos = self.canvas.coords(brick)
            if (pos[2] >= brick_pos[0] and pos[0] <= brick_pos[2] and 
                pos[3] >= brick_pos[1] and pos[1] <= brick_pos[3]):
                self.bricks.remove(brick)
                self.canvas.delete(brick)
                self.ball_dy *= -1
                
                # Update score
                self.score += 10
                self.canvas.itemconfig(self.score_text, text=f"SCORE: {self.score}")
                
                winsound.Beep(330, 25)
                break
        
        # Game over conditions
        if pos[3] >= 400:
            self.game_active = False
            winsound.Beep(55, 1000)
            self.show_game_over()
            return
            
        # Win condition
        if not self.bricks:
            self.game_active = False
            winsound.Beep(880, 500)
            self.show_win_screen()
            return

        # Maintain 60 FPS
        self.root.after(16, self.game_loop)
    
    def create_game_over(self):
        # Game over screen
        tk.Label(
            self.game_over_frame,
            text="GAME OVER",
            font=("Impact", 48, "bold"),
            fg="#e74c3c",
            bg="#121212"
        ).pack(pady=50)
        
        tk.Label(
            self.game_over_frame,
            text=f"FINAL SCORE: {self.score}",
            font=("Arial", 24),
            fg="#ecf0f1",
            bg="#121212"
        ).pack(pady=20)
        
        button_frame = tk.Frame(self.game_over_frame, bg="#121212")
        button_frame.pack(pady=40)
        
        tk.Button(
            button_frame,
            text="PLAY AGAIN",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            height=2,
            command=self.start_game
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Button(
            button_frame,
            text="MAIN MENU",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white",
            width=15,
            height=2,
            command=self.show_menu
        ).pack(side=tk.LEFT, padx=20)
    
    def create_win_screen(self):
        # Win screen
        tk.Label(
            self.win_frame,
            text="YOU WIN!",
            font=("Impact", 48, "bold"),
            fg="#2ecc71",
            bg="#121212"
        ).pack(pady=50)
        
        tk.Label(
            self.win_frame,
            text=f"FINAL SCORE: {self.score}",
            font=("Arial", 24),
            fg="#ecf0f1",
            bg="#121212"
        ).pack(pady=20)
        
        tk.Label(
            self.win_frame,
            text=f"LEVEL {self.level} COMPLETED",
            font=("Arial", 18),
            fg="#3498db",
            bg="#121212"
        ).pack(pady=10)
        
        button_frame = tk.Frame(self.win_frame, bg="#121212")
        button_frame.pack(pady=40)
        
        tk.Button(
            button_frame,
            text="NEXT LEVEL",
            font=("Arial", 14, "bold"),
            bg="#9b59b6",
            fg="white",
            width=15,
            height=2,
            command=self.next_level
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Button(
            button_frame,
            text="MAIN MENU",
            font=("Arial", 14, "bold"),
            bg="#2196F3",
            fg="white",
            width=15,
            height=2,
            command=self.show_menu
        ).pack(side=tk.LEFT, padx=20)
    
    def next_level(self):
        self.level += 1
        self.ball_speed += 0.5  # Increase difficulty
        self.start_game()
    
    def show_frame(self, frame):
        frame.tkraise()
    
    def show_menu(self):
        self.show_frame(self.menu_frame)
    
    def show_game(self):
        # Clear previous game if exists
        for widget in self.game_frame.winfo_children():
            widget.destroy()
        self.show_frame(self.game_frame)
    
    def show_game_over(self):
        self.create_game_over()
        self.show_frame(self.game_over_frame)
    
    def show_win_screen(self):
        self.create_win_screen()
        self.show_frame(self.win_frame)
    
    def exit_game(self):
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    game = BreakoutGame(root)
    root.mainloop()
