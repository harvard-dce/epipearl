epipearl
===============================

python client for [epiphan-pearl][pearl] [http api][pearl-http-api]

this software shoud be considered alpha, therefore likely to change/break in the near future.


install
-------

    pip install epipearl



example usage
-------------

    from epipearl import Epipearl
    client = Epipearl( "http://epiphan_pearl_address", "admin", "secret_password" )
    
    # to get the type of stream being published and frame size for channel 1
    response = client.get_params( channel='1', params={'publish_type':'', 'framesize':''})
    print "publish_type is %s" % response['publish_type']
    print "framsize is %s" % response['framesize']
    
    # to start recording on recorder 2
    response = client.set_params( channel='m2', params={'rec_enabled': 'on'})
    if response:
        print "recorder 2 set to start recording"



credits
---------

Tools used in rendering this package:

* [Cookiecutter][cookiecutter]
* [cookiecutter-dce package template][dce-pypackage]



license
-------

epipearl is licensed under the Apache 2.0 license



copyright
---------

2015~2016 President and Fellows of Harvard College

[cookiecutter]: https://github.com/audreyr/cookiecutter
[dce-pypackage]: https://github.com/harvard-dce/cookiecutter-dce
[pearl]: http://www.epiphan.com/products/pearl/
[pearl-http-api]:
http://31t4ggyuf393hqweo1aq90k7.wpengine.netdna-cdn.com/wp-content/uploads/2014/09/Epiphan_Pearl_userguide.pdf
