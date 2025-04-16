#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// Task states
#define TASK_READY 0
#define TASK_RUNNING 1
#define TASK_WAITING 2
#define TASK_SUSPENDED 3

// Semaphore states
#define SEMAPHORE_FREE 0
#define SEMAPHORE_TAKEN 1

// Task Control Block (TCB)
typedef struct {
    int id;
    int priority;
    int period;
    int execution_time;
    int state;
    int remaining_time;
    int next_run;
    int deadline;
    int missed_deadlines;
    int needs_resource;
} Task;

// Semaphore structure
typedef struct {
    int state;
    int owner_id;
} Semaphore;

// Global variables
#define MAX_TASKS 5
Task tasks[MAX_TASKS];
Semaphore printer_semaphore = {SEMAPHORE_FREE, -1};
int current_time = 0;
int task_count = 0;

// Initialize tasks
void init_tasks() {
    srand(time(NULL));
    task_count = 0;

    tasks[task_count].id = task_count;
    tasks[task_count].priority = 4;
    tasks[task_count].period = 4;
    tasks[task_count].execution_time = 1;
    tasks[task_count].state = TASK_READY;
    tasks[task_count].remaining_time = 0;
    tasks[task_count].next_run = 0;
    tasks[task_count].deadline = tasks[task_count].period;
    tasks[task_count].missed_deadlines = 0;
    tasks[task_count].needs_resource = 1;
    task_count++;

    tasks[task_count].id = task_count;
    tasks[task_count].priority = 3;
    tasks[task_count].period = 6;
    tasks[task_count].execution_time = 2;
    tasks[task_count].state = TASK_READY;
    tasks[task_count].remaining_time = 0;
    tasks[task_count].next_run = 0;
    tasks[task_count].deadline = tasks[task_count].period;
    tasks[task_count].missed_deadlines = 0;
    tasks[task_count].needs_resource = 0;
    task_count++;

    tasks[task_count].id = task_count;
    tasks[task_count].priority = 2;
    tasks[task_count].period = 8;
    tasks[task_count].execution_time = 3;
    tasks[task_count].state = TASK_READY;
    tasks[task_count].remaining_time = 0;
    tasks[task_count].next_run = 0;
    tasks[task_count].deadline = tasks[task_count].period;
    tasks[task_count].missed_deadlines = 0;
    tasks[task_count].needs_resource = 1;
    task_count++;

    tasks[task_count].id = task_count;
    tasks[task_count].priority = 1;
    tasks[task_count].period = 10;
    tasks[task_count].execution_time = 2;
    tasks[task_count].state = TASK_READY;
    tasks[task_count].remaining_time = 0;
    tasks[task_count].next_run = 0;
    tasks[task_count].deadline = tasks[task_count].period;
    tasks[task_count].missed_deadlines = 0;
    tasks[task_count].needs_resource = 0;
    task_count++;

    tasks[task_count].id = task_count;
    tasks[task_count].priority = 1;
    tasks[task_count].period = 12;
    tasks[task_count].execution_time = 4;
    tasks[task_count].state = TASK_READY;
    tasks[task_count].remaining_time = 0;
    tasks[task_count].next_run = 0;
    tasks[task_count].deadline = tasks[task_count].period;
    tasks[task_count].missed_deadlines = 0;
    tasks[task_count].needs_resource = 1;
    task_count++;
}

// Attempt to take semaphore
int take_semaphore(int task_id) {
    if (printer_semaphore.state == SEMAPHORE_FREE) {
        printer_semaphore.state = SEMAPHORE_TAKEN;
        printer_semaphore.owner_id = task_id;
        return 1;
    }
    return 0;
}

// Release semaphore
void release_semaphore() {
    printer_semaphore.state = SEMAPHORE_FREE;
    printer_semaphore.owner_id = -1;
}

// Find the highest-priority ready task
int find_highest_priority_task() {
    int highest_priority = -1;
    int selected_task = -1;

    for (int i = 0; i < task_count; i++) {
        if (tasks[i].state == TASK_READY && tasks[i].next_run <= current_time) {
            if (tasks[i].needs_resource && printer_semaphore.state == SEMAPHORE_TAKEN) {
                tasks[i].state = TASK_SUSPENDED;
                continue;
            }
            if (tasks[i].priority > highest_priority) {
                highest_priority = tasks[i].priority;
                selected_task = i;
            }
        }
    }
    return selected_task;
}

// Clear console (cross-platform approximation)
void clear_console() {
    printf("\033[H\033[J"); // ANSI escape code for clear screen
}

// Draw ASCII GUI
void draw_gui() {
    clear_console();
    printf("RTOS Scheduler Simulator - Tick %d\n", current_time);
    printf("==================================\n");

    // Draw task states
    printf("Tasks:\n");
    for (int i = 0; i < task_count; i++) {
        printf("Task %d (P%d): ", tasks[i].id, tasks[i].priority);
        switch (tasks[i].state) {
            case TASK_READY:    printf("[=====] Ready    "); break;
            case TASK_RUNNING:  printf("[*****] Running  "); break;
            case TASK_WAITING:  printf("[     ] Waiting  "); break;
            case TASK_SUSPENDED:printf("[~~~~~] Suspended"); break;
        }
        printf(" | Misses: %d | Resource: %s\n",
               tasks[i].missed_deadlines, tasks[i].needs_resource ? "Yes" : "No");
    }

    // Draw semaphore status
    printf("\nSemaphore: %s\n",
           printer_semaphore.state == SEMAPHORE_FREE ? "[ ] Free" : "[X] Taken");

    // Draw timeline
    printf("\nTimeline:\n");
    for (int i = 0; i < task_count; i++) {
        printf("T%d: ", tasks[i].id);
        for (int t = 0; t <= current_time && t < 20; t++) {
            if (t == current_time && tasks[i].state == TASK_RUNNING) {
                printf("*");
            } else if (t < tasks[i].next_run && tasks[i].state != TASK_SUSPENDED) {
                printf("-");
            } else {
                printf(" ");
            }
        }
        printf("\n");
    }
    printf("\n");
}

// Simulate task execution
void execute_task(int task_idx) {
    if (task_idx == -1) {
        draw_gui();
        return;
    }

    Task *task = &tasks[task_idx];
    task->state = TASK_RUNNING;

    if (task->needs_resource && !take_semaphore(task->id)) {
        task->state = TASK_SUSPENDED;
        draw_gui();
        return;
    }

    if (task->remaining_time == 0) {
        task->remaining_time = task->execution_time;
    }

    task->remaining_time--;
    if (task->remaining_time == 0) {
        if (task->needs_resource) {
            release_semaphore();
        }
        task->state = TASK_WAITING;
        task->next_run = current_time + task->period;
        task->deadline = task->next_run;
    }
    draw_gui();
}

// Update task states and check deadlines
void update_tasks() {
    for (int i = 0; i < task_count; i++) {
        if (tasks[i].state == TASK_RUNNING) {
            tasks[i].remaining_time--;
            if (tasks[i].remaining_time == 0) {
                if (tasks[i].needs_resource) {
                    release_semaphore();
                }
                tasks[i].state = TASK_WAITING;
                tasks[i].next_run = current_time + tasks[i].period;
                tasks[i].deadline = tasks[i].next_run;
            }
        }
        if (tasks[i].state != TASK_SUSPENDED && tasks[i].deadline <= current_time && tasks[i].state != TASK_RUNNING) {
            tasks[i].missed_deadlines++;
            tasks[i].deadline += tasks[i].period;
        }
        if (tasks[i].next_run <= current_time && tasks[i].state == TASK_WAITING) {
            tasks[i].state = TASK_READY;
        }
        if (tasks[i].state == TASK_SUSPENDED && (!tasks[i].needs_resource || printer_semaphore.state == SEMAPHORE_FREE)) {
            tasks[i].state = TASK_READY;
        }
    }
}

// Main scheduler loop
void scheduler() {
    for (current_time = 0; current_time < 20; current_time++) {
        update_tasks();
        int next_task = find_highest_priority_task();
        execute_task(next_task);
        // Pause for visibility (1 second per tick)
        #ifdef _WIN32
            system("timeout /t 1 >nul");
        #else
            system("sleep 1");
        #endif
    }

    clear_console();
    printf("Simulation Complete. Deadline Miss Summary:\n");
    for (int i = 0; i < task_count; i++) {
        printf("Task %d: %d missed deadlines\n", tasks[i].id, tasks[i].missed_deadlines);
    }
}

int main() {
    init_tasks();
    scheduler();
    return 0;
}