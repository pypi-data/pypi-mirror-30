from simpleflow import (
    activity,
    Workflow,
    futures,
)
from simpleflow.canvas import Group


@activity.with_attributes(task_list='quickstart', version='example',
                          raises_on_failure=False)
def fail_but_dont_raise():
    raise ValueError("This task had a problem but it's okay, YOU SHOULD NOT SEE THIS")


@activity.with_attributes(task_list='quickstart', version='example',
                          raises_on_failure=True)
def fail_and_raise():
    raise ValueError("This task had a problem and it will fail the workflow! (this is normal if you see this)")


class FailingWorkflow(Workflow):
    name = 'failing'
    version = 'example'
    task_list = 'example'
    retry = 1

    def run(self):
        x = self.submit(fail_but_dont_raise)
        y = self.submit(fail_and_raise)
        futures.wait(x, y)
        raise ValueError("YOU SHOULD NEVER SEE THIS")


class NotFailingWorkflow(Workflow):
    name = "basic"
    version = 'example'
    task_list = 'example'

    def run(self, *args, **kwargs):
        print("args:", args)
        print("kwargs:", kwargs)
        g = Group(raises_on_failure=False)
        g.append(FailingWorkflow)
        f = self.submit(g)
        futures.wait(f)

    def on_failure(self, history, reason, details=None):
        print("on_failure called, it shouldn't :'(")

    def on_completed(self, history):
        print('workflow completed!')
