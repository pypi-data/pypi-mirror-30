53iq cloud store python sdk
============================

ebcloudstore is a sdk for 53iq cloud

hello,world
------------

.. code-block:: python

    from ebcloudstore.client import EbStore
    store = EbStore("your token")
    r = store.upload("/your/file/path/hello.jpg")
    print(r)


use in tornado
--------------

.. code-block:: python

    def post(self):
        if len(self.request.files) > 0:
            file_metas = self.request.files["myfile"]
            for meta in file_metas:
                from ebcloudstore.client import EbStore
                store = EbStore("your token")
                r = store.upload(meta['body'], meta['filename'], meta["content_type"])
                self.write(r)

use in django
--------------

.. code-block:: python

    def test(request):
        if request.method == "POST":
            if len(request.FILES.dict()) >= 1:
                f = request.FILES["myfile"]
                from ebcloudstore.client import EbStore
                store = EbStore("your token")
                r = store.upload(f.read(), f.name, f.content_type)
                return HttpResponse(r)


callback after finished
-------------------------

.. code-block:: python

    from ebcloudstore.client import EbStore
    # will post the body data result to callback_url when upload finished (5 seconds timeout)
    store = EbStore("your token",action="callback",callback_url="http://your.domain.receive")
    r = store.upload("/your/file/path/hello.jpg")

set upload timeout
----------------------

.. code-block:: python

    from ebcloudstore.client import EbStore, EbStoreUploadTimeoutException
    store = EbStore("your token")
    try:
        # 20 seconds timeout
        r = store.upload("/your/file/path/hello.jpg", timeout=20)
        print(r)
    except EbStoreUploadTimeoutException:
        print("timeout!please retry")



redirect after finished
---------------------------

.. code-block:: python

    from ebcloudstore.client import EbStore
    # will redirect the referer url when upload finished
    store = EbStore("your token",action="redirect",referer="http://your.domain.receive")
    r = store.upload("/your/file/path/hello.jpg")

* tips: also can use javascript in web browser direct upload file to cloud server


Installation
--------------

**Automatic installation**::

    pip install ebcloudstore

* once you want to use this sdk,first of all you need a token, apply for by email to tsengdavid@126.com
* only python3.x supported
