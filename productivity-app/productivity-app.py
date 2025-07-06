'''
RBI how to automate your trading

R - Research (Google Scholar with MCP)
B - Backtest to see if it they work in the past . 95% of strats fail...5% of strats work
I - Implement with small size to a bot

devote 2 hours per day to this algo trading protocol

30 mins for research
1.5 hours of backtest 1
1.5 hours of backtest 3
.5 hours reading a paper
.5 hours watching youtube strategies
.5 hours connecting with other traders


Prompt for learning how to code:
explain the concepts in this code with 3 analogie and 3 coding examples. 
Im learning how to code and I need to understand these concepts perfectly.

'''
import json
import time
from datetime import datetime, timedelta
from termcolor import cprint
import random


def load_tasks():
    with open('tasks.json', 'r') as f:
        tasks = json.load(f)
    return tasks

def get_task_schedule(tasks):
    task_start_time = datetime.now()
    schedule = []
    for task, minutes in tasks.items():
        end_time = task_start_time + timedelta(minutes=minutes)
        schedule.append((task, task_start_time, end_time))
        task_start_time = end_time
    return schedule

def blink_text(text, colors=['white', 'red']):
    current_time = time.time()
    # Blink every 0.5 seconds
    if int(current_time * 2) % 2:
        cprint(text, colors[0], 'on_red')
    else:
        cprint(text, colors[1], 'on_red')

def main():
    tasks = load_tasks()
    schedule = get_task_schedule(tasks)
    current_index = 0

    while True:
        now = datetime.now()
        current_task, start_time, end_time = schedule[current_index]
        remaining_time = end_time - now
        remaining_minutes = int(remaining_time.total_seconds() // 60)

        print('\n' * 2)

        for index, (task, s_time, e_time) in enumerate(schedule):
            if index < current_index:
                # task is completed
                print(f'{task} done: {e_time.strftime("%H:%M")}')
            elif index == current_index:
                # current task
                if remaining_minutes < 2:
                    blink_text(f'{task} < 2m left!')
                elif remaining_minutes < 5:
                    cprint(f'{task} - {remaining_minutes} mins', 'white', 'on_red')
                else:
                    cprint(f'{task} - {remaining_minutes} mins', 'white', 'on_blue')
            else:
                print(f'{task} @ {s_time.strftime("%H:%M")}')

        list_of_reminders = [
            "ich habe ein KI-System Business mit 10'000CHF pro Monatsumsatz",
            "ich wohne im Student Village",
            "ich habe ein Netzwerk aus 100 Quants in Zürich aufgebaut",
            "ich habe ein Praktikum im Derivaten-Bereich bei der UBS",
            "ich bin aktiver Tennis und Trompeten-Spieler"
        ]                    
        random_reminder = random.choice(list_of_reminders)
        print('\nReminder: ' + random_reminder)

        if now >= end_time:
            current_index += 1
            if current_index >= len(schedule):
                cprint("All tasks are completed!", 'white', 'on_green')
                break
      
        time.sleep(15)

if __name__ == '__main__':
    main()
            


