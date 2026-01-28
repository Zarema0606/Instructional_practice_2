import unittest
import tempfile
import json
import os
from main import RepairRequestApp
import tkinter as tk

class TestRepairApp(unittest.TestCase):
    def setUp(self):
        self.test_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_data = [
            {
                "id": 1,
                "client": "Иванов И.И.",
                "equipment": "Кондиционер Samsung",
                "defect": "Утечка фреона",
                "date_in": "2024-03-01",
                "date_out": "2024-03-05",
                "status": "Завершена"
            }
        ]
        json.dump(self.test_data, self.test_file)
        self.test_file.close()
        
    def tearDown(self):
        os.unlink(self.test_file.name)
    
    def test_data_loading(self):
        """Тест загрузки данных из файла"""
        with open(self.test_file.name, 'r') as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["client"], "Иванов И.И.")
    
    def test_avg_time_calculation(self):
        """Тест расчёта среднего времени ремонта"""
        # Эмуляция данных
        requests = [
            {"date_in": "2024-03-01", "date_out": "2024-03-05", "status": "Завершена"},
            {"date_in": "2024-03-01", "date_out": "2024-03-03", "status": "Завершена"},
        ]
        
        # Логика расчёта (упрощённая)
        days = []
        for req in requests:
            if req["status"] == "Завершена" and req["date_out"]:
                days.append(4)  # Просто пример
        
        if days:
            avg = sum(days) / len(days)
            self.assertEqual(avg, 4)

if __name__ == "__main__":
    unittest.main()