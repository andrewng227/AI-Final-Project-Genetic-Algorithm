import string
import random
import time
import tkinter as tk
from tkinter import messagebox
import threading

POPULATION_SIZE = 200
MUTATION_RATE = 0.05
MAX_GENERATIONS = 10000
CHARSET = string.ascii_letters + string.digits + string.punctuation + " "

def check_common_password(password):
    with open('passwords.txt', 'r') as f:
        common = f.read().splitlines()
    if password in common:
        return True
    return False

# ĐÁNH GIÁ ĐỘ KHÓ CỦA PASSWORD
def password_strength(password):
    score = 0
    length = len(password)
    upper_case = any(c.isupper() for c in password)
    lower_case = any(c.islower() for c in password)
    special = any(c in string.punctuation for c in password)
    digits = any(c.isdigit() for c in password)
    characters = [upper_case, lower_case, special, digits]
    if length > 8:
        score += 1
    if length > 15:
        score += 1
    if length > 20:
        score += 1
    if length > 30:
        score += 1
    score += sum(characters) - 1
    if score < 4:
        return "Dễ", score
    elif score == 4:
        return "Trung Bình", score
    elif 4 < score < 6:
        return "Mạnh", score
    else:
        return "Rất Mạnh", score

def feedback(password):
    strength, score = password_strength(password)
    feedback_text = f"Password strength: {strength}\n"
    if score < 4:
        feedback_text += "Suggestions to improve your password:\n"
        if len(password) <= 8:
            feedback_text += "- Make your password longer (more than 8 characters).\n"
        if not any(c.isupper() for c in password):
            feedback_text += "- Include uppercase letters.\n"
        if not any(c.islower() for c in password):
            feedback_text += "- Include lowercase letters.\n"
        if not any(c in string.punctuation for c in password):
            feedback_text += "- Add special characters (e.g., @,#,$).\n"
        if not any(c.isdigit() for c in password):
            feedback_text += "- Add numbers.\n"
    return feedback_text


def random_gene():
    return random.choice(CHARSET)

def create_individual(length):
    ket_qua = ""
    for i in range(length):
        ket_qua = ket_qua + random_gene()
    return ket_qua

def fitness(individual, target):
    score = 0
    for i in range(len(target)):
        if individual[i] == target[i]:
            score = score + 1
    return score

def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)
    child = parent1[0:point] + parent2[point:len(parent2)]
    return child

def mutate(individual):
    new_individual = ""
    for i in range(len(individual)):
        if random.random() < MUTATION_RATE:
            new_individual = new_individual + random_gene()
        else:
            new_individual = new_individual + individual[i]
    return new_individual

def selection(population, target):
    bang_diem = []
    for p in population:
        diem = fitness(p, target)
        bang_diem.append([diem, p])
    bang_diem.sort(reverse=True)
    so_luong_giu_lai = POPULATION_SIZE // 2
    population_moi = []
    for i in range(so_luong_giu_lai):
        population_moi.append(bang_diem[i][1]) 
        
    return population_moi

#GIAO DIỆN GUI

class GeneticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Thuật Toán Đoán Mật Khẩu - Genetic Algorithm")
        self.root.geometry("640x520") 
        self.root.resizable(False, False)
        
        BG_COLOR = "#F0F4F8" 
        self.root.configure(bg=BG_COLOR)

        # 1. TIÊU ĐỀ CHÍNH
        tk.Label(
            root,
            text="PASSWORD GUESSING - GENETIC ALGORITHM",
            font=("Segoe UI", 18, "bold"),
            fg="#003366",
            bg=BG_COLOR
        ).pack(pady=(25, 5))  

        tk.Label(
            root,
            text="Nhập Password cần tìm từ 8 đến 40 ký tự",
            font=("Segoe UI", 10, "italic"),
            fg="#666666",
            bg=BG_COLOR
        ).pack(pady=(0, 20)) 

        # 2. KHUNG NHẬP LIỆU
        frame_nhap = tk.Frame(root, bg=BG_COLOR)
        frame_nhap.pack(pady=(0, 15))

        tk.Label(
            frame_nhap,
            text="Password cần tìm:",
            font=("Segoe UI", 12, "bold"),
            fg="#333333",
            bg=BG_COLOR
        ).grid(row=0, column=0, padx=(0, 15))

        self.entry = tk.Entry(
            frame_nhap,
            width=28,
            font=("Consolas", 14),
            relief="flat",
            highlightthickness=1,
            highlightbackground="#CCCCCC",
            highlightcolor="#2196F3",
            bd=5 
        )
        self.entry.grid(row=0, column=1)

        # 3. NÚT BẤM
        self.btn = tk.Button(
            root,
            text="TÌM KIẾM",
            command=self.start_attack, 
            font=("Segoe UI", 11, "bold"),
            bg="#0078D7",   
            fg="white",
            activebackground="#005A9E",
            activeforeground="white",
            width=20,
            pady=4,
            relief="flat",
            cursor="hand2"
        )
        self.btn.pack(pady=(5, 20))

        # 4. KHUNG KẾT QUẢ
        frame = tk.LabelFrame(
            root,
            text=" THÔNG TIN KẾT QUẢ ",
            font=("Segoe UI", 12, "bold"),
            padx=40,
            pady=15,
            bg="white",
            fg="#003366",
            relief="ridge",
            bd=2
        )
        frame.columnconfigure(1, weight=1)
        frame.pack(padx=35, fill="x")

        font_label = ("Segoe UI", 11)
        font_value = ("Consolas", 12, "bold")   

        pad_y = 5

        tk.Label(frame, text="Mật khẩu mục tiêu:", font=font_label, fg="#555555", bg="white").grid(row=0, column=0, sticky="w", pady=pad_y)
        self.lbl_target = tk.Label(frame, font=font_value, bg="white", fg="#333333")
        self.lbl_target.grid(row=0, column=1, sticky="w", padx=10)

        tk.Label(frame, text="Đã tìm thấy:", font=font_label, fg="#555555", bg="white").grid(row=1, column=0, sticky="w", pady=pad_y)
        self.lbl_best = tk.Label(frame, font=font_value, bg="white", fg="#28A745") # Xanh lá cây nổi bật
        self.lbl_best.grid(row=1, column=1, sticky="w", padx=10)

        tk.Label(frame, text="Số lần dò:", font=font_label, fg="#555555", bg="white").grid(row=2, column=0, sticky="w", pady=pad_y)
        self.lbl_gen = tk.Label(frame, font=font_value, bg="white", fg="#0052CC")
        self.lbl_gen.grid(row=2, column=1, sticky="w", padx=10)

        tk.Label(frame, text="Độ khớp:", font=font_label, fg="#555555", bg="white").grid(row=3, column=0, sticky="w", pady=pad_y)
        self.lbl_fitness = tk.Label(frame, font=font_value, bg="white", fg="#0052CC")
        self.lbl_fitness.grid(row=3, column=1, sticky="w", padx=10)

        tk.Label(frame, text="Thời gian dò:", font=font_label, fg="#555555", bg="white").grid(row=4, column=0, sticky="w", pady=pad_y)
        self.lbl_time = tk.Label(frame, font=font_value, bg="white", fg="#DC3545") # Màu đỏ cho thời gian
        self.lbl_time.grid(row=4, column=1, sticky="w", padx=10)

        tk.Label(frame, text="Độ mạnh:", font=font_label, fg="#555555", bg="white").grid(row=5, column=0, sticky="w", pady=pad_y)
        self.lbl_strength = tk.Label(frame, font=("Segoe UI", 11, "bold"), bg="white", fg="#FD7E14") # Màu cam
        self.lbl_strength.grid(row=5, column=1, sticky="w", padx=10)

        tk.Label(frame, text="Kết quả:", font=font_label, fg="#555555", bg="white").grid(row=6, column=0, sticky="w", pady=pad_y)
        self.lbl_dataset = tk.Label(frame, font=("Segoe UI", 11, "italic", "bold"), bg="white", fg="#6F42C1") # Màu tím
        self.lbl_dataset.grid(row=6, column=1, sticky="w", padx=10)
        
    def start_attack(self):
        target = self.entry.get()
        if len(target) < 8 or len(target) > 40:
            messagebox.showerror("Lỗi", "Mật khẩu phải từ 8 đến 40 ký tự!")
            return
        
        self.lbl_target.config(text=target)
        self.lbl_best.config(text="Đang dò...", fg="#FD7E14")
        self.lbl_gen.config(text="...")
        self.lbl_fitness.config(text="...")
        self.lbl_time.config(text="...")
        self.lbl_strength.config(text="...", fg="#FD7E14")
        self.lbl_dataset.config(text="...")
        
        self.btn.config(state=tk.DISABLED, bg="#999999", text="ĐANG XỬ LÝ...")

        threading.Thread(target=self.run_genetic, args=(target,), daemon=True).start()

    def run_genetic(self, target):
        in_dataset = check_common_password(target)
        population = [create_individual(len(target)) for _ in range(POPULATION_SIZE)]
        start_time = time.perf_counter()
        
        generation = 0
        best = ""
        best_score = 0

        for gen in range(1, MAX_GENERATIONS + 1):
            generation = gen
            population.sort(key=lambda x: fitness(x, target), reverse=True)
            best = population[0]
            best_score = fitness(best, target)
            
            if best == target:
                break
            
            parents = population[:POPULATION_SIZE//2]
            children = []
            while len(children) < POPULATION_SIZE:
                p1, p2 = random.sample(parents, 2)
                point = random.randint(1, len(target)-1)
                child = p1[:point] + p2[point:]
                children.append(mutate(child))
            population = children

        end_time = time.perf_counter()
        duration = end_time - start_time

        self.root.after(0, self.update_results, best, generation, best_score, len(target), duration, in_dataset)

    def update_results(self, best, generation, best_score, target_len, duration, in_dataset):
        self.lbl_best.config(text=best, fg="#28A745")
        self.lbl_gen.config(text=str(generation))
        self.lbl_fitness.config(text=f"{best_score} / {target_len}")
        self.lbl_time.config(text=f"{duration:.3f} s")
        
        strength_text, score = password_strength(best)
        self.lbl_strength.config(text=f"{strength_text}", fg="#FD7E14")
        
        if in_dataset:
            self.lbl_dataset.config(text="Tìm thấy trong file dataset", fg="#6F42C1")
        else:
            self.lbl_dataset.config(text="Nằm ngoài file dataset", fg="#0052CC")
            
        self.btn.config(state=tk.NORMAL, bg="#0078D7", text="TÌM KIẾM")

if __name__ == "__main__":
    root = tk.Tk()
    app = GeneticApp(root)
    root.mainloop()