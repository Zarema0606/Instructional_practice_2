import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class RepairRequestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учёт заявок на ремонт климатического оборудования")
        self.root.geometry("900x600")
        
        # ИНИЦИАЛИЗИРУЕМ атрибуты ДО вызова методов
        self.requests = []
        self.tree = None  # Важно: создаем атрибут сразу
        
        self.load_data()
        self.create_menu()
        self.create_widgets()
        self.refresh_table()  # Загружаем данные в таблицу
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Экспорт отчёта", command=self.export_report)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        stats_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Статистика", menu=stats_menu)
        stats_menu.add_command(label="Среднее время ремонта", command=self.show_avg_time)
        stats_menu.add_command(label="Статистика по неисправностям", command=self.show_defect_stats)
        
    def create_widgets(self):
        # Панель управления
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.grid(row=0, column=0, sticky="ew")
        
        ttk.Button(control_frame, text="Добавить заявку", command=self.open_add_request_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Удалить выбранное", command=self.delete_request).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить", command=self.load_data).pack(side=tk.LEFT, padx=5)
        
        # Таблица заявок
        columns = ("id", "client", "equipment", "defect", "date_in", "date_out", "status")
        
        # СОЗДАЕМ таблицу и сохраняем в self.tree
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=20)
        
        headings = [
            ("id", "ID"),
            ("client", "Клиент"),
            ("equipment", "Оборудование"),
            ("defect", "Неисправность"),
            ("date_in", "Дата приёма"),
            ("date_out", "Дата завершения"),
            ("status", "Статус")
        ]
        
        for col_id, col_text in headings:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=120)
        
        self.tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(self.root, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
    def open_add_request_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Добавить заявку")
        add_window.geometry("400x400")
        
        fields = [
            ("Клиент:", "entry"),
            ("Оборудование:", "entry"),
            ("Неисправность:", "combobox", ["Утечка фреона", "Неисправность компрессора", "Проблемы с электроникой", "Загрязнение фильтров"]),
            ("Дата приёма:", "entry", datetime.now().strftime("%Y-%m-%d")),
            ("Статус:", "combobox", ["Новая", "В работе", "Ожидает запчасти", "Завершена"])
        ]
        
        entries = {}
        for i, (label, field_type, *options) in enumerate(fields):
            ttk.Label(add_window, text=label).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            
            if field_type == "entry":
                entry = ttk.Entry(add_window, width=30)
                if options:
                    entry.insert(0, options[0])
                entry.grid(row=i, column=1, padx=10, pady=5)
                entries[label] = entry
            elif field_type == "combobox":
                combo = ttk.Combobox(add_window, values=options[0], width=27, state="readonly")
                combo.current(0)
                combo.grid(row=i, column=1, padx=10, pady=5)
                entries[label] = combo
        
        def save_request():
            try:
                request = {
                    "id": len(self.requests) + 1,
                    "client": entries["Клиент:"].get(),
                    "equipment": entries["Оборудование:"].get(),
                    "defect": entries["Неисправность:"].get(),
                    "date_in": entries["Дата приёма:"].get(),
                    "date_out": "",
                    "status": entries["Статус:"].get()
                }
                
                # Проверка обязательных полей
                if not request["client"] or not request["equipment"]:
                    raise ValueError("Заполните поля 'Клиент' и 'Оборудование'")
                
                # Проверка даты
                try:
                    datetime.strptime(request["date_in"], "%Y-%m-%d")
                except ValueError:
                    raise ValueError("Некорректный формат даты. Используйте ГГГГ-ММ-ДД")
                
                self.requests.append(request)
                self.save_data()
                self.refresh_table()
                add_window.destroy()
                messagebox.showinfo("Успех", "Заявка добавлена")
                
            except ValueError as e:
                messagebox.showerror("Ошибка ввода", str(e))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {str(e)}")
        
        ttk.Button(add_window, text="Сохранить", command=save_request).grid(row=len(fields), column=0, columnspan=2, pady=20)
        ttk.Button(add_window, text="Отмена", command=add_window.destroy).grid(row=len(fields)+1, column=0, columnspan=2, pady=5)
    
    def refresh_table(self):
        """Обновление данных в таблице"""
        # Проверяем, создана ли таблица
        if self.tree is None:
            return
            
        # Очищаем таблицу
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Заполняем данными
        for req in self.requests:
            self.tree.insert("", tk.END, values=(
                req["id"],
                req["client"],
                req["equipment"],
                req["defect"],
                req["date_in"],
                req["date_out"] if req["date_out"] else "—",
                req["status"]
            ))
    
    def delete_request(self):
        """Удаление выбранной заявки"""
        # Проверяем, создана ли таблица
        if self.tree is None:
            messagebox.showerror("Ошибка", "Таблица не инициализирована")
            return
            
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заявку для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранную заявку?"):
            try:
                item = self.tree.item(selected[0])
                req_id = item["values"][0]
                self.requests = [r for r in self.requests if r["id"] != req_id]
                self.save_data()
                self.refresh_table()
                messagebox.showinfo("Успех", "Заявка удалена")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить заявку: {e}")
    
    def show_avg_time(self):
        """Расчёт среднего времени ремонта"""
        completed = [r for r in self.requests if r["status"] == "Завершена" and r.get("date_out")]
        
        if not completed:
            messagebox.showinfo("Информация", "Нет завершённых заявок")
            return
        
        total_days = 0
        count = 0
        for req in completed:
            try:
                date_in = datetime.strptime(req["date_in"], "%Y-%m-%d")
                date_out = datetime.strptime(req["date_out"], "%Y-%m-%d")
                total_days += (date_out - date_in).days
                count += 1
            except (ValueError, KeyError):
                continue  # Пропускаем заявки с некорректными датами
        
        if count == 0:
            messagebox.showinfo("Информация", "Нет заявок с корректными датами")
            return
            
        avg_days = total_days / count
        messagebox.showinfo("Среднее время ремонта", 
                          f"Среднее время ремонта: {avg_days:.1f} дней\n"
                          f"Всего завершённых заявок: {len(completed)}\n"
                          f"Заявок с корректными датами: {count}")
    
    def show_defect_stats(self):
        """Статистика по типам неисправностей"""
        if not self.requests:
            messagebox.showinfo("Статистика", "Нет данных для анализа")
            return
            
        defects = {}
        for req in self.requests:
            defect = req.get("defect", "Не указана")
            defects[defect] = defects.get(defect, 0) + 1
        
        stats_text = "Статистика по неисправностям:\n\n"
        for defect, count in defects.items():
            stats_text += f"{defect}: {count} заявок\n"
        
        messagebox.showinfo("Статистика", stats_text)
    
    def export_report(self):
        """Экспорт отчёта в JSON"""
        if not self.requests:
            messagebox.showwarning("Экспорт", "Нет данных для экспорта")
            return
            
        try:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.requests, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Экспорт", f"Отчёт сохранён в файл:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка экспорта", f"Не удалось сохранить отчёт: {e}")
    
    def save_data(self):
        """Сохранение данных в файл"""
        try:
            with open("requests.json", "w", encoding="utf-8") as f:
                json.dump(self.requests, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        """Загрузка данных из файла"""
        try:
            if os.path.exists("requests.json"):
                with open("requests.json", "r", encoding="utf-8") as f:
                    self.requests = json.load(f)
                if self.tree:  # Проверяем, создана ли таблица
                    self.refresh_table()
            else:
                self.requests = []
                # Создаем тестовые данные для демонстрации
                self.requests = [
                    {
                        "id": 1,
                        "client": "Иванов И.И.",
                        "equipment": "Кондиционер Samsung",
                        "defect": "Утечка фреона",
                        "date_in": "2024-03-01",
                        "date_out": "2024-03-05",
                        "status": "Завершена"
                    },
                    {
                        "id": 2,
                        "client": "Петрова М.С.",
                        "equipment": "Сплит-система LG",
                        "defect": "Неисправность компрессора",
                        "date_in": "2024-03-10",
                        "date_out": "",
                        "status": "В работе"
                    }
                ]
                self.save_data()
                if self.tree:
                    self.refresh_table()
                    
        except json.JSONDecodeError:
            messagebox.showerror("Ошибка", "Файл данных поврежден")
            self.requests = []
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные: {e}")
            self.requests = []

if __name__ == "__main__":
    root = tk.Tk()
    app = RepairRequestApp(root)
    root.mainloop()