'''
Created on 2021-02-07

@author: wf
'''
import unittest
from fb4.sse_bp import Message


class TestMessages(unittest.TestCase):
    '''
    test SSE messages 
    
    converted to unittest from see https://github.com/singingwolfboy/flask-sse/blob/main/tests/test_message.py

    '''


    def setUp(self):
        pass


    def tearDown(self):
        pass
    
    def test_empty_message(self):
        m=None
        try:
            m=Message()
            self.fail("There should be an exception")
        except Exception as ex:
            msg=str(ex)
            self.assertTrue("missing 1 required positional argument: 'data'" in msg)
        self.assertTrue(m is None)
    
    def test_simple_data(self):
        m = Message("foo")
        assert m.data == "foo"
        assert m.type == None
        assert m.id == None
        assert m.retry == None
    
        assert m.to_dict() == {"data": "foo"}
        assert repr(m) == "Message('foo')"
        assert str(m) == 'data:foo\n\n'
    
    def test_data_dict(self):
        m = Message({"message": "Hello!"})
        assert m.data == {"message": "Hello!"}
        assert m.type == None
        assert m.id == None
        assert m.retry == None
    
        assert m.to_dict() == {"data": {"message": "Hello!"}}
        assert repr(m) == "Message({'message': 'Hello!'})"
        assert str(m) == 'data:{"message": "Hello!"}\n\n'
    
    def test_multiline_data(self):
        m = Message("foo\nbar")
        assert m.data == "foo\nbar"
        assert m.type == None
        assert m.id == None
        assert m.retry == None
    
        assert m.to_dict() == {"data": "foo\nbar"}
        assert repr(m) == "Message('foo\\nbar')"
        assert str(m) == 'data:foo\ndata:bar\n\n'

    def test_all_args(self):
        m = Message("foo", type="example", id=5, retry=500)
        assert m.data == "foo"
        assert m.type == "example"
        assert m.id == 5
        assert m.retry == 500
    
        assert m.to_dict() == {
            "data": "foo",
            "type": "example",
            "id": 5,
            "retry": 500,
        }
        assert repr(m) == "Message('foo', type='example', id=5, retry=500)"
        assert str(m) == 'event:example\ndata:foo\nid:5\nretry:500\n\n'

    def test_equality(self):
        m1 = Message("abc")
        m2 = Message("abc")
        assert m1 == m2
        m3 = Message("abc", type="example")
        assert m1 != m3
        m4 = Message("def")
        assert m1 != m4


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()