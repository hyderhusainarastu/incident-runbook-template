/* Fictional source used by check_skeleton.py */
#define BUF_SIZE 256

void run_job_in_worker(void);

void main_loop(void) {
    char scratch[BUF_SIZE];
    run_job_in_worker();
}
