from __future__ import absolute_import
from __future__ import unicode_literals

import mock
from testify import assert_equal
from testify import run
from testify import setup
from testify import setup_teardown
from testify import TestCase

from tron import actioncommand
from tron import eventloop
from tron import node
from tron.actioncommand import ActionCommand
from tron.core import serviceinstance


class BuildActionTestCase(TestCase):

    @setup
    def setup_task(self):
        self.command = 'command'
        self.id = 'the_id'
        self.name = 'the_name'
        self.serializer = mock.create_autospec(actioncommand.StringBufferStore)
        self.task = mock.Mock(
            command=self.command,
            id=self.id, task_name=self.name, buffer_store=self.serializer,
        )

    @setup_teardown
    def setup_mock(self):
        patcher = mock.patch(
            'tron.core.serviceinstance.ActionCommand', autospec=True,
        )
        with patcher as self.mock_action_command:
            yield

    def test_build_action(self):
        action = serviceinstance.build_action(self.task)
        self.mock_action_command.assert_called_with(
            '%s.%s' % (self.id, self.name), self.command, serializer=self.serializer,
        )
        assert_equal(action, self.mock_action_command.return_value)
        self.task.watch.assert_called_with(action)


class RunActionTestCase(TestCase):

    @setup
    def setup_task(self):
        self.node = mock.create_autospec(node.Node)
        self.failed = 'NOTIFY_FAILED'
        self.task = mock.Mock(
            node=self.node, NOTIFY_FAILED=self.failed,
            task_name='mock_task',
        )
        self.action = mock.create_autospec(actioncommand.ActionCommand)

    def test_run_action(self):
        assert serviceinstance.run_action(self.task, self.action)
        self.node.submit_command.assert_called_with(self.action)

    def test_run_action_failed(self):
        error = self.task.node.submit_command.side_effect = node.Error("Oops")
        assert not serviceinstance.run_action(self.task, self.action)
        self.task.notify.assert_called_with(self.failed)
        self.task.buffer_store.open.return_value.write.assert_called_with(
            "Node run failure for mock_task: %s" % str(error),
        )


class ServiceInstanceMonitorTaskTestCase(TestCase):

    @setup_teardown
    def setup_task(self):
        self.interval = 20
        self.filename = "/tmp/filename"
        mock_node = mock.create_autospec(node.Node)
        self.task = serviceinstance.ServiceInstanceMonitorTask(
            "id", mock_node, self.interval, self.filename,
        )
        self.task.notify = mock.create_autospec(self.task.notify)
        self.task.watch = mock.create_autospec(self.task.watch)
        self.task.hang_check_callback = mock.create_autospec(
            eventloop.UniqueCallback,
        )
        self.task.callback = mock.create_autospec(eventloop.UniqueCallback)
        self.mock_eventloop = None
        with mock.patch('tron.core.serviceinstance.eventloop') as self.mock_eventloop:
            yield

    def test_queue(self):
        self.task.queue()
        self.task.callback.start.assert_called_with()

    def test_queue_no_interval(self):
        self.task.interval = 0
        self.task.queue()
        assert_equal(self.mock_eventloop.call_later.call_count, 0)

    def test_run(self):
        self.task.run()

        self.task.notify.assert_called_with(self.task.NOTIFY_START)
        self.task.node.submit_command.assert_called_with(self.task.action)
        self.task.hang_check_callback.start.assert_called_with()
        assert_equal(self.task.action.command, self.task.command)

    def test_run_failed(self):
        with mock.patch('tron.core.serviceinstance.run_action') as mock_run:
            mock_run.return_value = False
            self.task.run()
            assert_equal(self.mock_eventloop.call_later.call_count, 0)

    def test_run_action_exists(self):
        self.task.action = mock.create_autospec(ActionCommand, is_done=False)
        with mock.patch('tron.core.serviceinstance.log', autospec=True) as mock_log:
            self.task.run()
            assert_equal(mock_log.warn.call_count, 1)

    def test_handle_action_event_failstart(self):
        self.task.queue = mock.create_autospec(self.task.queue)
        self.task.handle_action_event(
            self.task.action, ActionCommand.FAILSTART,
        )
        self.task.notify.assert_called_with(self.task.NOTIFY_FAILED)
        self.task.queue.assert_called_with()
        self.task.hang_check_callback.cancel.assert_called_with()

    def test_handle_action_event_exit(self):
        self.task._handle_action_exit = mock.create_autospec(
            self.task._handle_action_exit,
        )
        self.task.handle_action_event(self.task.action, ActionCommand.EXITING)
        self.task._handle_action_exit.assert_called_with()
        self.task.hang_check_callback.cancel.assert_called_with()

    def test_handle_action_running(self):
        self.task.queue = mock.create_autospec(self.task.queue)
        self.task.handle_action_event(self.task.action, ActionCommand.RUNNING)
        assert not self.task.hang_check_callback.cancel.mock_calls
        assert not self.task.queue.mock_calls

    def test_handle_action_mismatching_action(self):
        action = mock.create_autospec(actioncommand.ActionCommand)
        self.task._handle_action_exit = mock.create_autospec(
            self.task._handle_action_exit,
        )
        self.task.handle_action_event(action, ActionCommand.EXITING)
        assert not self.task._handle_action_exit.mock_calls

    def test_handle_action_exit_up(self):
        self.task.action = mock.create_autospec(ActionCommand)
        self.task.action.is_failed = False
        self.task.action.is_unknown = False
        self.task.queue = mock.create_autospec(self.task.queue)
        self.task._handle_action_exit()
        self.task.notify.assert_called_with(self.task.NOTIFY_UP)
        self.task.queue.assert_called_with()

    def test_handle_action_exit_down(self):
        self.task.action = mock.create_autospec(ActionCommand)
        self.task.action.is_unknown = False
        self.task.queue = mock.create_autospec(self.task.queue)
        self.task._handle_action_exit()
        self.task.notify.assert_called_with(self.task.NOTIFY_DOWN)
        assert_equal(self.task.queue.call_count, 0)

    def test_handle_action_unknown(self):
        self.task.action = mock.create_autospec(ActionCommand)
        self.task.action.is_unknown = True
        self.task.queue = mock.create_autospec(self.task.queue)
        self.task._handle_action_exit()
        self.task.notify.assert_called_with(self.task.NOTIFY_FAILED)
        assert_equal(self.task.queue.call_count, 1)

    def test_fail(self):
        self.task.action = mock.create_autospec(actioncommand.ActionCommand)
        original_action = self.task.action
        self.task.fail()
        self.task.notify.assert_called_with(self.task.NOTIFY_FAILED)
        self.task.node.stop.assert_called_with(original_action)
        assert_equal(self.task.action, actioncommand.CompletedActionCommand)
        assert_equal(original_action.write_stderr.call_count, 1)


class ServiceInstanceStopTaskTestCase(TestCase):

    @setup
    def setup_task(self):
        self.node = mock.create_autospec(node.Node)
        self.pid_filename = '/tmp/filename'
        self.task = serviceinstance.ServiceInstanceStopTask(
            'id', self.node, self.pid_filename,
        )
        self.task.notify = mock.create_autospec(self.task.notify)

    def test_kill_task(self):
        assert self.task.stop()

    def test_handle_action_event_complete(self):
        action = mock.create_autospec(ActionCommand)
        event = ActionCommand.COMPLETE
        self.task.handle_action_event(action, event)
        self.task.notify.assert_called_with(self.task.NOTIFY_SUCCESS)

    def test_handle_action_event_failstart(self):
        action = mock.create_autospec(ActionCommand)
        event = ActionCommand.FAILSTART
        self.task.handle_action_event(action, event)
        self.task.notify.assert_called_with(self.task.NOTIFY_FAILED)

    def test_handle_complete_failed(self):
        action = mock.create_autospec(ActionCommand, is_failed=True)
        with mock.patch('tron.core.serviceinstance.log', autospec=True) as mock_log:
            self.task._handle_complete(action)
            assert_equal(mock_log.error.call_count, 1)

        self.task.notify.assert_called_with(self.task.NOTIFY_SUCCESS)

    def test_handle_complete(self):
        action = mock.create_autospec(ActionCommand, is_failed=False)
        self.task._handle_complete(action)
        self.task.notify.assert_called_with(self.task.NOTIFY_SUCCESS)


class ServiceInstanceStartTaskTestCase(TestCase):

    @setup
    def setup_task(self):
        self.node = mock.create_autospec(node.Node)
        self.task = serviceinstance.ServiceInstanceStartTask('id', self.node)
        self.task.watch = mock.create_autospec(self.task.watch)

    def test_start(self):
        command = 'the command'
        patcher = mock.patch(
            'tron.core.serviceinstance.ActionCommand', autospec=True,
        )
        with patcher as mock_ac:
            self.task.start(command)
            self.task.watch.assert_called_with(mock_ac.return_value)
            self.node.submit_command.assert_called_with(mock_ac.return_value)
            mock_ac.assert_called_with(
                "%s.start" % self.task.id, command,
                serializer=self.task.buffer_store,
            )

    def test_start_failed(self):
        command = 'the command'
        self.node.submit_command.side_effect = node.Error
        self.task.notify = mock.create_autospec(self.task.notify)
        self.task.start(command)
        self.task.notify.assert_called_with(self.task.NOTIFY_FAILED)

    def test_handle_action_event_exit(self):
        action = mock.create_autospec(ActionCommand)
        event = ActionCommand.EXITING
        self.task.handle_action_event(action, event)
        self.task.notify(self.task.NOTIFY_STARTED)

    def test_handle_action_event_failstart(self):
        action = mock.create_autospec(ActionCommand)
        event = ActionCommand.FAILSTART
        patcher = mock.patch('tron.core.serviceinstance.log', autospec=True)
        with patcher as mock_log:
            self.task.handle_action_event(action, event)
            assert_equal(mock_log.warn.call_count, 1)

    def test_handle_action_exit_fail(self):
        action = mock.create_autospec(ActionCommand, is_failed=True)
        self.task.notify = mock.create_autospec(self.task.notify)
        self.task._handle_action_exit(action)
        self.task.notify.assert_called_with(self.task.NOTIFY_FAILED)

    def test_handle_action_exit_success(self):
        action = mock.create_autospec(ActionCommand, is_failed=False)
        self.task.notify = mock.create_autospec(self.task.notify)
        self.task._handle_action_exit(action)
        self.task.notify.assert_called_with(self.task.NOTIFY_STARTED)


class NodeSelectorTestCase(TestCase):

    @setup
    def setup_mocks(self):
        self.node_pool = mock.create_autospec(node.NodePool)

    def test_node_selector_no_hostname(self):
        selected_node = serviceinstance.node_selector(self.node_pool)
        assert_equal(selected_node, self.node_pool.next_round_robin())

    def test_node_selector_hostname_not_in_pool(self):
        hostname = 'hostname'
        self.node_pool.get_by_hostname.return_value = None
        selected_node = serviceinstance.node_selector(self.node_pool, hostname)
        assert_equal(
            selected_node, self.node_pool.next_round_robin.return_value,
        )

    def test_node_selector_hostname_found(self):
        hostname = 'hostname'
        selected_node = serviceinstance.node_selector(self.node_pool, hostname)
        assert_equal(
            selected_node, self.node_pool.get_by_hostname.return_value,
        )


def create_mock_instance(**kwargs):
    return mock.create_autospec(serviceinstance.ServiceInstance, **kwargs)


if __name__ == "__main__":
    run()
