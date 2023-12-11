#include <linux/init.h>
#include <linux/module.h>
#include <linux/sched.h>
#include <linux/signal.h>
#include <linux/kernel.h>
#include <linux/string.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Luke");
MODULE_DESCRIPTION("make processs unkillable and unstoppable. Based on code from Davidr.");
MODULE_VERSION("0.03");

// Need structs here becasue they are not in the headers.
struct sighand_struct {
	atomic_t		count;
	struct k_sigaction	action[64];
	spinlock_t		siglock;
	wait_queue_head_t	signalfd_wqh;
};
struct signal_struct {
	atomic_t		sigcnt;
	atomic_t		live;
	int			nr_threads;
	struct list_head	thread_head;

	wait_queue_head_t	wait_chldexit;	/* for wait4() */

	/* current thread group signal load-balancing target: */
	struct task_struct	*curr_target;

	/* shared signal handling: */
	struct sigpending	shared_pending;

	/* thread group exit support */
	int			group_exit_code;
	/* overloaded:
	 * - notify group_exit_task when ->count is equal to notify_count
	 * - everyone except group_exit_task is stopped during signal delivery
	 *   of fatal signals, group_exit_task processes the signal.
	 */
	int			notify_count;
	struct task_struct	*group_exit_task;

	/* thread group stop support, overloads group_exit_code too */
	int			group_stop_count;
	unsigned int		flags; /* see SIGNAL_* flags below */
};

#define next_task(p) \
	list_entry_rcu((p)->tasks.next, struct task_struct, tasks)

#define for_each_process(p) \
	for (p = current ; (p = next_task(p)) != current ; )

static void protect_process(struct task_struct * t) {
    // The original process must first create a handler for all of his signals,
    // then we will copy it to the kill signal action (and the stop signal)  
    t->sighand->action[8] = t->sighand->action[9];
    t->sighand->action[18] = t->sighand->action[9];
}

static struct task_struct * find_target_process_by_name(char * name) {
    struct task_struct * iter;
    for_each_process(iter) {
        if(strcmp(name, iter->comm) == 0)
			printk("werked?");
            return iter;
    }
    return NULL;
}

static int __init proc_prot_init(void) {
    struct task_struct *this;
    this = find_target_process_by_name("python3");
    if (NULL == this) {
        printk("Process not found.\n");
        return 0;
    }
    protect_process(this);

    return 0;
}
static void __exit proc_prot_exit(void) {
}
module_init(proc_prot_init);
module_exit(proc_prot_exit);
