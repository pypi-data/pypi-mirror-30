from __future__ import print_function

from simpleflow import activity, Workflow, canvas, futures


@activity.with_attributes(task_list='example', version='example')
class Delay(object):
    def submit(self, s):
        print('Delay: %d', s)


@activity.with_attributes(task_list='example', version='example')
class Foo(object):
    def submit(self, s):
        print('Foo: %d', s)


@activity.with_attributes(task_list='example', version='example')
class Bar(object):
    def submit(self, s):
        print('Bar: %d', s)


class MyWorkflow(Workflow):
    """docstring for MyWorkflow"""

    name = 'basic'
    version = 'example'
    task_list = 'example'

    def run(self):
        print('MyWorkflow')
        c1 = canvas.Chain(
            canvas.ActivityTask(Delay),
            canvas.ActivityTask(Foo),
            canvas.ActivityTask(Bar),
        )

        c2 = canvas.Chain(
            canvas.ActivityTask(Delay),
            canvas.ActivityTask(Foo),
            canvas.ActivityTask(Bar),
        )

        g = canvas.Group(c1, c2)
        f = self.submit(g)
        futures.wait(f)
