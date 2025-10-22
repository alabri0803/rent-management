"""
اختبار بسيط للتحقق من أن نظام الاختبارات يعمل
Basic test to verify testing system works
"""

def test_basic_addition():
    """اختبار بسيط للجمع"""
    assert 1 + 1 == 2

def test_basic_string():
    """اختبار بسيط للنصوص"""
    assert "hello" + " world" == "hello world"

def test_basic_list():
    """اختبار بسيط للقوائم"""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert 2 in test_list

if __name__ == "__main__":
    print("✅ جميع الاختبارات الأساسية نجحت!")
    print("✅ All basic tests passed!")
