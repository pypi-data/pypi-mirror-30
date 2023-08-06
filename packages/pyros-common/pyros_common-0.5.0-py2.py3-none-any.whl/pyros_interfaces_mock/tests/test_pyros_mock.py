from __future__ import absolute_import
from __future__ import print_function

import os
import sys

# This is needed if running this test directly (without using nose loader)
# prepending because ROS relies on package dirs list in PYTHONPATH and not isolated virtualenvs
# And we need our current module to be found first.
current_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
# if not current_path in sys.path:
sys.path.insert(1, current_path)  # sys.path[0] is always current path as per python spec

import time

from pyros_interfaces_mock.mocksystem import (
    mock_publisher_remote, mock_subscriber_remote, topics_available_remote, topics_available_type_remote,
)
from pyros_interfaces_mock import PyrosMock, statusecho_topic
import pyzmp
import pytest


### TESTING NODE CREATION / TERMINATION ###
@pytest.mark.timeout(5)
def test_mocknode_creation_termination():
    mockn = PyrosMock()
    assert not mockn.is_alive()
    mockn.start()
    try:
        assert mockn.is_alive()
    finally:
        mockn.shutdown()
        assert not mockn.is_alive()


@pytest.mark.timeout(5)
def test_mocknode_provide_services():  # Here we check that this node actually provides all the services
    mockn = PyrosMock()
    assert not mockn.is_alive()

    assert hasattr(mockn, 'msg_build')
    assert hasattr(mockn, 'topic')
    assert hasattr(mockn, 'topics')
    assert hasattr(mockn, 'service')
    assert hasattr(mockn, 'services')
    assert hasattr(mockn, 'param')
    assert hasattr(mockn, 'params')
    assert hasattr(mockn, 'setup')

    mockn.start()
    try:
        assert mockn.is_alive()

        print("Discovering msg_build Service...")
        msg_build = pyzmp.discover("msg_build", 5)  # we wait a bit to let it time to start
        assert msg_build is not None
        assert len(msg_build.providers) == 1

        print("Discovering topic Service...")
        topic = pyzmp.discover("topic", 5)  # we wait a bit to let it time to start
        assert topic is not None
        assert len(topic.providers) == 1

        print("Discovering topics Service...")
        topic_list = pyzmp.discover("topics", 5)  # we wait a bit to let it time to start
        assert topic_list is not None
        assert len(topic_list.providers) == 1

        print("Discovering service Service...")
        service = pyzmp.discover("service", 5)  # we wait a bit to let it time to start
        assert service is not None
        assert len(service.providers) == 1

        print("Discovering services Service...")
        service_list = pyzmp.discover("services", 5)  # we wait a bit to let it time to start
        assert service_list is not None
        assert len(service_list.providers) == 1

        print("Discovering param Service...")
        param = pyzmp.discover("param", 5)  # we wait a bit to let it time to start
        assert param is not None
        assert len(param.providers) == 1

        print("Discovering params Service...")
        param_list = pyzmp.discover("params", 5)  # we wait a bit to let it time to start
        assert param_list is not None
        assert len(param_list.providers) == 1

        print("Discovering setup Service...")
        param_list = pyzmp.discover("setup", 5)  # we wait a bit to let it time to start
        assert param_list is not None
        assert len(param_list.providers) == 1
    finally:
        mockn.shutdown()
        assert not mockn.is_alive()


def test_mocknode_publishers_detect():  # Here we check that this node actually detects a topic
    mockn = PyrosMock(kwargs={
        'services': [],
        'publishers': ['test_topic'],
        'subscribers': [],
        'params': []
    })
    assert not mockn.is_alive()

    assert hasattr(mockn, 'topics')

    # starting the node
    mockn.start()

    # checking interface is still None here ( instantiated in child only )
    assert mockn.interface is None

    # Services are initialized in run() method of pyzmp.Node, after interface has been initialized
    try:
        assert mockn.is_alive()

        with mock_publisher_remote('test_topic', statusecho_topic):

            # asserting the mock system has done its job from our point of view at least
            assert 'test_topic' in topics_available_remote
            assert topics_available_type_remote['test_topic'] == statusecho_topic

            # Getting topics list from child process
            print("Discovering topics Service...")
            topics = pyzmp.discover("topics", 3)  # we wait a bit to let it time to start
            assert topics is not None
            assert len(topics.providers) == 1

            time.sleep(mockn.update_interval + 1)  # make sure we let update time to kick in

            res = topics.call(recv_timeout=6000000)
            # the mock system should have done its job from the other process perspective too
            # via multiprocess manager list
            assert 'test_topic' in res  # topic detected since in list of exposed topics

    finally:
        mockn.shutdown()
        assert not mockn.is_alive()


def test_mocknode_publishers_configure_detect():  # Here we check that this node actually detects a topic
    mockn = PyrosMock()

    mockn.configure({
        'SERVICES': [],
        'PUBLISHERS': ['test_topic'],
        'SUBSCRIBERS': [],
        'PARAMS': []
    })

    assert not mockn.is_alive()

    assert hasattr(mockn, 'topics')

    # starting the node
    mockn.start()

    # checking interface is still None here ( instantiated in child only )
    assert mockn.interface is None

    # Services are initialized in run() method of pyzmp.Node, after interface has been initialized
    try:
        assert mockn.is_alive()

        with mock_publisher_remote('test_topic', statusecho_topic):

            # asserting the mock system has done its job from our point of view at least
            assert 'test_topic' in topics_available_remote
            assert topics_available_type_remote['test_topic'] == statusecho_topic

            # Getting topics list from child process
            print("Discovering topics Service...")
            topics = pyzmp.discover("topics", 3)  # we wait a bit to let it time to start
            assert topics is not None
            assert len(topics.providers) == 1

            time.sleep(mockn.update_interval + 1)  # make sure we let update time to kick in

            res = topics.call(recv_timeout=6000000)
            # the mock system should have done its job from the other process perspective too
            # via multiprocess manager list
            assert 'test_topic' in res  # topic detected since in list of exposed topics

    finally:
        mockn.shutdown()
        assert not mockn.is_alive()


def test_mocknode_publishers_detect_setup():  # Here we check that this node actually detects a topic upon setup
    mockn = PyrosMock()
    assert not mockn.is_alive()

    assert hasattr(mockn, 'topics')

    mockn.start()
    try:
        assert mockn.is_alive()

        with mock_publisher_remote('test_topic', statusecho_topic):

            print("Discovering topics Service...")
            topics = pyzmp.discover("topics", 3)  # we wait a bit to let it time to start
            assert topics is not None
            assert len(topics.providers) == 1

            res = topics.call()
            assert not 'test_topic' in res  # topic not detected since not in list of exposed topics

            print("Discovering setup Service...")
            setup = pyzmp.discover("setup", 3)  # we wait a bit to let it time to start
            assert setup is not None
            assert len(setup.providers) == 1

            setup.call(kwargs={'services': [], 'topics': ['test_topic'], 'params': []})

            time.sleep(mockn.update_interval + 1)  # waiting for update to kick in

            res = topics.call()
            assert 'test_topic' in res
    finally:
        mockn.shutdown()
        assert not mockn.is_alive()


def test_mocknode_publishers_detect_throttled():
    """
    Testing that the mocknode detection of topics is throttled properly
    :return:
    """
    mockn = PyrosMock()
    assert not mockn.is_alive()

    assert hasattr(mockn, 'topics')

    mockn.update_interval = 5  # we wait 5 seconds between each update_throttled call
    mockn.start()  # one update will be triggered, and then nothing for the next 10 seconds
    try:
        assert mockn.is_alive()

        print("Discovering setup Service...")
        setup = pyzmp.discover("setup", 3)  # we wait a bit to let it time to start
        assert setup is not None
        assert len(setup.providers) == 1

        setup.call(kwargs={'services': [], 'topics': ['test_topic'], 'params': []})

        with mock_publisher_remote('test_topic', statusecho_topic):

            print("Discovering topics Service...")
            topics = pyzmp.discover("topics", 3)  # we wait a bit to let it time to start
            assert topics is not None
            assert len(topics.providers) == 1

            # topic is very likely not detected yet ( we didn't wait after creating and exposing it )
            res = topics.call()
            assert not 'test_topic' in res

            time.sleep(mockn.update_interval + 1)  # make sure we let update time to kick in

            # topic has to be detected now
            res = topics.call()
            assert 'test_topic' in res

    finally:  # to make sure we clean up on failure
        mockn.shutdown()
        assert not mockn.is_alive()


def test_mocknode_subscribers_detect():  # Here we check that this node actually detects a topic
    mockn = PyrosMock(kwargs={
        'services': [],
        'publishers': [],
        'subscribers': ['test_topic'],
        'params': []
    })
    assert not mockn.is_alive()

    assert hasattr(mockn, 'topics')

    # starting the node
    mockn.start()

    # checking interface is still None here ( instantiated in child only )
    assert mockn.interface is None

    # Services are initialized in run() method of pyzmp.Node, after interface has been initialized
    try:
        assert mockn.is_alive()

        with mock_subscriber_remote('test_topic', statusecho_topic):

            # asserting the mock system has done its job from our point of view at least
            assert 'test_topic' in topics_available_remote
            assert topics_available_type_remote['test_topic'] == statusecho_topic

            # Getting topics list from child process
            print("Discovering topics Service...")
            topics = pyzmp.discover("topics", 3)  # we wait a bit to let it time to start
            assert topics is not None
            assert len(topics.providers) == 1

            time.sleep(mockn.update_interval + 1)  # make sure we let update time to kick in

            res = topics.call(recv_timeout=6000000)
            # the mock system should have done its job from the other process perspective too
            # via multiprocess manager list
            assert 'test_topic' in res  # topic detected since in list of exposed topics

    finally:
        mockn.shutdown()
        assert not mockn.is_alive()



def test_mocknode_subscribers_configure_detect():  # Here we check that this node actually detects a topic
    mockn = PyrosMock()

    mockn.configure({
        'SERVICES': [],
        'PUBLISHERS': [],
        'SUBSCRIBERS': ['test_topic'],
        'PARAMS': []
    })

    assert not mockn.is_alive()

    assert hasattr(mockn, 'topics')

    # starting the node
    mockn.start()

    # checking interface is still None here ( instantiated in child only )
    assert mockn.interface is None

    # Services are initialized in run() method of pyzmp.Node, after interface has been initialized
    try:
        assert mockn.is_alive()

        with mock_subscriber_remote('test_topic', statusecho_topic):

            # asserting the mock system has done its job from our point of view at least
            assert 'test_topic' in topics_available_remote
            assert topics_available_type_remote['test_topic'] == statusecho_topic

            # Getting topics list from child process
            print("Discovering topics Service...")
            topics = pyzmp.discover("topics", 3)  # we wait a bit to let it time to start
            assert topics is not None
            assert len(topics.providers) == 1

            time.sleep(mockn.update_interval + 1)  # make sure we let update time to kick in

            res = topics.call(recv_timeout=6000000)
            # the mock system should have done its job from the other process perspective too
            # via multiprocess manager list
            assert 'test_topic' in res  # topic detected since in list of exposed topics

    finally:
        mockn.shutdown()
        assert not mockn.is_alive()


def test_mocknode_subscribers_detect_setup():  # Here we check that this node actually detects a topic upon setup
    mockn = PyrosMock()
    assert not mockn.is_alive()

    assert hasattr(mockn, 'topics')

    mockn.start()
    try:
        assert mockn.is_alive()

        with mock_subscriber_remote('test_topic', statusecho_topic):

            print("Discovering topics Service...")
            topics = pyzmp.discover("topics", 3)  # we wait a bit to let it time to start
            assert topics is not None
            assert len(topics.providers) == 1

            res = topics.call()
            assert not 'test_topic' in res  # topic not detected since not in list of exposed topics

            print("Discovering setup Service...")
            setup = pyzmp.discover("setup", 3)  # we wait a bit to let it time to start
            assert setup is not None
            assert len(setup.providers) == 1

            setup.call(kwargs={'services': [], 'topics': ['test_topic'], 'params': []})

            time.sleep(mockn.update_interval + 1)  # waiting for update to kick in

            res = topics.call()
            assert 'test_topic' in res
    finally:
        mockn.shutdown()
        assert not mockn.is_alive()


def test_mocknode_subscribers_detect_throttled():
    """
    Testing that the mocknode detection of topics is throttled properly
    :return:
    """
    mockn = PyrosMock()
    assert not mockn.is_alive()

    assert hasattr(mockn, 'topics')

    mockn.update_interval = 5  # we wait 5 seconds between each update_throttled call
    mockn.start()  # one update will be triggered, and then nothing for the next 10 seconds
    try:
        assert mockn.is_alive()

        print("Discovering setup Service...")
        setup = pyzmp.discover("setup", 3)  # we wait a bit to let it time to start
        assert setup is not None
        assert len(setup.providers) == 1

        setup.call(kwargs={'services': [], 'topics': ['test_topic'], 'params': []})

        with mock_subscriber_remote('test_topic', statusecho_topic):

            print("Discovering topics Service...")
            topics = pyzmp.discover("topics", 3)  # we wait a bit to let it time to start
            assert topics is not None
            assert len(topics.providers) == 1

            # topic is very likely not detected yet ( we didn't wait after creating and exposing it )
            res = topics.call()
            assert not 'test_topic' in res

            time.sleep(mockn.update_interval + 1)  # make sure we let update time to kick in

            # topic has to be detected now
            res = topics.call()
            assert 'test_topic' in res

    finally:  # to make sure we clean up on failure
        mockn.shutdown()
        assert not mockn.is_alive()


def test_msg_build():
    msg = PyrosMock().msg_build('fake_connec_name')
    print("msg is of type {0}".format(type(msg)))
    assert isinstance(msg, str)


def test_echo_topic_default():
    mock = PyrosMock()
    recv_msg = mock.topic('random_topic')
    assert recv_msg is None


def test_echo_same_topic():
    msg = 'testing'
    mock = PyrosMock()
    mock.topic('random_topic', msg)
    print("msg sent is {0}".format(msg))
    recv_msg = mock.topic('random_topic')
    print("msg received is {0}".format(recv_msg))
    assert msg == recv_msg


def test_other_topic():
    msg = 'testing'
    mock = PyrosMock()
    mock.topic('random_topic', msg)
    print("msg sent is {0}".format(msg))
    recv_msg = mock.topic('random_topic_2')
    print("msg received is {0}".format(recv_msg))
    assert recv_msg is None


def test_echo_service_default():
    msg = 'testing'
    mock = PyrosMock()
    assert mock.service('random_service') is None


def test_echo_service():
    msg = 'testing'
    mock = PyrosMock()
    print("msg sent is {0}".format(msg))
    recv_msg = mock.service('random_service', msg)
    print("msg received is {0}".format(recv_msg))
    assert msg == recv_msg


class TestPyrosMockProcess(object):

    mockInstance = None

    @classmethod
    def setup_class(cls):
        cls.mockInstance = PyrosMock()
        assert cls.mockInstance.start()

    @classmethod
    def teardown_class(cls):
        cls.mockInstance.shutdown()

    def test_msg_build(self):
        msg_build_svc = pyzmp.Service.discover('msg_build', 5)
        assert(msg_build_svc is not None)
        assert(self.mockInstance not in msg_build_svc.providers)
        resp = msg_build_svc.call(args=('fake_connec_name',))
        assert isinstance(resp, str)

    def test_list_topic(self):
        list_topic_svc = pyzmp.Service.discover('topics', 5)
        assert(list_topic_svc is not None)
        assert(self.mockInstance not in list_topic_svc.providers)
        resp = list_topic_svc.call()
        assert resp is not None

    def test_echo_topic(self):
        topic_svc = pyzmp.Service.discover('topic', 5)
        assert(topic_svc is not None)
        assert(self.mockInstance not in topic_svc.providers)
        resp = topic_svc.call(args=('random_topic', 'testing'))
        assert resp is None  # message consumed

        resp = topic_svc.call(args=('random_topic', None))
        assert resp == 'testing'  # message echoed

    def test_other_topic(self):
        topic_svc = pyzmp.Service.discover('topic', 5)
        assert(topic_svc is not None)
        assert(self.mockInstance not in topic_svc.providers)
        resp = topic_svc.call(args=('random_topic', 'testing'))
        assert resp is None  # message consumed

        resp = topic_svc.call(args=('random_topic_2', None))
        assert resp is None  # message not echoed

    def test_list_service(self):
        service_svc = pyzmp.Service.discover('services', 5)
        assert(service_svc is not None)
        assert(self.mockInstance not in service_svc.providers)
        resp = service_svc.call()
        assert resp is not None  # message echoed

    def test_echo_service(self):
        service_svc = pyzmp.Service.discover('service', 5)
        assert(service_svc is not None)
        assert(self.mockInstance not in service_svc.providers)
        resp = service_svc.call(args=('random_service', 'testing'))
        assert resp == 'testing'  # message echoed

    #TODO Check that if a service is called inappropriately, the exception is properly transferred back to the calling process and reraised.


# Just in case we run this directly
if __name__ == '__main__':
    import pytest
    pytest.main([
        '-s', __file__,
])
